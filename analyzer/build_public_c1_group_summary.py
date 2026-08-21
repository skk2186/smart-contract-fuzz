#!/usr/bin/env python3

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GROUPED_ROOT = (
    ROOT / "results/public-benchmarks/c1/grouped"
)
OUTPUT_PATH = (
    ROOT
    / "results/public-benchmarks/c1/"
    "public-c1-group-summary.csv"
)

FIELDNAMES = [
    "benchmark",
    "method",
    "total_logs",
    "valid_runs",
    "falsified_runs",
    "budget_exhausted_runs",
    "passed_runs",
    "startup_error_runs",
    "incomplete_runs",
    "success_rate",
    "median_calls_successful",
    "mean_calls_successful",
    "median_fuzz_seconds_successful",
    "median_process_wall_seconds",
]


def main() -> None:
    rows = []

    for path in sorted(GROUPED_ROOT.glob("*.csv")):
        benchmark = path.stem

        with path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            for row in csv.DictReader(file):
                rows.append(
                    {
                        "benchmark": benchmark,
                        **row,
                    }
                )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=FIELDNAMES,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
