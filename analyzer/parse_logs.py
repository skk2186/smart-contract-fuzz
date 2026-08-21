import csv
import re
import sys
from pathlib import Path


def parse_log(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")

    status_match = re.search(
        r"echidna_value_safe:\s+(failed|passed|passing)",
        text,
        re.IGNORECASE,
    )

    if status_match:
        raw_status = status_match.group(1).lower()

        if raw_status == "failed":
            status = "falsified"
        else:
            status = "not_falsified"
    elif "Test limit reached" in text:
        status = "budget_exhausted"
    else:
        status = "unknown"
    calls_match = re.search(r"Total calls:\s*(\d+)", text)
    seed_match = re.search(r"Seed:\s*(\d+)", text)
    instructions_match = re.search(r"Unique instructions:\s*(\d+)", text)

    return {
        "file": str(path),
        "status": status,
        "total_calls": int(calls_match.group(1)) if calls_match else "",
        "seed": seed_match.group(1) if seed_match else "",
        "unique_instructions": (
            int(instructions_match.group(1))
            if instructions_match else ""
        ),
    }


def main() -> None:
    if len(sys.argv) != 3:
        print(
            "Usage: python analyzer/parse_logs.py <log-directory> <output.csv>"
        )
        raise SystemExit(1)

    log_dir = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    logs = sorted(log_dir.rglob("*.log"))
    rows = [parse_log(path) for path in logs]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "file",
                "status",
                "total_calls",
                "seed",
                "unique_instructions",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Parsed {len(rows)} log files")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
