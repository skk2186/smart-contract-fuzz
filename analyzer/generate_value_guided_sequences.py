#!/usr/bin/env python3

"""
Re-rank property-relevant transaction sequences using lightweight
state-value constraint matching.

Inputs:
    1. property-sequences.json
    2. value-constraints.json

For each adjacent function pair f -> g:
    - MATCH:
        f writes x = c and g requires a condition satisfied by c
    - CONFLICT:
        f writes x = c and g requires a condition not satisfied by c
    - UNKNOWN:
        f writes x symbolically or the value cannot be evaluated

Default scoring:
    value_score
        = property_score
        + match_reward * match_count
        - conflict_penalty * conflict_count
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any


SUPPORTED_OPERATORS = {
    "==",
    "!=",
    ">",
    ">=",
    "<",
    "<=",
}


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"JSON file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")

    return data


def normalize_number(value: float) -> int | float:
    if isinstance(value, float) and value.is_integer():
        return int(value)

    return value


def compare_literals(
    written: dict[str, Any],
    operator: str,
    required: dict[str, Any],
) -> bool | None:
    """
    Return:
        True  -> written value satisfies requirement
        False -> written value conflicts with requirement
        None  -> unsupported or incompatible comparison
    """

    if operator not in SUPPORTED_OPERATORS:
        return None

    written_kind = written.get("kind")
    required_kind = required.get("kind")

    if written_kind != required_kind:
        return None

    left = written.get("value")
    right = required.get("value")

    if operator == "==":
        return left == right

    if operator == "!=":
        return left != right

    # Ordering comparisons are currently limited to integer literals.
    if written_kind != "int":
        return None

    if not isinstance(left, int) or isinstance(left, bool):
        return None

    if not isinstance(right, int) or isinstance(right, bool):
        return None

    if operator == ">":
        return left > right

    if operator == ">=":
        return left >= right

    if operator == "<":
        return left < right

    if operator == "<=":
        return left <= right

    return None


def unsupported_write_variables(
    function_record: dict[str, Any],
) -> set[str]:
    variables: set[str] = set()

    for item in function_record.get("unsupported_writes", []):
        variable = item.get("variable")

        if isinstance(variable, str):
            variables.add(variable)

    return variables


def classify_requirement(
    source_record: dict[str, Any],
    requirement: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    """
    Classify whether a source function's write satisfies one requirement.

    Possible statuses:
        match
        conflict
        unknown
        unrelated
    """

    variable = requirement.get("variable")
    operator = requirement.get("operator")
    required_value = requirement.get("value")

    detail: dict[str, Any] = {
        "variable": variable,
        "operator": operator,
        "required_value": required_value,
    }

    if (
        not isinstance(variable, str)
        or not isinstance(operator, str)
        or not isinstance(required_value, dict)
    ):
        detail["reason"] = "malformed requirement"
        return "unknown", detail

    constant_writes = source_record.get(
        "constant_writes",
        {},
    )

    written_values = constant_writes.get(variable, [])

    if written_values:
        outcomes = [
            compare_literals(
                written=written_value,
                operator=operator,
                required=required_value,
            )
            for written_value in written_values
        ]

        detail["written_values"] = written_values
        detail["outcomes"] = outcomes

        if outcomes and all(result is True for result in outcomes):
            detail["reason"] = "all constant writes satisfy requirement"
            return "match", detail

        if outcomes and all(result is False for result in outcomes):
            detail["reason"] = "all constant writes violate requirement"
            return "conflict", detail

        detail["reason"] = (
            "multiple or unsupported write outcomes prevent "
            "a definite decision"
        )
        return "unknown", detail

    if variable in unsupported_write_variables(source_record):
        detail["reason"] = "source writes variable symbolically"
        return "unknown", detail

    detail["reason"] = "source does not write required variable"
    return "unrelated", detail


def analyze_edge(
    source_function: str,
    target_function: str,
    functions: dict[str, Any],
) -> dict[str, Any]:
    source_record = functions.get(source_function, {})
    target_record = functions.get(target_function, {})

    details: list[dict[str, Any]] = []

    match_count = 0
    conflict_count = 0
    unknown_count = 0

    for requirement in target_record.get("requirements", []):
        status, detail = classify_requirement(
            source_record,
            requirement,
        )

        detail["status"] = status
        details.append(detail)

        if status == "match":
            match_count += 1
        elif status == "conflict":
            conflict_count += 1
        elif status == "unknown":
            unknown_count += 1

    if conflict_count > 0:
        edge_status = "conflict"
    elif match_count > 0:
        edge_status = "match"
    elif unknown_count > 0:
        edge_status = "unknown"
    else:
        edge_status = "not_applicable"

    return {
        "source": source_function,
        "target": target_function,
        "status": edge_status,
        "match_count": match_count,
        "conflict_count": conflict_count,
        "unknown_count": unknown_count,
        "details": details,
    }


def score_path(
    path: dict[str, Any],
    functions: dict[str, Any],
    match_reward: float,
    conflict_penalty: float,
) -> dict[str, Any]:
    result = copy.deepcopy(path)

    sequence = result.get("sequence")

    if not isinstance(sequence, list):
        raise ValueError("Each path must contain a sequence list")

    property_score = result.get("score", 0)

    if not isinstance(property_score, (int, float)):
        property_score = 0

    edges: list[dict[str, Any]] = []

    total_matches = 0
    total_conflicts = 0
    total_unknowns = 0

    for index in range(len(sequence) - 1):
        edge = analyze_edge(
            source_function=sequence[index],
            target_function=sequence[index + 1],
            functions=functions,
        )

        edges.append(edge)

        total_matches += edge["match_count"]
        total_conflicts += edge["conflict_count"]
        total_unknowns += edge["unknown_count"]

    value_adjustment = (
        match_reward * total_matches
        - conflict_penalty * total_conflicts
    )

    value_score = property_score + value_adjustment

    # Preserve the old score explicitly and expose the new score through
    # the standard "score" field so existing Harness generation scripts
    # can continue consuming the JSON.
    result["property_score"] = property_score
    result["value_adjustment"] = normalize_number(value_adjustment)
    result["value_score"] = normalize_number(value_score)
    result["score"] = normalize_number(value_score)

    result["value_matches"] = total_matches
    result["value_conflicts"] = total_conflicts
    result["value_unknowns"] = total_unknowns
    result["value_edges"] = edges

    return result


def sort_key(path: dict[str, Any]) -> tuple[Any, ...]:
    sequence = path.get("sequence", [])

    return (
        path.get("value_score", 0),
        path.get("value_matches", 0),
        -path.get("value_conflicts", 0),
        path.get("property_score", 0),
        -path.get("value_unknowns", 0),
        len(sequence),
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Re-rank property-relevant transaction sequences using "
            "lightweight state-value constraint matching."
        )
    )

    parser.add_argument(
        "property_sequences",
        type=Path,
        help="Property-guided sequence JSON file.",
    )

    parser.add_argument(
        "value_constraints",
        type=Path,
        help="Value-constraint JSON file.",
    )

    parser.add_argument(
        "--contract",
        required=True,
        help="Target contract name.",
    )

    parser.add_argument(
        "--match-reward",
        type=float,
        default=4.0,
        help="Score added for each definite value match.",
    )

    parser.add_argument(
        "--conflict-penalty",
        type=float,
        default=4.0,
        help="Score subtracted for each definite value conflict.",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=None,
        help="Optionally keep only the top K re-ranked paths.",
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    if arguments.top_k is not None and arguments.top_k <= 0:
        print(
            "Error: --top-k must be greater than zero",
            file=sys.stderr,
        )
        raise SystemExit(1)

    try:
        property_data = load_json(arguments.property_sequences)
        constraint_data = load_json(arguments.value_constraints)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from error

    contract_name = arguments.contract

    if contract_name not in property_data:
        print(
            f"Error: contract '{contract_name}' not found in "
            f"{arguments.property_sequences}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    if contract_name not in constraint_data:
        print(
            f"Error: contract '{contract_name}' not found in "
            f"{arguments.value_constraints}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    contract_sequences = copy.deepcopy(
        property_data[contract_name]
    )

    paths = contract_sequences.get("paths")

    if not isinstance(paths, list):
        print(
            "Error: property sequence JSON must contain a paths list",
            file=sys.stderr,
        )
        raise SystemExit(1)

    functions = constraint_data[contract_name].get(
        "functions",
        {},
    )

    scored_paths = [
        score_path(
            path=path,
            functions=functions,
            match_reward=arguments.match_reward,
            conflict_penalty=arguments.conflict_penalty,
        )
        for path in paths
    ]

    scored_paths.sort(
        key=sort_key,
        reverse=True,
    )

    if arguments.top_k is not None:
        scored_paths = scored_paths[:arguments.top_k]

    for rank, path in enumerate(scored_paths, start=1):
        path["value_rank"] = rank

    contract_sequences["paths"] = scored_paths
    contract_sequences["value_scoring"] = {
        "match_reward": arguments.match_reward,
        "conflict_penalty": arguments.conflict_penalty,
        "unknown_adjustment": 0,
    }

    result = {
        contract_name: contract_sequences,
    }

    json.dump(
        result,
        sys.stdout,
        indent=2,
        ensure_ascii=False,
    )
    print()


if __name__ == "__main__":
    main()
