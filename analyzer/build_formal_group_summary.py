#!/usr/bin/env python3

from __future__ import annotations

import csv
import sys
from pathlib import Path


FIELDS = [
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


def build(grouped_root: Path, output_path: Path) -> None:
    rows = []
    for path in sorted(grouped_root.glob("*.csv")):
        with path.open(encoding="utf-8", newline="") as file:
            rows.extend(
                {"benchmark": path.stem, **row}
                for row in csv.DictReader(file)
            )
    rows.sort(key=lambda row: (row["benchmark"], row["method"]))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: build_formal_group_summary.py <grouped-dir> <output.csv>"
        )
    build(Path(sys.argv[1]), Path(sys.argv[2]))


if __name__ == "__main__":
    main()
