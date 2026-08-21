#!/usr/bin/env python3

"""Validate the preregistered C2 public benchmark candidate registry."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


REQUIRED_FIELDS = {
    "candidate_id",
    "role",
    "source_pool",
    "repository",
    "commit",
    "source_path",
    "local_source",
    "compiler",
    "target_contract",
    "property_origin",
    "min_sequence_length",
    "semantic_classification",
    "screening_status",
    "fuzzing_status",
    "exclusion_reason",
}

ROLES = {"legacy_reference", "c2_candidate"}
SCREENING_STATUSES = {
    "included_c1",
    "identified",
    "source_available",
    "compiled",
    "property_validated",
    "semantic_supported",
    "frozen_for_c2",
    "excluded",
}


def validate_registry(path: Path, project_root: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None or not REQUIRED_FIELDS.issubset(reader.fieldnames):
            raise ValueError("Candidate registry is missing required columns")
        rows = list(reader)
    if not rows:
        raise ValueError("Candidate registry is empty")
    ids = [row["candidate_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate candidate_id")

    for row in rows:
        candidate = row["candidate_id"]
        if row["role"] not in ROLES:
            raise ValueError(f"Invalid role for {candidate}")
        if row["screening_status"] not in SCREENING_STATUSES:
            raise ValueError(f"Invalid screening_status for {candidate}")
        if row["screening_status"] == "excluded" and not row["exclusion_reason"]:
            raise ValueError(f"Excluded candidate lacks a reason: {candidate}")
        if row["role"] == "c2_candidate" and row["fuzzing_status"] != "not_started":
            if row["screening_status"] != "frozen_for_c2":
                raise ValueError(
                    f"C2 fuzzing cannot start before registry freeze: {candidate}"
                )
        if row["local_source"]:
            local = project_root / row["local_source"]
            if not local.is_file():
                raise ValueError(f"Missing local source for {candidate}: {local}")
        try:
            sequence_length = int(row["min_sequence_length"])
        except ValueError as exc:
            raise ValueError(f"Invalid min_sequence_length for {candidate}") from exc
        if sequence_length < 2:
            raise ValueError(f"Candidate is not a multi-step task: {candidate}")
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = validate_registry(args.registry, args.project_root.resolve())
    legacy = sum(row["role"] == "legacy_reference" for row in rows)
    c2 = sum(row["role"] == "c2_candidate" for row in rows)
    print(f"Validated candidates: {len(rows)} (legacy={legacy}, c2={c2})")


if __name__ == "__main__":
    main()
