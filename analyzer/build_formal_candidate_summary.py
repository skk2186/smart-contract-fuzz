#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

CASES = [
    {
        "benchmark": "noisy-four-step",
        "contract": "NoisyFourStepExample",
        "correct_sequence": [
            "register()",
            "deposit()",
            "approve()",
            "withdraw(uint256)",
        ],
    },
    {
        "benchmark": "reset-example",
        "contract": "ResetExample",
        "correct_sequence": [
            "begin()",
            "authorize()",
            "commit()",
            "execute(uint256)",
        ],
    },
    {
        "benchmark": "branch-value",
        "contract": "BranchValueExample",
        "correct_sequence": [
            "prepareGood()",
            "unlock()",
            "activate()",
            "trigger(uint256)",
        ],
    },
    {
        "benchmark": "repeated-call",
        "contract": "RepeatedCallExample",
        "correct_sequence": [
            "deposit()",
            "deposit()",
            "unlock()",
            "withdraw(uint256)",
        ],
    },
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_paths(
    path: Path,
    contract: str,
) -> list[dict[str, Any]]:
    data = load_json(path)
    return data[contract]["paths"]


def find_rank(
    paths: list[dict[str, Any]],
    expected: list[str],
) -> int | str:
    for rank, item in enumerate(paths, start=1):
        if item.get("sequence") == expected:
            return rank

    return ""


def main() -> None:
    rows: list[dict[str, Any]] = []

    for case in CASES:
        benchmark = case["benchmark"]
        contract = case["contract"]
        expected = case["correct_sequence"]

        directory = (
            ROOT
            / "results/formal/candidates"
            / benchmark
        )

        dependency_paths = get_paths(
            directory / "dependency.json",
            contract,
        )

        property_paths = get_paths(
            directory / "property.json",
            contract,
        )

        repeat_data = load_json(
            directory / "repeat-property.json"
        )

        repeat_contract = repeat_data[contract]
        repeat_paths = repeat_contract["paths"]

        full_paths = get_paths(
            directory / "full.json",
            contract,
        )

        top1_sequence = ""

        if full_paths:
            top1_sequence = " -> ".join(
                full_paths[0]["sequence"]
            )

        rows.append(
            {
                "benchmark": benchmark,
                "dependency_retained_paths": len(
                    dependency_paths
                ),
                "dependency_correct_rank": find_rank(
                    dependency_paths,
                    expected,
                ),
                "property_retained_paths": len(
                    property_paths
                ),
                "property_correct_rank": find_rank(
                    property_paths,
                    expected,
                ),
                "repeat_generated_paths": (
                    repeat_contract.get(
                        "generated_path_count",
                        "",
                    )
                ),
                "repeat_retained_paths": len(
                    repeat_paths
                ),
                "repeat_correct_rank_before_value": find_rank(
                    repeat_paths,
                    expected,
                ),
                "full_retained_paths": len(full_paths),
                "full_correct_rank": find_rank(
                    full_paths,
                    expected,
                ),
                "dfs_expansions": repeat_contract.get(
                    "dfs_expansions",
                    "",
                ),
                "full_top1_sequence": top1_sequence,
            }
        )

    output_path = (
        ROOT
        / "results/formal/"
        "formal-candidate-summary.csv"
    )

    fieldnames = [
        "benchmark",
        "dependency_retained_paths",
        "dependency_correct_rank",
        "property_retained_paths",
        "property_correct_rank",
        "repeat_generated_paths",
        "repeat_retained_paths",
        "repeat_correct_rank_before_value",
        "full_retained_paths",
        "full_correct_rank",
        "dfs_expansions",
        "full_top1_sequence",
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

    print(f"Saved candidate summary to {output_path}")


if __name__ == "__main__":
    main()
