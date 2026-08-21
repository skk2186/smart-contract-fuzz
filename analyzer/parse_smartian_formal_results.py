#!/usr/bin/env python3
"""Parse SMARTIAN external-baseline run records without changing C2 registry."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BUG_LABELS = {"IB": "IntegerBug"}


def parse_bug_types(output_dir: Path) -> list[str]:
    bug_dir = output_dir / "bug"
    labels: set[str] = set()
    if not bug_dir.is_dir():
        return []
    for path in bug_dir.iterdir():
        if not path.is_file():
            continue
        match = re.search(r"-([A-Za-z]+)_\d+$", path.name)
        if match:
            labels.add(BUG_LABELS.get(match.group(1), match.group(1)))
    return sorted(labels)


def classify(row: dict[str, str], bug_types: list[str]) -> str:
    if row["exit_code"] != "0" or row["completed"] != "1":
        return "startup_or_incomplete"
    if "IntegerBug" in bug_types:
        return "falsified"
    return "budget_exhausted"


def parse_rows(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(newline="") as handle:
        for raw in csv.DictReader(handle, delimiter="\t"):
            output_dir = Path(raw["output_dir"])
            bug_types = parse_bug_types(output_dir)
            typed = {
                "target": raw["target"],
                "run_id": int(raw["run_id"]),
                "exit_code": int(raw["exit_code"]),
                "duration_sec": int(raw["duration_sec"]),
                "completed": int(raw["completed"]),
                "testcase_files": int(raw["testcase_files"]),
                "bug_files": int(raw["bug_files"]),
                "bug_types": ",".join(bug_types),
                "status": classify(raw, bug_types),
                "log": raw["log"],
                "output_dir": raw["output_dir"],
            }
            rows.append(typed)
    return rows


def summary(rows: list[dict[str, object]]) -> dict[str, object]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[str(row["target"])].append(row)
    group_summary: dict[str, object] = {}
    for target, target_rows in sorted(groups.items()):
        counts = Counter(str(row["status"]) for row in target_rows)
        durations = [int(row["duration_sec"]) for row in target_rows]
        valid = counts.get("falsified", 0) + counts.get("budget_exhausted", 0)
        group_summary[target] = {
            "runs": len(target_rows),
            "falsified": counts.get("falsified", 0),
            "budget_exhausted": counts.get("budget_exhausted", 0),
            "startup_or_incomplete": counts.get("startup_or_incomplete", 0),
            "success_rate_over_valid_runs": (
                counts.get("falsified", 0) / valid if valid else None
            ),
            "duration_sec_min": min(durations) if durations else None,
            "duration_sec_max": max(durations) if durations else None,
            "testcase_files_total": sum(int(row["testcase_files"]) for row in target_rows),
            "bug_files_total": sum(int(row["bug_files"]) for row in target_rows),
        }
    return {
        "purpose": "SMARTIAN external baseline for existing C1 legacy targets",
        "formal_c2_batch": False,
        "rows": len(rows),
        "targets": group_summary,
        "success_definition": "IntegerBug artifact in a completed run",
        "seed_control": "SMARTIAN CLI exposes no seed option; run_id is used",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-status", required=True, type=Path)
    parser.add_argument("--output-csv", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    args = parser.parse_args()

    rows = parse_rows(args.run_status)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", newline="") as handle:
        fields = [
            "target", "run_id", "exit_code", "duration_sec", "completed",
            "testcase_files", "bug_files", "bug_types", "status", "log", "output_dir",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    result = summary(rows)
    args.output_json.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
