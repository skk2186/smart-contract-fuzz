#!/usr/bin/env python3

"""Validate the deterministic V1 semantic differential regression log."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


EXPECTED_PROPERTIES = (
    "echidna_same_caller_trace_is_equivalent",
    "echidna_caller_alternation_changes_behavior",
    "echidna_rollback_boundary_changes_behavior",
)

PROFILES = {
    "semantic-model": EXPECTED_PROPERTIES,
    "formal-replay": (
        "echidna_branch_value_trace_agrees",
        "echidna_noisy_trace_agrees",
        "echidna_repeated_call_trace_agrees",
        "echidna_reset_trace_agrees",
        "echidna_alternative_path_trace_agrees",
        "echidna_multi_property_trace_agrees",
    ),
    "public-v8-replay": (
        "echidna_public_multi_trace_agrees",
        "echidna_public_flags_trace_agrees",
        "echidna_exercise2_same_caller_trace_agrees",
    ),
    "public-v4-replay": (
        "echidna_smartbugs_multifunc_trace_agrees",
        "echidna_smartbugs_onefunc_trace_agrees",
    ),
}


def validate_log(
    text: str,
    expected_properties: tuple[str, ...] = EXPECTED_PROPERTIES,
) -> dict[str, object]:
    missing = [name for name in expected_properties if name not in text]
    failed = [
        name
        for name in expected_properties
        if f"{name}: failed" in text.lower()
        or f"{name}: falsified" in text.lower()
    ]
    passed = [
        name
        for name in expected_properties
        if f"{name}: passing" in text.lower()
        or f"{name}: passed" in text.lower()
    ]

    if missing:
        raise ValueError(
            "Differential log is missing expected properties: "
            + ", ".join(missing)
        )
    if failed:
        raise ValueError(
            "Differential properties failed: " + ", ".join(failed)
        )
    if len(passed) != len(expected_properties):
        raise ValueError(
            "Could not confirm a passing result for every property"
        )

    return {
        "schema_version": 1,
        "expected_properties": list(expected_properties),
        "passed_properties": passed,
        "all_passed": True,
        "scope": "local semantic regression; not a vulnerability benchmark or full equivalence proof",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--profile",
        choices=sorted(PROFILES),
        default="semantic-model",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    text = args.log.read_text(encoding="utf-8", errors="strict")
    expected_properties = PROFILES[args.profile]
    result = validate_log(text, expected_properties)
    result["profile"] = args.profile
    if args.profile == "semantic-model":
        result["interpretation"] = {
            "same_caller": "same-caller independent calls and wrapper calls agree",
            "caller_alternation": "alternating callers can diverge from a fixed-caller wrapper",
            "rollback_boundary": "a caught later failure preserves an earlier independent call but rolls back an atomic wrapper",
        }
    else:
        result["interpretation"] = {
            "trace_replay": "the fixed known successful trace produced the expected property-relevant final state on direct and generated-Harness paths"
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Validated properties: {len(expected_properties)}")


if __name__ == "__main__":
    main()
