#!/usr/bin/env python3

import json
from pathlib import Path


CASES = [
    {
        "name": "original",
        "path": Path("results/branch-value/value-sequences.json"),
        "contract": "BranchValueExample",
        "correct_start": "prepareGood()",
    },
    {
        "name": "reordered",
        "path": Path(
            "results/branch-value/reordered/value-sequences.json"
        ),
        "contract": "BranchValueExampleReordered",
        "correct_start": "prepareGood()",
    },
    {
        "name": "renamed",
        "path": Path(
            "results/branch-value/renamed/value-sequences.json"
        ),
        "contract": "BranchValueExampleRenamed",
        "correct_start": "zCorrectPrepare()",
    },
]


for case in CASES:
    data = json.loads(
        case["path"].read_text(encoding="utf-8")
    )

    paths = data[case["contract"]]["paths"]

    assert paths, f"{case['name']}: no paths generated"

    first_path = paths[0]
    first_sequence = first_path["sequence"]

    assert first_sequence[0] == case["correct_start"], (
        f"{case['name']}: correct value-writing function "
        f"was not ranked first.\n"
        f"Actual first path: {first_sequence}"
    )

    assert first_path["value_conflicts"] == 0, (
        f"{case['name']}: first path contains a value conflict"
    )

    print(
        f"{case['name']}: PASS | "
        f"score={first_path['value_score']} | "
        f"{' -> '.join(first_sequence)}"
    )

print("Value-guided ranking invariance checks passed.")
