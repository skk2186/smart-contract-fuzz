#!/usr/bin/env python3

from __future__ import annotations

import csv
import os
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

from analyzer.build_formal_group_summary import build as build_group_summary
from analyzer.experiment_validation import validate_manifest_runs
from analyzer.parse_experiment_logs import parse_log
from analyzer.summarize_experiment import summarize_rows, write_summaries


ROOT = Path(__file__).resolve().parents[1]
RUNS_ROOT = ROOT / "results/formal/runs"
MANIFEST = ROOT / "results/formal/manifest.tsv"
RESULT_ROOT = ROOT / "results/formal"

EXPECTED = {
    ("branch-value", "original"): (28, 2),
    ("branch-value", "property-k1"): (0, 30),
    ("branch-value", "value-k1"): (30, 0),
    ("branch-value", "full-k1"): (30, 0),
    ("noisy-four-step", "original"): (26, 4),
    ("noisy-four-step", "dependency-k10"): (30, 0),
    ("noisy-four-step", "property-k1"): (30, 0),
    ("noisy-four-step", "full-k1"): (30, 0),
    ("reset-example", "original"): (27, 3),
    ("reset-example", "dependency-k10"): (30, 0),
    ("reset-example", "property-k1"): (30, 0),
    ("reset-example", "full-k1"): (30, 0),
    ("repeated-call", "original"): (30, 0),
    ("repeated-call", "value-no-repeat-k1"): (0, 30),
    ("repeated-call", "full-k1"): (30, 0),
}

PARSED_FIELDS = [
    "method",
    "file",
    "status",
    "total_calls",
    "seed",
    "unique_instructions",
    "fuzz_seconds",
    "process_wall_seconds",
]

def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def validate_counts(rows_by_benchmark: dict[str, list[dict]]) -> None:
    totals = Counter()
    observed = {}
    for benchmark, rows in rows_by_benchmark.items():
        by_method = defaultdict(list)
        for row in rows:
            by_method[row["method"]].append(row)
            totals[row["status"]] += 1
        for method, method_rows in by_method.items():
            counts = Counter(row["status"] for row in method_rows)
            observed[(benchmark, method)] = (
                counts["falsified"],
                counts["budget_exhausted"],
            )
            if len(method_rows) != 30:
                raise ValueError(f"Expected 30 rows for {benchmark}/{method}")

    if observed != EXPECTED:
        raise ValueError(
            "Formal raw-log status counts conflict with audited expectations: "
            f"{observed}"
        )
    expected_totals = Counter(
        falsified=381,
        budget_exhausted=69,
        passed=0,
        startup_error=0,
        incomplete=0,
    )
    for status, count in expected_totals.items():
        if totals[status] != count:
            raise ValueError(
                f"Expected Formal {status}={count}, found {totals[status]}"
            )


def rebuild() -> None:
    groups = validate_manifest_runs(
        MANIFEST,
        RUNS_ROOT,
        expected_groups=15,
        expected_seeds=30,
        completion_marker="FORMAL_RUN_COMPLETED=1",
    )

    benchmarks = sorted({group.benchmark for group in groups})
    rows_by_benchmark = {}
    for benchmark in benchmarks:
        paths = sorted((RUNS_ROOT / benchmark).rglob("seed-*.log"))
        rows_by_benchmark[benchmark] = [
            parse_log(path.relative_to(ROOT)) for path in paths
        ]
    validate_counts(rows_by_benchmark)

    with tempfile.TemporaryDirectory(
        prefix="formal-derived-", dir=RESULT_ROOT
    ) as temporary:
        stage = Path(temporary)
        combined = []
        for benchmark in benchmarks:
            parsed_rows = rows_by_benchmark[benchmark]
            grouped_rows = summarize_rows(parsed_rows)
            parsed_path = stage / "parsed" / f"{benchmark}.csv"
            grouped_path = stage / "grouped" / f"{benchmark}.csv"
            write_csv(parsed_path, PARSED_FIELDS, parsed_rows)
            write_summaries(grouped_rows, grouped_path)
            for row in grouped_rows:
                combined.append({"benchmark": benchmark, **row})

        combined.sort(key=lambda row: (row["benchmark"], row["method"]))
        overall_path = stage / "formal-group-summary.csv"
        build_group_summary(stage / "grouped", overall_path)

        if len(combined) != 15:
            raise ValueError(f"Expected 15 summary groups, found {len(combined)}")
        if sum(int(row["total_logs"]) for row in combined) != 450:
            raise ValueError("Formal summary does not contain 450 logs")

        replacements = []
        for benchmark in benchmarks:
            replacements.extend(
                [
                    (
                        stage / "parsed" / f"{benchmark}.csv",
                        RESULT_ROOT / "parsed" / f"{benchmark}.csv",
                    ),
                    (
                        stage / "grouped" / f"{benchmark}.csv",
                        RESULT_ROOT / "grouped" / f"{benchmark}.csv",
                    ),
                ]
            )
        replacements.append((overall_path, RESULT_ROOT / overall_path.name))
        for source, destination in replacements:
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(source, destination)

    print("Rebuilt Formal parsed/grouped/overall derived results")


if __name__ == "__main__":
    rebuild()
