import json
import argparse
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def is_property_function(name: str) -> bool:
    return name.startswith("echidna_")


def property_function_base_name(name: str) -> str:
    """Return the function name without its full-name signature suffix."""
    return name.split("(", 1)[0]


def resolve_property_function(
    functions: dict[str, dict[str, Any]],
    requested: str,
) -> str:
    """Resolve a CLI property name against rw-data function keys."""
    requested = requested.strip()

    if not requested:
        raise ValueError("--property must not be empty")

    candidates = [
        name
        for name in functions
        if is_property_function(name)
        and (
            name == requested
            or property_function_base_name(name)
            == property_function_base_name(requested)
        )
    ]

    if not candidates:
        raise ValueError(
            f"Property function {requested!r} not found"
        )

    if requested in candidates:
        return requested

    if len(candidates) > 1:
        raise ValueError(
            f"Property function {requested!r} is ambiguous: "
            f"{', '.join(sorted(candidates))}"
        )

    return candidates[0]


def build_edges(
    functions: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    normal_functions = {
        name: info
        for name, info in functions.items()
        if not is_property_function(name)
    }

    edges: list[dict[str, Any]] = []

    for source_name, source_info in normal_functions.items():
        for target_name, target_info in normal_functions.items():
            if source_name == target_name:
                continue

            source_writes = set(source_info.get("write", []))
            target_reads = set(target_info.get("read", []))

            shared_variables = source_writes & target_reads

            if not shared_variables:
                continue

            edges.append(
                {
                    "from": source_name,
                    "to": target_name,
                    "score": 2 * len(shared_variables),
                    "variables": sorted(shared_variables),
                }
            )

    return edges


def find_property_variables(
    functions: dict[str, dict[str, Any]],
) -> set[str]:
    variables: set[str] = set()

    for name, info in functions.items():
        if is_property_function(name):
            variables.update(info.get("read", []))

    return variables


def find_selected_property_variables(
    functions: dict[str, dict[str, Any]],
    property_function: str,
) -> set[str]:
    return set(functions[property_function].get("read", []))


def find_target_functions(
    functions: dict[str, dict[str, Any]],
    property_variables: set[str],
) -> set[str]:
    targets: set[str] = set()

    for name, info in functions.items():
        if is_property_function(name):
            continue

        writes = set(info.get("write", []))

        if writes & property_variables:
            targets.add(name)

    return targets


def build_relevant_paths(
    edges: list[dict[str, Any]],
    target_functions: set[str],
    max_length: int,
) -> list[dict[str, Any]]:
    adjacency: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for edge in edges:
        adjacency[edge["from"]].append(edge)

    nodes = {
        edge["from"] for edge in edges
    } | {
        edge["to"] for edge in edges
    }

    paths: list[dict[str, Any]] = []

    def dfs(
        current: str,
        sequence: list[str],
        score: int,
        variables: set[str],
    ) -> None:
        if (
            len(sequence) >= 2
            and current in target_functions
        ):
            paths.append(
                {
                    "sequence": sequence.copy(),
                    "length": len(sequence),
                    "score": score,
                    "dependency_variables": sorted(variables),
                    "target_function": current,
                }
            )

        if len(sequence) >= max_length:
            return

        for edge in adjacency.get(current, []):
            next_function = edge["to"]

            if next_function in sequence:
                continue

            dfs(
                current=next_function,
                sequence=sequence + [next_function],
                score=score + edge["score"],
                variables=variables | set(edge["variables"]),
            )

    for start in sorted(nodes):
        dfs(
            current=start,
            sequence=[start],
            score=0,
            variables=set(),
        )

    paths.sort(
        key=lambda item: (
            item["length"],
            item["score"],
        ),
        reverse=True,
    )

    unique_paths = []
    seen = set()

    for path in paths:
        key = tuple(path["sequence"])

        if key in seen:
            continue

        seen.add(key)
        unique_paths.append(path)

    return unique_paths


def analyze(
    rw_data: dict[str, Any],
    max_length: int,
    top_k: int,
    property_function: str | None = None,
) -> dict[str, Any]:
    result = {}

    if property_function is None:
        contract_items = list(rw_data.items())
    else:
        contract_items = []

        for contract_name, functions in rw_data.items():
            try:
                resolve_property_function(
                    functions,
                    property_function,
                )
            except ValueError:
                continue

            contract_items.append((contract_name, functions))

        if not contract_items:
            raise ValueError(
                f"Property function {property_function!r} not found"
            )

    for contract_name, functions in contract_items:
        selected_property = None

        if property_function is None:
            property_variables = find_property_variables(functions)
        else:
            selected_property = resolve_property_function(
                functions,
                property_function,
            )
            property_variables = find_selected_property_variables(
                functions,
                selected_property,
            )

        target_functions = find_target_functions(
            functions,
            property_variables,
        )

        edges = build_edges(functions)

        paths = build_relevant_paths(
            edges,
            target_functions,
            max_length,
        )

        if selected_property is not None:
            for path in paths:
                path["property_function"] = selected_property

            result[contract_name] = {
                "property_function": selected_property,
                "property_variables": sorted(property_variables),
                "target_functions": sorted(target_functions),
                "paths": paths[:top_k],
            }
        else:
            result[contract_name] = {
                "property_variables": sorted(property_variables),
                "target_functions": sorted(target_functions),
                "paths": paths[:top_k],
            }

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate property-relevant transaction sequences. "
            "Without --property, retain legacy union-property mode."
        )
    )
    parser.add_argument("rw_json", type=Path)
    parser.add_argument("max_length", type=int, nargs="?", default=4)
    parser.add_argument("top_k", type=int, nargs="?", default=20)
    parser.add_argument(
        "--property",
        dest="property_function",
        help=(
            "Explicit echidna_ property function. This enables "
            "property-specific planning."
        ),
    )
    arguments = parser.parse_args()

    input_path = arguments.rw_json
    max_length = arguments.max_length
    top_k = arguments.top_k

    if not input_path.is_file():
        print(
            f"Input file not found: {input_path}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    with input_path.open("r", encoding="utf-8") as file:
        rw_data = json.load(file)

    try:
        result = analyze(
            rw_data,
            max_length,
            top_k,
            property_function=arguments.property_function,
        )
    except (KeyError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from error

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
