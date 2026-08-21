#!/usr/bin/env python3

import json
from pathlib import Path


CASES = [
    {
        "benchmark": "noisy-four-step",
        "contract": "NoisyFourStepExample",
        "expected": [
            "register()",
            "deposit()",
            "approve()",
            "withdraw(uint256)",
        ],
    },
    {
        "benchmark": "reset-example",
        "contract": "ResetExample",
        "expected": [
            "begin()",
            "authorize()",
            "commit()",
            "execute(uint256)",
        ],
    },
    {
        "benchmark": "branch-value",
        "contract": "BranchValueExample",
        "expected": [
            "prepareGood()",
            "unlock()",
            "activate()",
            "trigger(uint256)",
        ],
    },
    {
        "benchmark": "repeated-call",
        "contract": "RepeatedCallExample",
        "expected": [
            "deposit()",
            "deposit()",
            "unlock()",
            "withdraw(uint256)",
        ],
    },
]


all_passed = True

for case in CASES:
    path = (
        Path("results/formal/preparation")
        / case["benchmark"]
        / "full-sequences.json"
    )

    data = json.loads(path.read_text(encoding="utf-8"))
    paths = data[case["contract"]]["paths"]

    if not paths:
        print(f"{case['benchmark']}: FAIL — no paths")
        all_passed = False
        continue

    actual = paths[0]["sequence"]
    passed = actual == case["expected"]

    print(
        f"{case['benchmark']}: "
        f"{'PASS' if passed else 'FAIL'}"
    )
    print("  Actual  : " + " -> ".join(actual))
    print("  Expected: " + " -> ".join(case["expected"]))

    if not passed:
        print("  Top five paths:")

        for rank, item in enumerate(paths[:5], start=1):
            print(
                f"    {rank}. "
                + " -> ".join(item["sequence"])
                + f" | score={item.get('value_score')}"
            )

        all_passed = False


if not all_passed:
    raise SystemExit(
        "Full-v1.0 Top-1 preflight failed."
    )

print("All Full-v1.0 Top-1 checks passed.")
