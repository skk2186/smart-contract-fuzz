#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

OUTPUT_ROOT = ROOT / "results/public-benchmarks/c0"
HARNESS_ROOT = ROOT / "contracts/harnesses/public-c0"


CASES = [
    {
        "benchmark": "echidna-multi",
        "compiler": "0.8.20",
        "source": (
            "contracts/public-benchmarks/"
            "raw/echidna/multi.sol"
        ),
        "contract": "C",
        "harness": "PublicEchidnaMultiFullK1Harness",
        "expected": [
            "f(uint256)",
            "g(uint256)",
            "h(uint256)",
        ],
        "requires_repeat": False,
    },
    {
        "benchmark": "echidna-flags",
        "compiler": "0.8.20",
        "source": (
            "contracts/public-benchmarks/"
            "raw/echidna/flags.sol"
        ),
        "contract": "Test",
        "harness": "PublicEchidnaFlagsFullK1Harness",
        "expected": [
            "set0(int256)",
            "set1(int256)",
        ],
        "requires_repeat": False,
    },
    {
        "benchmark": "exercise2-access-control",
        "compiler": "0.8.20",
        "source": (
            "contracts/public-benchmarks/"
            "raw/exercise2/solution.sol"
        ),
        "contract": "TestToken",
        "harness": "PublicExercise2FullK1Harness",
        "expected": [
            "Owner()",
            "resume()",
        ],
        "requires_repeat": False,
    },
    {
        "benchmark": "smartbugs-multifunc",
        "compiler": "0.4.23",
        "source": (
            "contracts/public-benchmarks/"
            "adapted/SmartBugsMultiFuncEchidna.sol"
        ),
        "contract": "SmartBugsMultiFuncEchidna",
        "harness": "PublicSmartBugsMultiFuncFullK1Harness",
        "expected": [
            "init()",
            "run(uint256)",
        ],
        "requires_repeat": False,
    },
    {
        "benchmark": "smartbugs-onefunc",
        "compiler": "0.4.23",
        "source": (
            "contracts/public-benchmarks/"
            "adapted/SmartBugsOneFuncEchidna.sol"
        ),
        "contract": "SmartBugsOneFuncEchidna",
        "harness": "PublicSmartBugsOneFuncFullK1Harness",
        "expected": [
            "run(uint256)",
            "run(uint256)",
        ],
        "requires_repeat": True,
    },
]


STAGE_FIELDS = [
    "switch_compiler",
    "compile_source",
    "extract_rw",
    "generate_visits1",
    "generate_visits2",
    "extract_value_constraints",
    "rerank_visits1",
    "rerank_visits2",
    "generate_harness",
    "compile_harness",
]


def run_command(
    command: list[str],
    log_path: Path,
    stdout_path: Path | None = None,
) -> tuple[bool, float]:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    start = time.perf_counter()

    with log_path.open(
        "w",
        encoding="utf-8",
        newline="\n",
    ) as log_file:
        if stdout_path is None:
            completed = subprocess.run(
                command,
                cwd=ROOT,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
        else:
            stdout_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with stdout_path.open(
                "w",
                encoding="utf-8",
                newline="\n",
            ) as stdout_file:
                completed = subprocess.run(
                    command,
                    cwd=ROOT,
                    stdout=stdout_file,
                    stderr=log_file,
                    text=True,
                    check=False,
                )

    seconds = time.perf_counter() - start
    return completed.returncode == 0, seconds


def load_paths(
    path: Path,
    contract: str,
) -> list[dict[str, Any]]:
    if not path.is_file():
        return []

    try:
        data = json.loads(
            path.read_text(encoding="utf-8")
        )
    except (
        OSError,
        json.JSONDecodeError,
    ):
        return []

    contract_data = data.get(contract)

    if not isinstance(contract_data, dict):
        return []

    paths = contract_data.get("paths")

    if not isinstance(paths, list):
        return []

    return [
        item
        for item in paths
        if isinstance(item, dict)
    ]


def find_rank(
    paths: list[dict[str, Any]],
    expected: list[str],
) -> int | str:
    for rank, item in enumerate(paths, start=1):
        if item.get("sequence") == expected:
            return rank

    return ""


def top_sequences(
    paths: list[dict[str, Any]],
    limit: int = 5,
) -> str:
    sequences = []

    for rank, item in enumerate(
        paths[:limit],
        start=1,
    ):
        sequence = item.get("sequence", [])

        if not isinstance(sequence, list):
            continue

        score = item.get(
            "value_score",
            item.get("score", ""),
        )

        sequences.append(
            f"{rank}:"
            + " -> ".join(str(x) for x in sequence)
            + f" [score={score}]"
        )

    return " || ".join(sequences)


def write_summary(
    rows: list[dict[str, Any]],
) -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_ROOT / "c0-summary.csv"

    fields = [
        "benchmark",
        "compiler",
        "contract",
        *STAGE_FIELDS,
        "visits1_paths",
        "visits2_paths",
        "full_visits1_paths",
        "full_visits2_paths",
        "expected_rank_visits1",
        "expected_rank_visits2",
        "expected_rank_full_visits1",
        "expected_rank_full_visits2",
        "screening_status",
        "notes",
    ]

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def write_path_report(
    rows: list[dict[str, Any]],
) -> None:
    output_path = OUTPUT_ROOT / "c0-top-paths.csv"

    fields = [
        "benchmark",
        "method",
        "path_count",
        "top_paths",
    ]

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    HARNESS_ROOT.mkdir(parents=True, exist_ok=True)

    summary_rows: list[dict[str, Any]] = []
    path_rows: list[dict[str, Any]] = []

    python_executable = sys.executable

    for case in CASES:
        benchmark = case["benchmark"]
        compiler = case["compiler"]
        source = ROOT / case["source"]
        contract = case["contract"]
        harness_name = case["harness"]
        expected = case["expected"]

        print()
        print("=" * 60)
        print(f"Screening: {benchmark}")
        print(f"Compiler : {compiler}")
        print(f"Contract : {contract}")
        print("=" * 60)

        work = OUTPUT_ROOT / benchmark
        logs = work / "logs"

        work.mkdir(parents=True, exist_ok=True)
        logs.mkdir(parents=True, exist_ok=True)

        rw_json = work / "rw.json"
        visits1_json = work / "property-visits1.json"
        visits2_json = work / "property-visits2.json"
        constraints_json = work / "value-constraints.json"
        full1_json = work / "full-visits1.json"
        full2_json = work / "full-visits2.json"

        harness_file = (
            HARNESS_ROOT
            / f"{harness_name}.sol"
        )

        row: dict[str, Any] = {
            "benchmark": benchmark,
            "compiler": compiler,
            "contract": contract,
        }

        notes: list[str] = []

        if not source.is_file():
            for field in STAGE_FIELDS:
                row[field] = "SKIP"

            row["screening_status"] = "FAIL"
            row["notes"] = f"Source not found: {source}"
            summary_rows.append(row)
            write_summary(summary_rows)
            continue

        ok, _ = run_command(
            [
                "solc-select",
                "use",
                compiler,
            ],
            logs / "switch-compiler.log",
        )
        row["switch_compiler"] = "PASS" if ok else "FAIL"

        if not ok:
            notes.append(
                f"Could not activate solc {compiler}"
            )

        ok_compile = False

        if ok:
            ok_compile, _ = run_command(
                [
                    "solc",
                    "--bin",
                    str(source),
                ],
                logs / "compile-source.log",
            )

        row["compile_source"] = (
            "PASS" if ok_compile else "FAIL"
        )

        if not ok_compile:
            notes.append("Source compilation failed")

        ok_rw = False

        if ok_compile:
            ok_rw, _ = run_command(
                [
                    python_executable,
                    str(ROOT / "analyzer/extract_rw.py"),
                    str(source),
                ],
                logs / "extract-rw.log",
                rw_json,
            )

        row["extract_rw"] = "PASS" if ok_rw else "FAIL"

        if not ok_rw:
            notes.append("Read/write extraction failed")

        ok_v1 = False
        ok_v2 = False

        if ok_rw:
            ok_v1, _ = run_command(
                [
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
                    "1",
                ],
                logs / "generate-visits1.log",
                visits1_json,
            )

            ok_v2, _ = run_command(
                [
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
                logs / "generate-visits2.log",
                visits2_json,
            )

        row["generate_visits1"] = (
            "PASS" if ok_v1 else "FAIL"
        )
        row["generate_visits2"] = (
            "PASS" if ok_v2 else "FAIL"
        )

        ok_constraints = False

        if ok_compile:
            ok_constraints, _ = run_command(
                [
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
                logs / "extract-value-constraints.log",
                constraints_json,
            )

        row["extract_value_constraints"] = (
            "PASS" if ok_constraints else "FAIL"
        )

        ok_full1 = False
        ok_full2 = False

        if ok_v1 and ok_constraints:
            ok_full1, _ = run_command(
                [
                    python_executable,
                    str(
                        ROOT
                        / "analyzer/"
                        "generate_value_guided_sequences.py"
                    ),
                    str(visits1_json),
                    str(constraints_json),
                    "--contract",
                    contract,
                ],
                logs / "rerank-visits1.log",
                full1_json,
            )

        if ok_v2 and ok_constraints:
            ok_full2, _ = run_command(
                [
                    python_executable,
                    str(
                        ROOT
                        / "analyzer/"
                        "generate_value_guided_sequences.py"
                    ),
                    str(visits2_json),
                    str(constraints_json),
                    "--contract",
                    contract,
                ],
                logs / "rerank-visits2.log",
                full2_json,
            )

        row["rerank_visits1"] = (
            "PASS" if ok_full1 else "FAIL"
        )
        row["rerank_visits2"] = (
            "PASS" if ok_full2 else "FAIL"
        )

        visits1_paths = load_paths(
            visits1_json,
            contract,
        )
        visits2_paths = load_paths(
            visits2_json,
            contract,
        )
        full1_paths = load_paths(
            full1_json,
            contract,
        )
        full2_paths = load_paths(
            full2_json,
            contract,
        )

        row["visits1_paths"] = len(visits1_paths)
        row["visits2_paths"] = len(visits2_paths)
        row["full_visits1_paths"] = len(full1_paths)
        row["full_visits2_paths"] = len(full2_paths)

        rank_v1 = find_rank(
            visits1_paths,
            expected,
        )
        rank_v2 = find_rank(
            visits2_paths,
            expected,
        )
        rank_full1 = find_rank(
            full1_paths,
            expected,
        )
        rank_full2 = find_rank(
            full2_paths,
            expected,
        )

        row["expected_rank_visits1"] = rank_v1
        row["expected_rank_visits2"] = rank_v2
        row["expected_rank_full_visits1"] = rank_full1
        row["expected_rank_full_visits2"] = rank_full2

        path_rows.extend(
            [
                {
                    "benchmark": benchmark,
                    "method": "property-visits1",
                    "path_count": len(visits1_paths),
                    "top_paths": top_sequences(visits1_paths),
                },
                {
                    "benchmark": benchmark,
                    "method": "property-visits2",
                    "path_count": len(visits2_paths),
                    "top_paths": top_sequences(visits2_paths),
                },
                {
                    "benchmark": benchmark,
                    "method": "full-visits1",
                    "path_count": len(full1_paths),
                    "top_paths": top_sequences(full1_paths),
                },
                {
                    "benchmark": benchmark,
                    "method": "full-visits2",
                    "path_count": len(full2_paths),
                    "top_paths": top_sequences(full2_paths),
                },
            ]
        )

        ok_harness = False
        ok_harness_compile = False

        if ok_full2 and full2_paths:
            ok_harness, _ = run_command(
                [
                    python_executable,
                    str(
                        ROOT
                        / "analyzer/"
                        "generate_harness_from_paths.py"
                    ),
                    "--source",
                    str(source),
                    "--sequences",
                    str(full2_json),
                    "--target-contract",
                    contract,
                    "--harness-contract",
                    harness_name,
                    "--output",
                    str(harness_file),
                    "--prefix",
                    "full",
                    "--top-k",
                    "1",
                    "--solidity-pragma",
                    compiler,
                ],
                logs / "generate-harness.log",
            )

        row["generate_harness"] = (
            "PASS" if ok_harness else "FAIL"
        )

        if ok_harness:
            ok_harness_compile, _ = run_command(
                [
                    "solc",
                    "--allow-paths",
                    str(ROOT / "contracts"),
                    "--bin",
                    str(harness_file),
                ],
                logs / "compile-harness.log",
            )

        row["compile_harness"] = (
            "PASS" if ok_harness_compile else "FAIL"
        )

        if not ok_harness:
            notes.append(
                "Harness generation failed"
            )

        if ok_harness and not ok_harness_compile:
            notes.append(
                "Harness compilation failed"
            )

        required_stages_passed = all(
            row.get(field) == "PASS"
            for field in (
                "switch_compiler",
                "compile_source",
                "extract_rw",
                "generate_visits2",
                "extract_value_constraints",
                "rerank_visits2",
                "generate_harness",
                "compile_harness",
            )
        )

        expected_full_present = rank_full2 != ""

        repeat_condition_passed = True

        if case["requires_repeat"]:
            repeat_condition_passed = (
                rank_v1 == ""
                and rank_v2 != ""
                and rank_full1 == ""
                and rank_full2 != ""
            )

            if rank_v1 != "":
                notes.append(
                    "Expected repeated path unexpectedly "
                    "appeared with Visits=1"
                )

            if rank_v2 == "":
                notes.append(
                    "Expected repeated path absent "
                    "with Visits=2"
                )
        elif rank_full2 == "":
            notes.append(
                "Expected path absent from Full Visits=2"
            )

        if (
            required_stages_passed
            and expected_full_present
            and repeat_condition_passed
        ):
            row["screening_status"] = "PASS"
        else:
            row["screening_status"] = "FAIL"

        if row["screening_status"] == "PASS":
            notes.append(
                "Compatibility screening passed"
            )
        elif not notes:
            notes.append(
                "Compatibility screening failed"
            )

        row["notes"] = " | ".join(notes)

        summary_rows.append(row)
        write_summary(summary_rows)
        write_path_report(path_rows)

        print(
            f"Result: {row['screening_status']}"
        )
        print(
            f"Full Visits=2 expected rank: {rank_full2}"
        )

    run_command(
        [
            "solc-select",
            "use",
            "0.8.20",
        ],
        OUTPUT_ROOT / "restore-solc-0.8.20.log",
    )

    write_summary(summary_rows)
    write_path_report(path_rows)

    print()
    print(
        "Saved summary: "
        "results/public-benchmarks/c0/c0-summary.csv"
    )
    print(
        "Saved paths: "
        "results/public-benchmarks/c0/c0-top-paths.csv"
    )


if __name__ == "__main__":
    main()
