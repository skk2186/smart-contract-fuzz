#!/usr/bin/env python3

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CASES = [
    {
        "benchmark": "noisy-four-step",
        "contract": "NoisyFourStepExample",
        "correct": [
            "register()",
            "deposit()",
            "approve()",
            "withdraw(uint256)",
        ],
    },
    {
        "benchmark": "reset-example",
        "contract": "ResetExample",
        "correct": [
            "begin()",
            "authorize()",
            "commit()",
            "execute(uint256)",
        ],
    },
    {
        "benchmark": "branch-value",
        "contract": "BranchValueExample",
        "correct": [
            "prepareGood()",
            "unlock()",
            "activate()",
            "trigger(uint256)",
        ],
    },
    {
        "benchmark": "repeated-call",
        "contract": "RepeatedCallExample",
        "correct": [
            "deposit()",
            "deposit()",
            "unlock()",
            "withdraw(uint256)",
        ],
    },
]

METHODS = [
    ("dependency", "dependency.json", "score"),
    ("property", "property.json", "score"),
    ("repeat", "repeat-property.json", "score"),
    ("full", "full.json", "value_score"),
]


def load_paths(path: Path, contract: str):
    data = json.loads(path.read_text(encoding="utf-8"))
    return data[contract]["paths"]


def analyze_rank(paths, expected, score_key):
    correct_index = None
    correct_path = None

    for index, path in enumerate(paths):
        if path.get("sequence") == expected:
            correct_index = index + 1
            correct_path = path
            break

    if correct_path is None:
        return {
            "display_rank": "",
            "correct_score": "",
            "higher_score_paths": "",
            "equal_score_paths": "",
            "best_tied_rank": "",
            "worst_tied_rank": "",
        }

    score = correct_path.get(score_key)

    if score is None:
        score = correct_path.get("score", 0)

    higher = 0
    equal = 0

    for path in paths:
        path_score = path.get(score_key)

        if path_score is None:
            path_score = path.get("score", 0)

        if path_score > score:
            higher += 1
        elif path_score == score:
            equal += 1

    return {
        "display_rank": correct_index,
        "correct_score": score,
        "higher_score_paths": higher,
        "equal_score_paths": equal,
        "best_tied_rank": higher + 1,
        "worst_tied_rank": higher + equal,
    }


rows = []

for case in CASES:
    directory = (
        ROOT
        / "results/formal/candidates"
        / case["benchmark"]
    )

    for method, filename, score_key in METHODS:
        path = directory / filename

        if not path.is_file():
            continue

        paths = load_paths(path, case["contract"])
        rank = analyze_rank(
            paths,
            case["correct"],
            score_key,
        )

        rows.append(
            {
                "benchmark": case["benchmark"],
                "method": method,
                **rank,
            }
        )

output = (
    ROOT
    / "results/formal/"
    "formal-tie-aware-ranking.csv"
)

fieldnames = [
    "benchmark",
    "method",
    "display_rank",
    "correct_score",
    "higher_score_paths",
    "equal_score_paths",
    "best_tied_rank",
    "worst_tied_rank",
]

with output.open(
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

print(f"Saved to {output}")
