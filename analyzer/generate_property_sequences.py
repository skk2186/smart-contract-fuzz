import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def is_property_function(name: str) -> bool:
    return name.startswith("echidna_")


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
) -> dict[str, Any]:
    result = {}

    for contract_name, functions in rw_data.items():
        property_variables = find_property_variables(functions)

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

        result[contract_name] = {
            "property_variables": sorted(property_variables),
            "target_functions": sorted(target_functions),
            "paths": paths[:top_k],
        }

    return result


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: python generate_property_sequences.py "
            "<rw.json> [max_length] [top_k]",
            file=sys.stderr,
        )
        raise SystemExit(1)

    input_path = Path(sys.argv[1])
    max_length = int(sys.argv[2]) if len(sys.argv) >= 3 else 4
    top_k = int(sys.argv[3]) if len(sys.argv) >= 4 else 20

    if not input_path.is_file():
        print(
            f"Input file not found: {input_path}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    with input_path.open("r", encoding="utf-8") as file:
        rw_data = json.load(file)

    result = analyze(
        rw_data,
        max_length,
        top_k,
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
