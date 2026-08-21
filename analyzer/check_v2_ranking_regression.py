#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


V2_DIRECTORY = Path(__file__).resolve().parent / "v2"
sys.path.insert(0, str(V2_DIRECTORY))

from rank_violation_paths import (  # noqa: E402
    can_dominate_repeated_path,
    conflicts_of,
    matches_of,
)


EXPECTED_TOP_ONE = {
    "noisy-four-step": [
        "register()",
        "deposit()",
        "approve()",
        "withdraw(uint256)",
    ],
    "reset-example": [
        "begin()",
        "authorize()",
        "commit()",
        "execute(uint256)",
    ],
    "branch-value": [
        "prepareGood()",
        "unlock()",
        "activate()",
        "trigger(uint256)",
    ],
    "repeated-call": [
        "deposit()",
        "deposit()",
        "unlock()",
        "withdraw(uint256)",
    ],
    "multi-property-a": [
        "prepare()",
        "authorize()",
        "execute(uint256,uint256)",
    ],
    "multi-property-b": [
        "prepare()",
        "authorize()",
        "execute(uint256,uint256)",
    ],
    "echidna-multi": [
        "f(uint256)",
        "g(uint256)",
        "h(uint256)",
    ],
    "echidna-flags": [
        "set0(int256)",
        "set1(int256)",
    ],
    "exercise2-access-control": [
        "Owner()",
        "resume()",
    ],
    "smartbugs-onefunc": [
        "run(uint256)",
        "run(uint256)",
    ],
}


EXPECTED_ALTERNATIVES = {
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


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check V2 ranking regression artifacts."
    )
    parser.add_argument(
        "--result-root",
        type=Path,
        default=Path("results/v2/regression"),
    )
    return parser.parse_args()


def load_ranked(
    result_root: Path,
    case_name: str,
) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
    path = result_root / f"{case_name}-ranked.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    containers = [
        (name, value)
        for name, value in data.items()
        if isinstance(value, dict)
        and isinstance(value.get("paths"), list)
    ]

    assert len(containers) == 1, (
        f"{case_name}: expected one contract path container, "
        f"found {len(containers)}"
    )

    contract_name, container = containers[0]
    paths = container["paths"]
    assert paths, f"{case_name}: no ranked paths"

    return contract_name, container, paths


def check_field_compatibility() -> None:
    assert matches_of({"value_matches": 3}) == 3
    assert conflicts_of({"value_conflicts": 2}) == 2


def check_conservative_dominance() -> None:
    candidate = {
        "sequence": ["setup()", "run()"],
        "violation_class": "MAY_VIOLATE",
        "value_matches": 1,
        "value_conflicts": 0,
        "terminal_state": {
            "count": {"kind": "exact", "value": 1}
        },
    }
    repeated = {
        "sequence": ["setup()", "setup()", "run()"],
        "violation_class": "MAY_VIOLATE",
        "value_matches": 1,
        "value_conflicts": 0,
        "terminal_state": {
            "count": {"kind": "exact", "value": 2}
        },
    }

    assert not can_dominate_repeated_path(candidate, repeated), (
        "A path with a different terminal state must not dominate "
        "a repeated path."
    )

    repeated["terminal_state"] = candidate["terminal_state"]
    assert can_dominate_repeated_path(candidate, repeated), (
        "A state-equivalent, no-worse path should dominate a "
        "redundant repeated path."
    )


def main() -> None:
    arguments = parse_arguments()
    result_root = arguments.result_root

    check_field_compatibility()
    check_conservative_dominance()

    rows: list[dict[str, Any]] = []

    for case_name, expected in EXPECTED_TOP_ONE.items():
        contract, container, paths = load_ranked(
            result_root,
            case_name,
        )
        top = paths[0]

        assert top["sequence"] == expected, (
            f"{case_name}: unexpected Top-1 path\n"
            f"Expected: {expected}\n"
            f"Actual:   {top['sequence']}"
        )

        if case_name in {"repeated-call", "smartbugs-onefunc"}:
            assert top.get("dominated_repeat") == 0, (
                f"{case_name}: necessary repetition was marked "
                "as dominated"
            )

        if case_name == "exercise2-access-control":
            assert top.get("violation_class") == "MUST_VIOLATE"
            assert paths[1].get("violation_class") == "CANNOT_VIOLATE"

        rows.append(
            {
                "case": case_name,
                "contract": contract,
                "property": container.get("v2_property", ""),
                "path_count": len(paths),
                "expected_rank": 1,
                "expected_sequence": " -> ".join(expected),
                "violation_class": top.get("violation_class", ""),
                "dominated_repeat": top.get("dominated_repeat", 0),
                "status": "PASS",
            }
        )

    contract, container, paths = load_ranked(
        result_root,
        "alternative-path",
    )
    actual_alternatives = {
        tuple(item["sequence"])
        for item in paths[:2]
    }
    assert actual_alternatives == EXPECTED_ALTERNATIVES, (
        "alternative-path: Top-2 does not preserve both valid routes"
    )
    rows.append(
        {
            "case": "alternative-path",
            "contract": contract,
            "property": container.get("v2_property", ""),
            "path_count": len(paths),
            "expected_rank": "1-2",
            "expected_sequence": " | ".join(
                " -> ".join(sequence)
                for sequence in sorted(EXPECTED_ALTERNATIVES)
            ),
            "violation_class": paths[0].get("violation_class", ""),
            "dominated_repeat": 0,
            "status": "PASS",
        }
    )

    contract, container, paths = load_ranked(
        result_root,
        "smartbugs-multifunc",
    )
    top_sequence = paths[0]["sequence"]
    assert top_sequence[0] == "init()", (
        "smartbugs-multifunc: Top-1 must initialize before run"
    )
    assert top_sequence[-1] == "run(uint256)"
    assert ["init()", "run(uint256)"] in [
        item["sequence"]
        for item in paths
    ], "smartbugs-multifunc: minimal valid path was removed"
    rows.append(
        {
            "case": "smartbugs-multifunc",
            "contract": contract,
            "property": container.get("v2_property", ""),
            "path_count": len(paths),
            "expected_rank": 1,
            "expected_sequence": " -> ".join(top_sequence),
            "violation_class": paths[0].get("violation_class", ""),
            "dominated_repeat": paths[0].get("dominated_repeat", 0),
            "status": "PASS",
        }
    )

    output_path = result_root / "ranking-regression-summary.csv"
    fieldnames = [
        "case",
        "contract",
        "property",
        "path_count",
        "expected_rank",
        "expected_sequence",
        "violation_class",
        "dominated_repeat",
        "status",
    ]

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"V2 ranking regression passed: {len(rows)} checks")
    print(f"Summary: {output_path}")


if __name__ == "__main__":
    main()
