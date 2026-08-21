#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

from analyzer.parse_experiment_logs import parse_status


PROPERTIES = [
    "echidna_value_a_safe",
    "echidna_value_b_safe",
]
ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
WALL_RE = re.compile(r"PROCESS_WALL_SECONDS=([0-9.]+)")


def seed_number(path: Path) -> int:
    match = re.fullmatch(r"seed-(\d+)\.log", path.name)
    return int(match.group(1)) if match else -1


def parse_rows(runs_root: Path) -> list[dict]:
    rows = []
    for method_directory in sorted(runs_root.iterdir()):
        if not method_directory.is_dir():
            continue
        method = method_directory.name
        for log_path in sorted(
            method_directory.glob("seed-*.log"), key=seed_number
        ):
            text = ANSI_RE.sub(
                "",
                log_path.read_text(encoding="utf-8", errors="ignore"),
            )
            failed = {}
            for property_name in PROPERTIES:
                failed[property_name] = int(
                    bool(
                        re.search(
                            rf"{re.escape(property_name)}\s*:\s*"
                            r"(?:failed|falsified)",
                            text,
                            re.IGNORECASE,
                        )
                    )
                )
            wall = WALL_RE.search(text)
            rows.append(
                {
                    "method": method,
                    "seed": seed_number(log_path),
                    **failed,
                    "both_properties_failed": int(all(failed.values())),
                    "property_outcomes": len(PROPERTIES),
                    "run_status": parse_status(text),
                    "wall_seconds": float(wall.group(1)) if wall else "",
                }
            )
    return rows


def summarize_rows(rows: list[dict]) -> list[dict]:
    summaries = []
    methods = sorted({row["method"] for row in rows})
    for method in methods:
        method_rows = [row for row in rows if row["method"] == method]
        runs = len(method_rows)
        for property_name in PROPERTIES:
            outcomes = sum(int(row[property_name]) for row in method_rows)
            summaries.append(
                {
                    "method": method,
                    "metric": property_name,
                    "metric_type": "property_outcome",
                    "denominator_unit": "runs_with_one_outcome_for_this_property",
                    "runs": runs,
                    "successful_outcomes": outcomes,
                    "success_rate": round(outcomes / runs, 4) if runs else "",
                }
            )
        composite = sum(
            int(row["both_properties_failed"]) for row in method_rows
        )
        summaries.append(
            {
                "method": method,
                "metric": "both_properties_failed",
                "metric_type": "run_level_composite",
                "denominator_unit": "runs",
                "runs": runs,
                "successful_outcomes": composite,
                "success_rate": round(composite / runs, 4) if runs else "",
            }
        )
    return summaries


def write_outputs(
    rows: list[dict], detailed_path: Path, grouped_path: Path
) -> None:
    detailed_fields = [
        "method",
        "seed",
        *PROPERTIES,
        "both_properties_failed",
        "property_outcomes",
        "run_status",
        "wall_seconds",
    ]
    grouped_fields = [
        "method",
        "metric",
        "metric_type",
        "denominator_unit",
        "runs",
        "successful_outcomes",
        "success_rate",
    ]
    for path, fields, output_rows in (
        (detailed_path, detailed_fields, rows),
        (grouped_path, grouped_fields, summarize_rows(rows)),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(
                file, fieldnames=fields, lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(output_rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("runs_root", type=Path)
    parser.add_argument("detailed_output", type=Path)
    parser.add_argument("grouped_output", type=Path)
    arguments = parser.parse_args()
    rows = parse_rows(arguments.runs_root)
    write_outputs(rows, arguments.detailed_output, arguments.grouped_output)


if __name__ == "__main__":
    main()
