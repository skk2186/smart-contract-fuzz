import csv
import re
import sys
from datetime import datetime
from pathlib import Path


TIMESTAMP_PATTERN = (
    r"\[(\d{4}-\d{2}-\d{2} "
    r"\d{2}:\d{2}:\d{2}\.\d+)\]"
)

PROPERTY_PATTERN = r"echidna_[A-Za-z0-9_]+"
BUDGET_EXHAUSTED_PATTERN = r"Test limit reached\. Stopping\."

STARTUP_ERROR_PATTERNS = [
    r"Echidna doesn't support versions of solc before",
    r"compilation failed",
    r"ParserError",
    r"File outside of allowed directories",
    r"Source .* not found",
    r"Config .* not found",
    r"Could not compile",
]

FUZZ_TIME_PATTERNS = [
    (
        r"fuzz(?:ing)?(?: time)?\s*[:=]\s*"
        r"([0-9]+(?:\.[0-9]+)?)\s*(?:s|seconds?)"
    ),
    (
        rf"(?:Test\s+)?{PROPERTY_PATTERN}.*?"
        r"(?:after|in)\s+"
        r"([0-9]+(?:\.[0-9]+)?)\s*(?:s|seconds?)"
    ),
    (
        r"([0-9]+(?:\.[0-9]+)?)\s*(?:s|seconds?)"
        r"\s*(?:of fuzzing|to falsification)"
    ),
]


def parse_timestamp(value: str) -> datetime:
    return datetime.strptime(
        value,
        "%Y-%m-%d %H:%M:%S.%f",
    )


def find_timestamp(text: str, line_pattern: str):
    pattern = re.compile(
        TIMESTAMP_PATTERN + r".*" + line_pattern,
        re.IGNORECASE,
    )
    match = pattern.search(text)

    if not match:
        return None

    return parse_timestamp(match.group(1))


def infer_method(path: Path) -> str:
    try:
        parts = path.parts
        index = parts.index("reset-example")
        return parts[index + 1]
    except (ValueError, IndexError):
        return path.parent.name


def find_property_results(
    text: str,
) -> tuple[set[str], set[str]]:
    failed_properties = set()

    failed_properties.update(
        re.findall(
            rf"Test\s+({PROPERTY_PATTERN})\s+falsified!?",
            text,
            flags=re.IGNORECASE,
        )
    )

    failed_properties.update(
        re.findall(
            rf"({PROPERTY_PATTERN})\s*:\s*"
            r"(?:failed|falsified)!?",
            text,
            flags=re.IGNORECASE,
        )
    )

    passed_properties = set(
        re.findall(
            rf"({PROPERTY_PATTERN})\s*:\s*"
            r"(?:passed|passing)!?",
            text,
            flags=re.IGNORECASE,
        )
    )

    return failed_properties, passed_properties


def has_startup_error(text: str) -> bool:
    return any(
        re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )
        for pattern in STARTUP_ERROR_PATTERNS
    )


def parse_status(text: str) -> str:
    failed_properties, passed_properties = (
        find_property_results(text)
    )

    if has_startup_error(text):
        return "startup_error"

    if failed_properties:
        return "falsified"

    if re.search(
        BUDGET_EXHAUSTED_PATTERN,
        text,
        flags=re.IGNORECASE,
    ):
        return "budget_exhausted"

    if passed_properties:
        return "passed"

    return "incomplete"


def parse_fuzz_seconds(text: str):
    for pattern in FUZZ_TIME_PATTERNS:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            return float(match.group(1))

    fuzz_start = find_timestamp(
        text,
        r"Running slither on .* Done!",
    )

    falsified_time = find_timestamp(
        text,
        rf"Test\s+{PROPERTY_PATTERN}\s+falsified",
    )

    budget_end = find_timestamp(
        text,
        r"Test limit reached\. Stopping\.",
    )

    fuzz_end = falsified_time or budget_end

    if fuzz_start and fuzz_end:
        return round(
            (fuzz_end - fuzz_start).total_seconds(),
            6,
        )

    return ""


def parse_log(path: Path) -> dict:
    text = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    total_calls = re.search(
        r"Total calls:\s*(\d+)",
        text,
    )
    seed = re.search(
        r"Seed:\s*(\d+)",
        text,
    )
    unique_instructions = re.search(
        r"Unique instructions:\s*(\d+)",
        text,
    )
    process_wall = re.search(
        r"PROCESS_WALL_SECONDS=([0-9.]+)",
        text,
    )

    return {
        "method": infer_method(path),
        "file": str(path),
        "status": parse_status(text),
        "total_calls": (
            int(total_calls.group(1))
            if total_calls
            else ""
        ),
        "seed": (
            seed.group(1)
            if seed
            else ""
        ),
        "unique_instructions": (
            int(unique_instructions.group(1))
            if unique_instructions
            else ""
        ),
        "fuzz_seconds": parse_fuzz_seconds(text),
        "process_wall_seconds": (
            float(process_wall.group(1))
            if process_wall
            else ""
        ),
    }


def main() -> None:
    if len(sys.argv) != 3:
        print(
            "Usage: python parse_experiment_logs.py "
            "<log-directory> <output.csv>",
            file=sys.stderr,
        )
        raise SystemExit(1)

    log_directory = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    logs = sorted(log_directory.rglob("seed-*.log"))
    rows = [parse_log(path) for path in logs]

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "method",
        "file",
        "status",
        "total_calls",
        "seed",
        "unique_instructions",
        "fuzz_seconds",
        "process_wall_seconds",
    ]

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Parsed {len(rows)} logs")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
