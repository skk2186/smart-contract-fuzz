#!/usr/bin/env python3

from __future__ import annotations

import csv
import os
import re
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

from analyzer.experiment_validation import validate_manifest_runs
from analyzer.parse_experiment_logs import parse_log
from analyzer.parse_multi_property_results import (
    PROPERTIES,
    parse_rows as parse_multi_rows,
    write_outputs as write_multi_outputs,
)
from analyzer.summarize_experiment import summarize_rows, write_summaries


ROOT = Path(__file__).resolve().parents[1]
RESULT_ROOT = ROOT / "results/formal-b2"
RUNS_ROOT = RESULT_ROOT / "runs"
MANIFEST = RESULT_ROOT / "manifest.tsv"

RUN_SUMMARY_FIELDS = [
    "experiment_version",
    "batch",
    "benchmark",
    "method",
    "runs",
    "successful_runs",
    "budget_exhausted_runs",
    "startup_error_runs",
    "incomplete_runs",
    "success_rate",
    "success_definition",
    "denominator_unit",
    "environment_snapshot_status",
]


def metadata_from_log(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    version = re.search(r"(?m)^FORMAL_EXPERIMENT_VERSION=(.+)$", text)
    batch = re.search(r"(?m)^FORMAL_BATCH=(.+)$", text)
    if not version or not batch:
        raise ValueError(f"Missing B2 version/batch metadata in {path}")
    return version.group(1).strip(), batch.group(1).strip()


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


def rebuild() -> None:
    groups = validate_manifest_runs(
        MANIFEST,
        RUNS_ROOT,
        expected_groups=5,
        expected_seeds=30,
        completion_marker="FORMAL_B2_RUN_COMPLETED=1",
    )

    versions = set()
    batches = set()
    for group in groups:
        for seed in range(1, 31):
            version, batch = metadata_from_log(
                RUNS_ROOT
                / group.benchmark
                / group.method
                / f"seed-{seed}.log"
            )
            versions.add(version)
            batches.add(batch)
    if versions != {"Full-v1.0"} or batches != {"B-2"}:
        raise ValueError(
            f"Unexpected B2 metadata: versions={versions}, batches={batches}"
        )

    alternative_paths = sorted(
        (RUNS_ROOT / "alternative-path").rglob("seed-*.log")
    )
    alternative_rows = [
        parse_log(path.relative_to(ROOT)) for path in alternative_paths
    ]
    alternative_grouped = summarize_rows(alternative_rows)
    if len(alternative_rows) != 90 or any(
        row["status"] != "falsified" for row in alternative_rows
    ):
        raise ValueError("AlternativePath raw counts conflict with audit")

    multi_rows = parse_multi_rows(RUNS_ROOT / "multi-property")
    if len(multi_rows) != 60:
        raise ValueError(f"Expected 60 MultiProperty run rows, found {len(multi_rows)}")
    by_method = defaultdict(list)
    for row in multi_rows:
        by_method[row["method"]].append(row)
    if set(by_method) != {"original", "full-k1"}:
        raise ValueError(f"Unexpected MultiProperty methods: {set(by_method)}")
    for method, rows in by_method.items():
        if len(rows) != 30 or sum(
            int(row["both_properties_failed"]) for row in rows
        ) != 30:
            raise ValueError(f"MultiProperty run-level count mismatch: {method}")
        for property_name in PROPERTIES:
            if sum(int(row[property_name]) for row in rows) != 30:
                raise ValueError(
                    f"MultiProperty property count mismatch: {method}/{property_name}"
                )

    run_summary = []
    for row in alternative_grouped:
        run_summary.append(
            {
                "experiment_version": "Full-v1.0",
                "batch": "B-2",
                "benchmark": "alternative-path",
                "method": row["method"],
                "runs": row["valid_runs"],
                "successful_runs": row["falsified_runs"],
                "budget_exhausted_runs": row["budget_exhausted_runs"],
                "startup_error_runs": row["startup_error_runs"],
                "incomplete_runs": row["incomplete_runs"],
                "success_rate": row["success_rate"],
                "success_definition": "target_property_falsified_in_run",
                "denominator_unit": "runs",
                "environment_snapshot_status": "missing_independent_snapshot",
            }
        )
    for method in sorted(by_method):
        rows = by_method[method]
        statuses = Counter(row["run_status"] for row in rows)
        successful = sum(int(row["both_properties_failed"]) for row in rows)
        run_summary.append(
            {
                "experiment_version": "Full-v1.0",
                "batch": "B-2",
                "benchmark": "multi-property",
                "method": method,
                "runs": len(rows),
                "successful_runs": successful,
                "budget_exhausted_runs": statuses["budget_exhausted"],
                "startup_error_runs": statuses["startup_error"],
                "incomplete_runs": statuses["incomplete"],
                "success_rate": round(successful / len(rows), 4),
                "success_definition": "both_specified_properties_falsified_in_same_run",
                "denominator_unit": "runs",
                "environment_snapshot_status": "missing_independent_snapshot",
            }
        )
    run_summary.sort(key=lambda row: (row["benchmark"], row["method"]))
    if len(run_summary) != 5 or sum(
        int(row["successful_runs"]) for row in run_summary
    ) != 150:
        raise ValueError("B2 run-level summary does not equal 150/150")

    with tempfile.TemporaryDirectory(prefix="formal-b2-derived-", dir=RESULT_ROOT) as temporary:
        stage = Path(temporary)
        alternative_parsed = stage / "parsed/alternative-path.csv"
        alternative_grouped_path = stage / "grouped/alternative-path.csv"
        multi_detailed = stage / "parsed/multi-property-detailed.csv"
        multi_grouped = stage / "grouped/multi-property-properties.csv"
        run_summary_path = stage / "formal-b2-run-summary.csv"

        write_csv(
            alternative_parsed,
            [
                "method",
                "file",
                "status",
                "total_calls",
                "seed",
                "unique_instructions",
                "fuzz_seconds",
                "process_wall_seconds",
            ],
            alternative_rows,
        )
        write_summaries(alternative_grouped, alternative_grouped_path)
        write_multi_outputs(multi_rows, multi_detailed, multi_grouped)
        write_csv(run_summary_path, RUN_SUMMARY_FIELDS, run_summary)

        for source, relative in (
            (alternative_parsed, "parsed/alternative-path.csv"),
            (alternative_grouped_path, "grouped/alternative-path.csv"),
            (multi_detailed, "parsed/multi-property-detailed.csv"),
            (multi_grouped, "grouped/multi-property-properties.csv"),
            (run_summary_path, "formal-b2-run-summary.csv"),
        ):
            destination = RESULT_ROOT / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(source, destination)

    print("Rebuilt Formal-B2 parsed/grouped/run-level derived results")


if __name__ == "__main__":
    rebuild()
