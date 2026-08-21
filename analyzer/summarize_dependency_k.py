import csv
import re
import statistics
from pathlib import Path


ROOT = Path("results/ablation-k")
K_VALUES = [1, 3, 5, 6, 10]


def parse_log(path: Path) -> tuple[bool, int | None]:
    text = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    falsified = bool(
        re.search(
            r"echidna_value_safe:\s*failed",
            text,
            re.IGNORECASE,
        )
    )

    calls_match = re.search(
        r"Total calls:\s*(\d+)",
        text,
    )

    calls = (
        int(calls_match.group(1))
        if calls_match
        else None
    )

    return falsified, calls


rows = []

for k in K_VALUES:
    directory = ROOT / f"dependency-k{k}"
    logs = sorted(directory.glob("seed-*.log"))

    successful_calls = []
    successes = 0

    for log in logs:
        falsified, calls = parse_log(log)

        if falsified:
            successes += 1

            if calls is not None:
                successful_calls.append(calls)

    rows.append(
        {
            "k": k,
            "runs": len(logs),
            "falsified_runs": successes,
            "success_rate": (
                round(successes / len(logs), 4)
                if logs else 0
            ),
            "median_calls_successful": (
                statistics.median(successful_calls)
                if successful_calls else ""
            ),
            "mean_calls_successful": (
                round(
                    statistics.mean(successful_calls),
                    4,
                )
                if successful_calls else ""
            ),
        }
    )

output = ROOT / "dependency-k-summary.csv"

with output.open(
    "w",
    newline="",
    encoding="utf-8",
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "k",
            "runs",
            "falsified_runs",
            "success_rate",
            "median_calls_successful",
            "mean_calls_successful",
        ],
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved to {output}")
