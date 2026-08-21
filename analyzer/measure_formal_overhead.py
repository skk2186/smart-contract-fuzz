#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

CASES = [
    {
        "benchmark": "noisy-four-step",
        "source": "contracts/benchmarks/NoisyFourStepExample.sol",
        "contract": "NoisyFourStepExample",
        "harness": "NoisyFourStepOverheadHarness",
    },
    {
        "benchmark": "reset-example",
        "source": "contracts/benchmarks/ResetExample.sol",
        "contract": "ResetExample",
        "harness": "ResetOverheadHarness",
    },
    {
        "benchmark": "branch-value",
        "source": "contracts/benchmarks/BranchValueExample.sol",
        "contract": "BranchValueExample",
        "harness": "BranchValueOverheadHarness",
    },
    {
        "benchmark": "repeated-call",
        "source": "contracts/benchmarks/RepeatedCallExample.sol",
        "contract": "RepeatedCallExample",
        "harness": "RepeatedCallOverheadHarness",
    },
]


def run_stage(
    *,
    benchmark: str,
    repetition: int,
    stage: str,
    command: list[str],
    stderr_path: Path,
    stdout_path: Path | None = None,
) -> float:
    stderr_path.parent.mkdir(parents=True, exist_ok=True)

    start = time.perf_counter()

    with stderr_path.open("w", encoding="utf-8") as stderr_file:
        if stdout_path is None:
            completed = subprocess.run(
                command,
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
                stderr=stderr_file,
                text=True,
                check=False,
            )
        else:
            stdout_path.parent.mkdir(parents=True, exist_ok=True)

            with stdout_path.open("w", encoding="utf-8") as stdout_file:
                completed = subprocess.run(
                    command,
                    cwd=ROOT,
                    stdout=stdout_file,
                    stderr=stderr_file,
                    text=True,
                    check=False,
                )

    elapsed = time.perf_counter() - start

    if completed.returncode != 0:
        raise RuntimeError(
            f"{benchmark}, repetition={repetition}, "
            f"stage={stage} failed with exit code "
            f"{completed.returncode}. See {stderr_path}"
        )

    return elapsed


def write_detailed_csv(
    rows: list[dict[str, Any]],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "benchmark",
        "repetition",
        "stage",
        "seconds",
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


def summarize(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[float]] = {}

    for row in rows:
        key = (
            str(row["benchmark"]),
            str(row["stage"]),
        )

        groups.setdefault(key, []).append(
            float(row["seconds"])
        )

    summary_rows: list[dict[str, Any]] = []

    for (benchmark, stage), values in sorted(groups.items()):
        quartiles = statistics.quantiles(
            values,
            n=4,
            method="inclusive",
        )

        summary_rows.append(
            {
                "benchmark": benchmark,
                "stage": stage,
                "runs": len(values),
                "median_seconds": round(
                    statistics.median(values),
                    6,
                ),
                "mean_seconds": round(
                    statistics.mean(values),
                    6,
                ),
                "q1_seconds": round(quartiles[0], 6),
                "q3_seconds": round(quartiles[2], 6),
                "min_seconds": round(min(values), 6),
                "max_seconds": round(max(values), 6),
            }
        )

    return summary_rows


def write_summary_csv(
    rows: list[dict[str, Any]],
    output_path: Path,
) -> None:
    fieldnames = [
        "benchmark",
        "stage",
        "runs",
        "median_seconds",
        "mean_seconds",
        "q1_seconds",
        "q3_seconds",
        "min_seconds",
        "max_seconds",
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


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Measure Full-v1.0 preprocessing and compilation overhead."
        )
    )

    parser.add_argument(
        "--repetitions",
        type=int,
        default=10,
        help="Number of repeated measurements per benchmark.",
    )

    parser.add_argument(
        "--output-directory",
        type=Path,
        default=Path("results/formal/overhead"),
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    if arguments.repetitions <= 0:
        raise SystemExit("--repetitions must be positive")

    output_directory = ROOT / arguments.output_directory
    artifact_root = output_directory / "artifacts"
    harness_root = (
        ROOT / "contracts/harnesses/formal-overhead"
    )

    output_directory.mkdir(parents=True, exist_ok=True)
    artifact_root.mkdir(parents=True, exist_ok=True)
    harness_root.mkdir(parents=True, exist_ok=True)

    python_executable = sys.executable
    detailed_rows: list[dict[str, Any]] = []

    for case in CASES:
        benchmark = case["benchmark"]
        source = ROOT / case["source"]
        contract = case["contract"]

        if not source.is_file():
            raise SystemExit(f"Missing source: {source}")

        for repetition in range(1, arguments.repetitions + 1):
            print(
                f"[{benchmark}] repetition "
                f"{repetition}/{arguments.repetitions}"
            )

            work_directory = (
                artifact_root
                / benchmark
                / f"run-{repetition:02d}"
            )

            harness_directory = (
                harness_root
                / benchmark
                / f"run-{repetition:02d}"
            )

            work_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

            harness_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

            rw_json = work_directory / "rw.json"
            repeat_json = (
                work_directory
                / "repeat-property-sequences.json"
            )
            constraints_json = (
                work_directory
                / "value-constraints.json"
            )
            full_json = (
                work_directory
                / "full-sequences.json"
            )
            harness_file = (
                harness_directory
                / f"{case['harness']}.sol"
            )

            stage_times: dict[str, float] = {}

            stage_times["extract_rw"] = run_stage(
                benchmark=benchmark,
                repetition=repetition,
                stage="extract_rw",
                command=[
                    python_executable,
                    str(ROOT / "analyzer/extract_rw.py"),
                    str(source),
                ],
                stdout_path=rw_json,
                stderr_path=work_directory / "extract_rw.stderr.log",
            )

            stage_times["property_repeat_generation"] = run_stage(
                benchmark=benchmark,
                repetition=repetition,
                stage="property_repeat_generation",
                command=[
                    python_executable,
                    str(
                        ROOT
                        / "analyzer/"
                        "generate_repetition_aware_sequences.py"
                    ),
                    str(rw_json),
                    "4",
                    "500",
                    "--contract",
                    contract,
                    "--max-function-visits",
                    "2",
                ],
                stdout_path=repeat_json,
                stderr_path=(
                    work_directory
                    / "property_repeat_generation.stderr.log"
                ),
            )

            stage_times["extract_value_constraints"] = run_stage(
                benchmark=benchmark,
                repetition=repetition,
                stage="extract_value_constraints",
                command=[
                    python_executable,
                    str(
                        ROOT
                        / "analyzer/"
                        "extract_value_constraints.py"
                    ),
                    str(source),
                    "--contract",
                    contract,
                ],
                stdout_path=constraints_json,
                stderr_path=(
                    work_directory
                    / "extract_value_constraints.stderr.log"
                ),
            )

            stage_times["value_reranking"] = run_stage(
                benchmark=benchmark,
                repetition=repetition,
                stage="value_reranking",
                command=[
                    python_executable,
                    str(
                        ROOT
                        / "analyzer/"
                        "generate_value_guided_sequences.py"
                    ),
                    str(repeat_json),
                    str(constraints_json),
                    "--contract",
                    contract,
                ],
                stdout_path=full_json,
                stderr_path=(
                    work_directory
                    / "value_reranking.stderr.log"
                ),
            )

            stage_times["harness_generation"] = run_stage(
                benchmark=benchmark,
                repetition=repetition,
                stage="harness_generation",
                command=[
                    python_executable,
                    str(
                        ROOT
                        / "analyzer/"
                        "generate_harness_from_paths.py"
                    ),
                    "--source",
                    str(source),
                    "--sequences",
                    str(full_json),
                    "--target-contract",
                    contract,
                    "--harness-contract",
                    case["harness"],
                    "--output",
                    str(harness_file),
                    "--prefix",
                    "full",
                    "--top-k",
                    "1",
                ],
                stderr_path=(
                    work_directory
                    / "harness_generation.stderr.log"
                ),
            )

            stage_times["solc_compilation"] = run_stage(
                benchmark=benchmark,
                repetition=repetition,
                stage="solc_compilation",
                command=[
                    "solc",
                    "--bin",
                    str(harness_file),
                ],
                stderr_path=(
                    work_directory
                    / "solc_compilation.stderr.log"
                ),
            )

            analysis_harness_total = sum(
                stage_times[name]
                for name in (
                    "extract_rw",
                    "property_repeat_generation",
                    "extract_value_constraints",
                    "value_reranking",
                    "harness_generation",
                )
            )

            end_to_end_total = (
                analysis_harness_total
                + stage_times["solc_compilation"]
            )

            stage_times["analysis_harness_total"] = (
                analysis_harness_total
            )
            stage_times["preparation_with_compilation_total"] = (
                end_to_end_total
            )

            for stage, seconds in stage_times.items():
                detailed_rows.append(
                    {
                        "benchmark": benchmark,
                        "repetition": repetition,
                        "stage": stage,
                        "seconds": round(seconds, 9),
                    }
                )

            write_detailed_csv(
                detailed_rows,
                output_directory / "overhead-detailed.csv",
            )

    summary_rows = summarize(detailed_rows)

    write_summary_csv(
        summary_rows,
        output_directory / "overhead-summary.csv",
    )

    metadata = {
        "method_version": "Full-v1.0",
        "repetitions": arguments.repetitions,
        "max_path_length": 4,
        "max_function_visits": 2,
        "top_k": 1,
        "benchmarks": [
            case["benchmark"]
            for case in CASES
        ],
    }

    with (
        output_directory / "metadata.json"
    ).open("w", encoding="utf-8") as file:
        json.dump(
            metadata,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(
        "Saved detailed results to "
        f"{output_directory / 'overhead-detailed.csv'}"
    )
    print(
        "Saved summary results to "
        f"{output_directory / 'overhead-summary.csv'}"
    )


if __name__ == "__main__":
    main()
