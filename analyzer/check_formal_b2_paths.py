#!/usr/bin/env python3

import json
from pathlib import Path


def load_paths(path: str, contract: str):
    data = json.loads(
        Path(path).read_text(encoding="utf-8")
    )
    return data[contract]["paths"]


alternative_paths = load_paths(
    "results/formal-b2/preparation/"
    "alternative-path/full-sequences.json",
    "AlternativePathExample",
)

expected_alternatives = {
    (
        "openRouteA()",
        "confirm()",
        "execute(uint256)",
    ),
    (
        "openRouteB()",
        "confirm()",
        "execute(uint256)",
    ),
}

actual_top_two = {
    tuple(path["sequence"])
    for path in alternative_paths[:2]
}

assert actual_top_two == expected_alternatives, (
    "AlternativePath Top-2 does not contain both valid paths.\n"
    f"Actual Top-2: {actual_top_two}"
)

for path in alternative_paths[:2]:
    assert path.get("value_conflicts", 0) == 0

multi_paths = load_paths(
    "results/formal-b2/preparation/"
    "multi-property/full-sequences.json",
    "MultiPropertyExample",
)

expected_multi = [
    "prepare()",
    "authorize()",
    "execute(uint256,uint256)",
]

assert multi_paths, "MultiProperty generated no paths"

assert multi_paths[0]["sequence"] == expected_multi, (
    "MultiProperty correct path is not ranked first.\n"
    f"Actual: {multi_paths[0]['sequence']}"
)

print("AlternativePath Top-2 valid paths:")
for rank, path in enumerate(alternative_paths[:2], start=1):
    print(
        f"{rank}. "
        + " -> ".join(path["sequence"])
        + f" | score={path.get('value_score')}"
    )

print()
print(
    "MultiProperty Top-1: "
    + " -> ".join(multi_paths[0]["sequence"])
)
print("Formal B-2 path checks passed.")
