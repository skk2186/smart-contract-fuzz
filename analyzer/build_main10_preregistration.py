#!/usr/bin/env python3
"""Build and validate the B4 public supported 10-seed preregistration.

This script only reads the B2 registries and the two public C-1 configs.  It
never runs Echidna, Slither, solc, or any other experiment command.  ``--check``
validates the inputs without writing; ``--write`` writes only the two B3
preregistration TSV files under ``paper-ready/v1``.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "paper-ready" / "v1" / "public_benchmark_registry.tsv"
GATE_PATH = REPO_ROOT / "paper-ready" / "v1" / "native_replay_gate.tsv"
PREREG_PATH = REPO_ROOT / "paper-ready" / "v1" / "main10_preregistration.tsv"
EXPECTED_RUNS_PATH = REPO_ROOT / "paper-ready" / "v1" / "main10_expected_runs.tsv"
OUTPUT_ROOT = "work/v1-restart/b4-public-supported-10seed-main/"

SUPPORTED_IDS = ("PUB01", "PUB02", "PUB03", "PUB04")
METHODS = (("Original", "original"), ("Full-K1", "full-k1"), ("Full-K5", "full-k5"))
SEEDS = tuple(range(1, 11))
EXPECTED_ARTIFACTS = "manifest.tsv,command.txt,environment.txt,raw,parsed,summary,status,checksums"
STATUS_POLICY = (
    "falsified_or_failed_marker_first;budget_exhausted=no_observed_counterexample_within_budget;"
    "startup_error|unknown_error|incomplete=separate;parser_status_mismatch=block"
)

PREREG_FIELDS = [
    "run_group", "benchmark_id", "benchmark_name", "method", "seed_start", "seed_end",
    "seed_count", "expected_runs", "source_path", "config_path", "property", "output_root",
    "status_policy", "main_table_candidate", "notes",
]
EXPECTED_FIELDS = [
    "run_id", "benchmark_id", "benchmark_name", "method", "seed", "source_path",
    "config_path", "output_dir", "expected_artifacts", "status",
]


class ValidationError(Exception):
    """Raised when the preregistration inputs are not safe to use."""


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.is_file():
        raise ValidationError(f"required input is missing: {path.relative_to(REPO_ROOT)}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = reader.fieldnames or []
        rows = list(reader)
    return fields, rows


def read_simple_config(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise ValidationError(f"required config is missing: {path.relative_to(REPO_ROOT)}")
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def validate_inputs() -> list[dict[str, str]]:
    registry_fields, registry_rows = read_tsv(REGISTRY_PATH)
    gate_fields, gate_rows = read_tsv(GATE_PATH)
    required_registry = {"benchmark_id", "benchmark_name", "source_path", "classification", "status", "property"}
    required_gate = {
        "benchmark_id", "benchmark_name", "classification_before_b2", "gate_status",
        "execution_mode", "source_path", "property", "main_table_gate", "b3_action",
    }
    if not required_registry.issubset(registry_fields):
        raise ValidationError(f"registry header is missing: {sorted(required_registry - set(registry_fields))}")
    if not required_gate.issubset(gate_fields):
        raise ValidationError(f"native gate header is missing: {sorted(required_gate - set(gate_fields))}")

    registry_by_id: dict[str, dict[str, str]] = {}
    for row in registry_rows:
        benchmark_id = row.get("benchmark_id", "")
        if benchmark_id in registry_by_id:
            raise ValidationError(f"duplicate registry benchmark_id: {benchmark_id}")
        registry_by_id[benchmark_id] = row
    gate_by_id: dict[str, dict[str, str]] = {}
    for row in gate_rows:
        benchmark_id = row.get("benchmark_id", "")
        if benchmark_id in gate_by_id:
            raise ValidationError(f"duplicate native gate benchmark_id: {benchmark_id}")
        gate_by_id[benchmark_id] = row

    selected: list[dict[str, str]] = []
    for benchmark_id in SUPPORTED_IDS:
        registry = registry_by_id.get(benchmark_id)
        gate = gate_by_id.get(benchmark_id)
        if registry is None or gate is None:
            raise ValidationError(f"missing B2 registry/gate row for {benchmark_id}")
        if registry["classification"] != "supported":
            raise ValidationError(f"{benchmark_id} is not supported in the public registry")
        if registry["status"] not in {"b3_preregistered", "static_gate_pass"}:
            raise ValidationError(f"{benchmark_id} has unexpected B3 status: {registry['status']}")
        if gate["classification_before_b2"] != "supported":
            raise ValidationError(f"{benchmark_id} was not supported before B2")
        if gate["gate_status"] != "static_gate_pass" or gate["execution_mode"] != "static_gate_only":
            raise ValidationError(f"{benchmark_id} does not have the required static B2 gate")
        if gate["main_table_gate"] != "yes_after_b3_prereg" or gate["b3_action"] != "include_in_b3_supported":
            raise ValidationError(f"{benchmark_id} has an unsafe B3 action in the native gate")
        if registry["source_path"] != gate["source_path"] or registry["property"] != gate["property"]:
            raise ValidationError(f"registry/native gate source or property mismatch for {benchmark_id}")
        selected.append(registry)

    original_config = REPO_ROOT / "configs" / "public-c1-original.yaml"
    harness_config = REPO_ROOT / "configs" / "public-c1-harness.yaml"
    original = read_simple_config(original_config)
    harness = read_simple_config(harness_config)
    expected_common = {
        "testMode": "property", "testLimit": "100000", "timeout": "30",
        "workers": "1", "stopOnFail": "true",
    }
    for label, config in (("Original", original), ("Harness", harness)):
        for key, value in expected_common.items():
            if config.get(key) != value:
                raise ValidationError(f"{label} config {key}={config.get(key)!r}, expected {value!r}")
        if "corpusDir" in config:
            raise ValidationError(f"{label} config unexpectedly declares corpusDir")
    if original.get("seqLen") != "4" or harness.get("seqLen") != "1":
        raise ValidationError("public C-1 Original/Harness seqLen inheritance is not 4/1")

    for row in selected:
        source = REPO_ROOT / row["source_path"]
        if not source.is_file():
            raise ValidationError(f"registered source is missing: {row['source_path']}")
    return selected


def build_rows(selected: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    prereg_rows: list[dict[str, str]] = []
    expected_rows: list[dict[str, str]] = []
    for benchmark in selected:
        caveat = (
            "B3 preregistration only; preserve Original multi-transaction versus Harness single-wrapper "
            "caller, atomicity, rollback, and Total calls semantic caveats; budget_exhausted is not property passed."
        )
        for display_method, normalized_method in METHODS:
            config_path = (
                "configs/public-c1-original.yaml"
                if normalized_method == "original"
                else "configs/public-c1-harness.yaml"
            )
            prereg_rows.append({
                "run_group": "B4-main10", "benchmark_id": benchmark["benchmark_id"],
                "benchmark_name": benchmark["benchmark_name"], "method": display_method,
                "seed_start": "1", "seed_end": "10", "seed_count": "10", "expected_runs": "10",
                "source_path": benchmark["source_path"], "config_path": config_path,
                "property": benchmark["property"], "output_root": OUTPUT_ROOT,
                "status_policy": STATUS_POLICY, "main_table_candidate": "after_successful_b4_summary",
                "notes": caveat,
            })
            for seed in SEEDS:
                run_id = f"b4-{benchmark['benchmark_name']}-{normalized_method}-s{seed}"
                expected_rows.append({
                    "run_id": run_id, "benchmark_id": benchmark["benchmark_id"],
                    "benchmark_name": benchmark["benchmark_name"], "method": normalized_method,
                    "seed": str(seed), "source_path": benchmark["source_path"],
                    "config_path": config_path, "output_dir": f"{OUTPUT_ROOT}{run_id}/",
                    "expected_artifacts": EXPECTED_ARTIFACTS, "status": "preregistered",
                })
    return prereg_rows, expected_rows


def ensure_unique(rows: list[dict[str, str]], field: str) -> None:
    values = [row[field] for row in rows]
    if len(values) != len(set(values)):
        raise ValidationError(f"duplicate {field} in generated preregistration")


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="validate B2 inputs without writing files")
    group.add_argument("--write", action="store_true", help="write only the two B3 preregistration TSV files")
    args = parser.parse_args()

    try:
        selected = validate_inputs()
        prereg_rows, expected_rows = build_rows(selected)
        ensure_unique([{"key": f"{row['benchmark_id']}:{row['method']}"} for row in prereg_rows], "key")
        ensure_unique(expected_rows, "run_id")
        if len(prereg_rows) != 12 or len(expected_rows) != 120:
            raise ValidationError(f"unexpected generated sizes: prereg={len(prereg_rows)}, expected={len(expected_rows)}")
        if args.write:
            PREREG_PATH.parent.mkdir(parents=True, exist_ok=True)
            write_tsv(PREREG_PATH, PREREG_FIELDS, prereg_rows)
            write_tsv(EXPECTED_RUNS_PATH, EXPECTED_FIELDS, expected_rows)
            print(f"wrote {PREREG_PATH.relative_to(REPO_ROOT)} ({len(prereg_rows)} data rows)")
            print(f"wrote {EXPECTED_RUNS_PATH.relative_to(REPO_ROOT)} ({len(expected_rows)} data rows)")
        else:
            print(f"check passed: 4 benchmarks, 3 methods, 10 seeds, {len(expected_rows)} expected runs")
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
