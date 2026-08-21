#!/usr/bin/env python3

"""
Generate property-relevant transaction sequences while allowing bounded
repeated function visits.

Example:

    deposit()
    -> deposit()
    -> unlock()
    -> withdraw(uint256)

The generator performs backward traversal from functions that write
property variables.

An edge f -> g exists when:

    W(f) ∩ R(g) != ∅

Edge score:

    2 * |W(f) ∩ R(g)| + |W(f) ∩ W(g)|

The maximum number of occurrences of one function in a path is controlled
by --max-function-visits.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


READ_KEYS = (
    "reads",
    "read",
    "state_variables_read",
    "variables_read",
)

WRITE_KEYS = (
    "writes",
    "write",
    "state_variables_written",
    "variables_written",
)


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"JSON file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Root JSON value must be an object")

    return data


def normalize_variable(item: Any) -> str | None:
    if isinstance(item, str):
        value = item.strip()
        return value or None

    if isinstance(item, dict):
        for key in (
            "name",
            "full_name",
            "canonical_name",
            "variable",
        ):
            value = item.get(key)

            if isinstance(value, str) and value.strip():
                return value.strip()

    return None


def normalize_variable_collection(value: Any) -> set[str]:
    if value is None:
        return set()

    if isinstance(value, (str, dict)):
        value = [value]

    if not isinstance(value, list):
        return set()

    result: set[str] = set()

    for item in value:
        variable = normalize_variable(item)

        if variable is not None:
            result.add(variable)

    return result


def find_first_field(
    record: dict[str, Any],
    keys: tuple[str, ...],
) -> Any:
    for key in keys:
        if key in record:
            return record[key]

    return None


def looks_like_function_record(value: Any) -> bool:
    if not isinstance(value, dict):
        return False

    keys = set(value)

    return bool(
        keys.intersection(READ_KEYS)
        or keys.intersection(WRITE_KEYS)
    )


def extract_function_map(
    contract_data: Any,
) -> dict[str, dict[str, Any]]:
    if not isinstance(contract_data, dict):
        raise ValueError("Contract data must be an object")

    explicit_functions = contract_data.get("functions")

    if isinstance(explicit_functions, dict):
        return {
            str(name): record
            for name, record in explicit_functions.items()
            if isinstance(record, dict)
        }

    if isinstance(explicit_functions, list):
        result: dict[str, dict[str, Any]] = {}

        for record in explicit_functions:
            if not isinstance(record, dict):
                continue

            name = (
                record.get("full_name")
                or record.get("signature")
                or record.get("name")
            )

            if isinstance(name, str):
                result[name] = record

        return result

    return {
        str(name): record
        for name, record in contract_data.items()
        if looks_like_function_record(record)
    }


def extract_rw(
    function_map: dict[str, dict[str, Any]],
) -> dict[str, dict[str, set[str]]]:
    result: dict[str, dict[str, set[str]]] = {}

    for function_name, record in function_map.items():
        reads = normalize_variable_collection(
            find_first_field(record, READ_KEYS)
        )

        writes = normalize_variable_collection(
            find_first_field(record, WRITE_KEYS)
        )

        result[function_name] = {
            "reads": reads,
            "writes": writes,
        }

    return result


def edge_score(
    source: dict[str, set[str]],
    target: dict[str, set[str]],
) -> tuple[int, set[str], set[str]]:
    write_read = source["writes"].intersection(
        target["reads"]
    )

    write_write = source["writes"].intersection(
        target["writes"]
    )

    score = (
        2 * len(write_read)
        + len(write_write)
    )

    return score, write_read, write_write


def build_predecessors(
    functions: dict[str, dict[str, set[str]]],
    excluded_functions: set[str],
) -> dict[str, list[dict[str, Any]]]:
    candidates = [
        name
        for name in functions
        if name not in excluded_functions
    ]

    predecessors: dict[str, list[dict[str, Any]]] = {
        name: []
        for name in candidates
    }

    for source_name in candidates:
        for target_name in candidates:
            score, write_read, write_write = edge_score(
                functions[source_name],
                functions[target_name],
            )

            # A dependency edge requires at least one write-read relation.
            if not write_read:
                continue

            predecessors[target_name].append(
                {
                    "source": source_name,
                    "target": target_name,
                    "score": score,
                    "write_read_variables": sorted(write_read),
                    "write_write_variables": sorted(write_write),
                }
            )

    for target_name in predecessors:
        predecessors[target_name].sort(
            key=lambda edge: (
                -edge["score"],
                edge["source"],
            )
        )

    return predecessors


def repeated_function_map(
    sequence: list[str],
) -> dict[str, int]:
    counts = Counter(sequence)

    return {
        function_name: count
        for function_name, count in counts.items()
        if count > 1
    }


def generate_paths(
    predecessors: dict[str, list[dict[str, Any]]],
    target_functions: list[str],
    max_path_length: int,
    max_function_visits: int,
    max_expansions: int,
) -> tuple[list[dict[str, Any]], int]:
    generated: dict[tuple[str, ...], dict[str, Any]] = {}
    expansions = 0

    def dfs(
        current_function: str,
        sequence: list[str],
        edges: list[dict[str, Any]],
        visits: Counter[str],
        target_function: str,
    ) -> None:
        nonlocal expansions

        if len(sequence) >= 2:
            sequence_key = tuple(sequence)
            score = sum(edge["score"] for edge in edges)
            repeated = repeated_function_map(sequence)

            generated[sequence_key] = {
                "sequence": list(sequence),
                "score": score,
                "length": len(sequence),
                "target_function": target_function,
                "has_repetition": bool(repeated),
                "repeated_functions": repeated,
                "edges": list(edges),
            }

        if len(sequence) >= max_path_length:
            return

        for edge in predecessors.get(
            current_function,
            [],
        ):
            if expansions >= max_expansions:
                return

            predecessor = edge["source"]

            if visits[predecessor] >= max_function_visits:
                continue

            expansions += 1

            visits[predecessor] += 1

            dfs(
                current_function=predecessor,
                sequence=[predecessor, *sequence],
                edges=[edge, *edges],
                visits=visits,
                target_function=target_function,
            )

            visits[predecessor] -= 1

    for target_function in target_functions:
        visits: Counter[str] = Counter(
            {target_function: 1}
        )

        dfs(
            current_function=target_function,
            sequence=[target_function],
            edges=[],
            visits=visits,
            target_function=target_function,
        )

    paths = list(generated.values())

    paths.sort(
        key=lambda path: (
            -path["score"],
            -path["length"],
            tuple(path["sequence"]),
        )
    )

    return paths, expansions


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate property-relevant transaction sequences with "
            "bounded repeated function visits."
        )
    )

    parser.add_argument(
        "rw_json",
        type=Path,
        help="Read/write relationship JSON file.",
    )

    parser.add_argument(
        "max_path_length",
        type=int,
        help="Maximum number of functions in one path.",
    )

    parser.add_argument(
        "max_paths",
        type=int,
        help="Maximum number of paths retained after ranking.",
    )

    parser.add_argument(
        "--contract",
        required=True,
        help="Target contract name.",
    )

    parser.add_argument(
        "--max-function-visits",
        type=int,
        default=2,
        help=(
            "Maximum number of times one function may occur "
            "in one path."
        ),
    )

    parser.add_argument(
        "--max-expansions",
        type=int,
        default=100000,
        help="Maximum number of DFS expansions.",
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    if arguments.max_path_length < 2:
        print(
            "Error: max_path_length must be at least 2",
            file=sys.stderr,
        )
        raise SystemExit(1)

    if arguments.max_paths <= 0:
        print(
            "Error: max_paths must be greater than zero",
            file=sys.stderr,
        )
        raise SystemExit(1)

    if arguments.max_function_visits <= 0:
        print(
            "Error: max-function-visits must be positive",
            file=sys.stderr,
        )
        raise SystemExit(1)

    try:
        root = load_json(arguments.rw_json)
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
    ) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from error

    contract_name = arguments.contract

    if contract_name not in root:
        print(
            f"Error: contract '{contract_name}' not found",
            file=sys.stderr,
        )
        raise SystemExit(1)

    function_map = extract_function_map(
        root[contract_name]
    )

    functions = extract_rw(function_map)

    if not functions:
        print(
            "Error: no function read/write records found",
            file=sys.stderr,
        )
        raise SystemExit(1)

    property_functions = sorted(
        function_name
        for function_name in functions
        if function_name.startswith("echidna_")
    )

    if not property_functions:
        print(
            "Error: no echidna_ property function found",
            file=sys.stderr,
        )
        raise SystemExit(1)

    property_variables: set[str] = set()

    for property_function in property_functions:
        property_variables.update(
            functions[property_function]["reads"]
        )

    target_functions = sorted(
        function_name
        for function_name, record in functions.items()
        if (
            function_name not in property_functions
            and record["writes"].intersection(
                property_variables
            )
        )
    )

    if not target_functions:
        print(
            "Error: no function writes a property variable",
            file=sys.stderr,
        )
        raise SystemExit(1)

    predecessors = build_predecessors(
        functions=functions,
        excluded_functions=set(property_functions),
    )

    paths, expansions = generate_paths(
        predecessors=predecessors,
        target_functions=target_functions,
        max_path_length=arguments.max_path_length,
        max_function_visits=arguments.max_function_visits,
        max_expansions=arguments.max_expansions,
    )

    retained_paths = paths[:arguments.max_paths]

    for rank, path in enumerate(
        retained_paths,
        start=1,
    ):
        path["repeat_rank"] = rank

    output = {
        contract_name: {
            "property_functions": property_functions,
            "property_variables": sorted(
                property_variables
            ),
            "target_functions": target_functions,
            "max_path_length": arguments.max_path_length,
            "max_function_visits": (
                arguments.max_function_visits
            ),
            "generated_path_count": len(paths),
            "retained_path_count": len(retained_paths),
            "dfs_expansions": expansions,
            "paths": retained_paths,
        }
    }

    json.dump(
        output,
        sys.stdout,
        indent=2,
        ensure_ascii=False,
    )
    print()


if __name__ == "__main__":
    main()
