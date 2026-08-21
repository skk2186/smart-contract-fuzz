#!/usr/bin/env python3

import csv
import json
from pathlib import Path


# This is a manually curated semantic allowlist. Candidate generation alone
# is not evidence that a path triggers the property; each entry below is
# backed by audited contract logic or a counterexample in the C-1 run logs.
CASES = [
    {
        "benchmark": "echidna-multi",
        "contract": "C",
        "expected_minimal_path": [
            "f(uint256)",
            "g(uint256)",
            "h(uint256)",
        ],
        "known_triggering_paths": [
            [
                "f(uint256)",
                "g(uint256)",
                "h(uint256)",
            ],
        ],
    },
    {
        "benchmark": "echidna-flags",
        "contract": "PublicEchidnaFlagsTarget",
        "expected_minimal_path": [
            "set0(int256)",
            "set1(int256)",
        ],
        "known_triggering_paths": [
            [
                "set0(int256)",
                "set1(int256)",
            ],
        ],
    },
    {
        "benchmark": "exercise2-access-control",
        "contract": "TestToken",
        "expected_minimal_path": [
            "Owner()",
            "resume()",
        ],
        "known_triggering_paths": [
            [
                "Owner()",
                "resume()",
            ],
        ],
    },
    {
        "benchmark": "smartbugs-multifunc",
        "contract": "SmartBugsMultiFuncEchidna",
        "expected_minimal_path": [
            "init()",
            "run(uint256)",
        ],
        "known_triggering_paths": [
            [
                "init()",
                "run(uint256)",
            ],
            [
                "init()",
                "run(uint256)",
                "run(uint256)",
            ],
        ],
    },
    {
        "benchmark": "smartbugs-onefunc",
        "contract": "SmartBugsOneFuncEchidna",
        "expected_minimal_path": [
            "run(uint256)",
            "run(uint256)",
        ],
        "known_triggering_paths": [
            [
                "run(uint256)",
                "run(uint256)",
            ],
        ],
    },
]


rows = []
all_present = True

for case in CASES:
    path = (
        Path("results/public-benchmarks/c1/preparation")
        / case["benchmark"]
        / "full.json"
    )

    data = json.loads(path.read_text(encoding="utf-8"))
    paths = data[case["contract"]]["paths"]

    expected_minimal_path_rank = ""

    for rank, item in enumerate(paths, start=1):
        if (
            item.get("sequence")
            == case["expected_minimal_path"]
        ):
            expected_minimal_path_rank = rank
            break

    top1 = (
        " -> ".join(paths[0]["sequence"])
        if paths
        else ""
    )

    exact_minimal_path_in_k1 = (
        expected_minimal_path_rank == 1
    )
    exact_minimal_path_in_k5 = (
        isinstance(expected_minimal_path_rank, int)
        and expected_minimal_path_rank <= 5
    )
    k1_sequences = {
        tuple(item.get("sequence", []))
        for item in paths[:1]
    }
    k5_sequences = {
        tuple(item.get("sequence", []))
        for item in paths[:5]
    }
    known_triggering_paths = {
        tuple(sequence)
        for sequence in case["known_triggering_paths"]
    }
    any_known_triggering_path_in_k1 = bool(
        k1_sequences & known_triggering_paths
    )
    any_known_triggering_path_in_k5 = bool(
        k5_sequences & known_triggering_paths
    )

    rows.append(
        {
            "benchmark": case["benchmark"],
            "expected_minimal_path": " -> ".join(
                case["expected_minimal_path"]
            ),
            "expected_minimal_path_rank": (
                expected_minimal_path_rank
            ),
            "exact_minimal_path_in_k1": int(
                exact_minimal_path_in_k1
            ),
            "exact_minimal_path_in_k5": int(
                exact_minimal_path_in_k5
            ),
            "any_known_triggering_path_in_k1": int(
                any_known_triggering_path_in_k1
            ),
            "any_known_triggering_path_in_k5": int(
                any_known_triggering_path_in_k5
            ),
            "top1_sequence": top1,
            "path_count": len(paths),
        }
    )

    if not exact_minimal_path_in_k5:
        all_present = False

    print(
        f"{case['benchmark']}: "
        f"minimal-rank={expected_minimal_path_rank}, "
        f"exact-K1="
        f"{'yes' if exact_minimal_path_in_k1 else 'no'}, "
        f"exact-K5="
        f"{'yes' if exact_minimal_path_in_k5 else 'no'}, "
        f"known-trigger-K1="
        f"{'yes' if any_known_triggering_path_in_k1 else 'no'}, "
        f"known-trigger-K5="
        f"{'yes' if any_known_triggering_path_in_k5 else 'no'}"
    )
    print(f"  Top-1: {top1}")


output = Path(
    "results/public-benchmarks/c1/"
    "c1-path-preflight.csv"
)

with output.open(
    "w",
    encoding="utf-8",
    newline="",
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "benchmark",
            "expected_minimal_path",
            "expected_minimal_path_rank",
            "exact_minimal_path_in_k1",
            "exact_minimal_path_in_k5",
            "any_known_triggering_path_in_k1",
            "any_known_triggering_path_in_k5",
            "top1_sequence",
            "path_count",
        ],
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)


if not all_present:
    raise SystemExit(
        "At least one expected path is absent from Full-K5."
    )

print("All expected public paths are included by Full-K5.")
