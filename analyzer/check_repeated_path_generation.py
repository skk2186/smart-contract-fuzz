#!/usr/bin/env python3

import json
from pathlib import Path


EXPECTED = [
    "deposit()",
    "deposit()",
    "unlock()",
    "withdraw(uint256)",
]


def load_paths(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["RepeatedCallExample"]["paths"]


visits_1 = load_paths(
    Path(
        "results/repeated-call/"
        "repeat-v1-property-sequences.json"
    )
)

visits_2 = load_paths(
    Path(
        "results/repeated-call/"
        "repeat-v2-property-sequences.json"
    )
)

v1_matches = [
    path
    for path in visits_1
    if path["sequence"] == EXPECTED
]

v2_matches = [
    path
    for path in visits_2
    if path["sequence"] == EXPECTED
]

assert not v1_matches, (
    "Visits=1 unexpectedly generated the repeated path"
)

assert len(v2_matches) == 1, (
    "Visits=2 did not generate exactly one expected path"
)

repeated_path = v2_matches[0]

assert repeated_path["has_repetition"] is True

assert (
    repeated_path["repeated_functions"].get(
        "deposit()"
    )
    == 2
)

print("Visits=1: repeated path absent — PASS")
print("Visits=2: repeated path present — PASS")
print(
    "Generated sequence: "
    + " -> ".join(repeated_path["sequence"])
)
print(
    f"Path score: {repeated_path['score']}"
)
