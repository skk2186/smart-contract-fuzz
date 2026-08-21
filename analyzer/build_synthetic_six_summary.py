#!/usr/bin/env python3

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER_ROOT = ROOT / "results/paper-data"

BENCHMARK_ORDER = [
    "branch-value",
    "noisy-four-step",
    "reset-example",
    "repeated-call",
    "alternative-path",
    "multi-property",
]


def read_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def config_value(path: Path, key: str) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        name, separator, value = line.partition(":")
        if separator and name.strip() == key:
            return value.strip()
    raise ValueError(f"Missing {key} in {path}")


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


def build() -> tuple[list[dict], list[dict]]:
    formal = read_rows(ROOT / "results/formal/formal-group-summary.csv")
    b2 = read_rows(ROOT / "results/formal-b2/formal-b2-run-summary.csv")
    formal_lookup = {
        (row["benchmark"], row["method"]): row for row in formal
    }
    b2_lookup = {(row["benchmark"], row["method"]): row for row in b2}

    main_original = ROOT / "configs/formal-original-seq4.yaml"
    main_harness = ROOT / "configs/formal-harness-seq1.yaml"
    alt_original = ROOT / "configs/formal-b2-alternative-original.yaml"
    alt_harness = ROOT / "configs/formal-b2-alternative-harness.yaml"
    multi_original = ROOT / "configs/formal-b2-multi-original.yaml"
    multi_harness = ROOT / "configs/formal-b2-multi-harness.yaml"

    rows = []
    for benchmark in BENCHMARK_ORDER:
        for paper_method, source_method in (
            ("Original", "original"),
            ("Full-K1", "full-k1"),
        ):
            if benchmark in BENCHMARK_ORDER[:4]:
                source = formal_lookup[(benchmark, source_method)]
                batch = "formal-main"
                version = "Full-v1.0"
                falsified = int(source["falsified_runs"])
                budget = int(source["budget_exhausted_runs"])
                runs = int(source["valid_runs"])
                original_config, harness_config = main_original, main_harness
                success_definition = "target_property_falsified_in_run"
                provenance = (
                    "Formal main; Original and Harness share testLimit=100000, "
                    "timeout=30, workers=1, stopOnFail=true; transaction semantics differ"
                )
            else:
                source = b2_lookup[(benchmark, source_method)]
                batch = source["batch"]
                version = source["experiment_version"]
                falsified = int(source["successful_runs"])
                budget = int(source["budget_exhausted_runs"])
                runs = int(source["runs"])
                if benchmark == "alternative-path":
                    original_config, harness_config = alt_original, alt_harness
                    provenance = (
                        "Formal B-2; independent environment snapshot missing; "
                        "Original seqLen=3 and Harness seqLen=1"
                    )
                else:
                    original_config, harness_config = multi_original, multi_harness
                    provenance = (
                        "Formal B-2; independent environment snapshot missing; "
                        "stopOnFail=false for both methods to observe both properties"
                    )
                success_definition = source["success_definition"]

            stop_on_fail = config_value(
                original_config if paper_method == "Original" else harness_config,
                "stopOnFail",
            )
            rows.append(
                {
                    "batch": batch,
                    "experiment_version": version,
                    "benchmark": benchmark,
                    "method": paper_method,
                    "runs": runs,
                    "falsified_runs": falsified,
                    "budget_exhausted_runs": budget,
                    "success_rate": round(falsified / runs, 4),
                    "success_definition": success_definition,
                    "original_seq_len": config_value(original_config, "seqLen"),
                    "harness_seq_len": config_value(harness_config, "seqLen"),
                    "stop_on_fail": stop_on_fail,
                    "provenance_note": provenance,
                }
            )

    rows.sort(
        key=lambda row: (
            BENCHMARK_ORDER.index(row["benchmark"]),
            0 if row["method"] == "Original" else 1,
        )
    )

    overall = []
    for method in ("Original", "Full-K1"):
        selected = [row for row in rows if row["method"] == method]
        runs = sum(int(row["runs"]) for row in selected)
        falsified = sum(int(row["falsified_runs"]) for row in selected)
        budget = sum(int(row["budget_exhausted_runs"]) for row in selected)
        overall.append(
            {
                "aggregation_scope": "descriptive_across_heterogeneous_benchmarks",
                "method": method,
                "benchmarks": len(selected),
                "runs": runs,
                "falsified_runs": falsified,
                "budget_exhausted_runs": budget,
                "success_rate": round(falsified / runs, 4),
                "pooled_significance_test": "not_performed",
                "denominator_unit": "runs",
                "interpretation_note": (
                    "Descriptive total only; batches, seqLen, property count, and "
                    "stopOnFail are not fully homogeneous"
                ),
            }
        )

    expected = {"Original": (180, 171), "Full-K1": (180, 180)}
    for row in overall:
        if (int(row["runs"]), int(row["falsified_runs"])) != expected[row["method"]]:
            raise ValueError(f"Unexpected synthetic-six total: {row}")

    write_csv(
        PAPER_ROOT / "synthetic-six-benchmark-summary.csv",
        [
            "batch",
            "experiment_version",
            "benchmark",
            "method",
            "runs",
            "falsified_runs",
            "budget_exhausted_runs",
            "success_rate",
            "success_definition",
            "original_seq_len",
            "harness_seq_len",
            "stop_on_fail",
            "provenance_note",
        ],
        rows,
    )
    write_csv(
        PAPER_ROOT / "synthetic-six-overall-descriptive.csv",
        [
            "aggregation_scope",
            "method",
            "benchmarks",
            "runs",
            "falsified_runs",
            "budget_exhausted_runs",
            "success_rate",
            "pooled_significance_test",
            "denominator_unit",
            "interpretation_note",
        ],
        overall,
    )
    return rows, overall


if __name__ == "__main__":
    build()
    print("Built synthetic-six descriptive tables")
