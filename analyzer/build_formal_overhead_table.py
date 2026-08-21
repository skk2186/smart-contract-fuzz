#!/usr/bin/env python3

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

overhead_path = (
    ROOT
    / "results/formal/overhead/"
    "overhead-summary.csv"
)

candidate_path = (
    ROOT
    / "results/formal/"
    "formal-candidate-summary.csv"
)

output_path = (
    ROOT
    / "results/formal/"
    "formal-overhead-table.csv"
)


with overhead_path.open(
    encoding="utf-8",
    newline="",
) as file:
    overhead_rows = list(csv.DictReader(file))

with candidate_path.open(
    encoding="utf-8",
    newline="",
) as file:
    candidate_rows = {
        row["benchmark"]: row
        for row in csv.DictReader(file)
    }


wanted_stages = {
    "analysis_harness_total",
    "solc_compilation",
    "preparation_with_compilation_total",
}

times = {}

for row in overhead_rows:
    if row["stage"] not in wanted_stages:
        continue

    times.setdefault(
        row["benchmark"],
        {},
    )[row["stage"]] = row


rows = []

for benchmark, candidate in candidate_rows.items():
    benchmark_times = times[benchmark]

    rows.append(
        {
            "benchmark": benchmark,
            "dependency_paths": candidate[
                "dependency_retained_paths"
            ],
            "property_paths": candidate[
                "property_retained_paths"
            ],
            "repeat_paths": candidate[
                "repeat_retained_paths"
            ],
            "full_correct_rank": candidate[
                "full_correct_rank"
            ],
            "analysis_harness_median_seconds": (
                benchmark_times[
                    "analysis_harness_total"
                ]["median_seconds"]
            ),
            "analysis_harness_iqr": (
                "["
                + benchmark_times[
                    "analysis_harness_total"
                ]["q1_seconds"]
                + ", "
                + benchmark_times[
                    "analysis_harness_total"
                ]["q3_seconds"]
                + "]"
            ),
            "compilation_median_seconds": (
                benchmark_times[
                    "solc_compilation"
                ]["median_seconds"]
            ),
            "total_preparation_median_seconds": (
                benchmark_times[
                    "preparation_with_compilation_total"
                ]["median_seconds"]
            ),
        }
    )


fieldnames = [
    "benchmark",
    "dependency_paths",
    "property_paths",
    "repeat_paths",
    "full_correct_rank",
    "analysis_harness_median_seconds",
    "analysis_harness_iqr",
    "compilation_median_seconds",
    "total_preparation_median_seconds",
]

with output_path.open(
    "w",
    encoding="utf-8",
    newline="",
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames,
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved paper-oriented table to {output_path}")
