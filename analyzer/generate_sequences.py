import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def is_property_function(function_name: str) -> bool:
    """Echidna 属性函数不作为交易序列中的普通步骤。"""
    return function_name.startswith("echidna_")


def build_edges(functions: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """
    根据状态变量读写集合构建函数依赖边。

    当 f1 写入的变量被 f2 读取时，建立：
        f1 -> f2
    """
    normal_functions = {
        name: info
        for name, info in functions.items()
        if not is_property_function(name)
    }

    edges: list[dict[str, Any]] = []
    items = list(normal_functions.items())

    for source_name, source_info in items:
        for target_name, target_info in items:
            if source_name == target_name:
                continue

            source_writes = set(source_info.get("write", []))
            target_reads = set(target_info.get("read", []))
            target_writes = set(target_info.get("write", []))

            write_read = source_writes & target_reads
            write_write = source_writes & target_writes

            # 路径生成至少要求存在写-读依赖。
            # 仅有写-写关系时暂时不建立有向边。
            if not write_read:
                continue

            score = (
                2 * len(write_read)
                + 1 * len(write_write)
            )

            edges.append(
                {
                    "from": source_name,
                    "to": target_name,
                    "score": score,
                    "write_read_variables": sorted(write_read),
                    "write_write_variables": sorted(write_write),
                }
            )

    return edges


def build_paths(
    edges: list[dict[str, Any]],
    max_length: int,
) -> list[dict[str, Any]]:
    """通过深度优先搜索，将依赖边连接成长度 2～max_length 的路径。"""
    adjacency: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for edge in edges:
        adjacency[edge["from"]].append(edge)

    paths: list[dict[str, Any]] = []

    def dfs(
        current: str,
        sequence: list[str],
        total_score: int,
        dependencies: list[dict[str, Any]],
    ) -> None:
        if len(sequence) >= 2:
            variables = sorted(
                {
                    variable
                    for dependency in dependencies
                    for variable in dependency["write_read_variables"]
                }
            )

            paths.append(
                {
                    "sequence": sequence.copy(),
                    "length": len(sequence),
                    "score": total_score,
                    "dependency_variables": variables,
                    "dependencies": dependencies.copy(),
                }
            )

        if len(sequence) >= max_length:
            return

        for edge in adjacency.get(current, []):
            next_function = edge["to"]

            # 当前版本不允许同一函数在一条序列内重复。
            if next_function in sequence:
                continue

            sequence.append(next_function)
            dependencies.append(edge)

            dfs(
                current=next_function,
                sequence=sequence,
                total_score=total_score + edge["score"],
                dependencies=dependencies,
            )

            dependencies.pop()
            sequence.pop()

    all_nodes = {
        edge["from"] for edge in edges
    } | {
        edge["to"] for edge in edges
    }

    for start_function in sorted(all_nodes):
        dfs(
            current=start_function,
            sequence=[start_function],
            total_score=0,
            dependencies=[],
        )

    # 按“依赖得分优先、路径更长优先”排序。
    paths.sort(
        key=lambda item: (
            item["score"],
            item["length"],
            item["sequence"],
        ),
        reverse=True,
    )

    # 按函数序列去重。
    unique_paths: list[dict[str, Any]] = []
    seen: set[tuple[str, ...]] = set()

    for path in paths:
        key = tuple(path["sequence"])

        if key in seen:
            continue

        seen.add(key)
        unique_paths.append(path)

    return unique_paths


def analyze_contracts(
    rw_data: dict[str, Any],
    max_length: int,
    top_k: int,
) -> dict[str, Any]:
    result: dict[str, Any] = {}

    for contract_name, functions in rw_data.items():
        edges = build_edges(functions)
        paths = build_paths(edges, max_length=max_length)

        result[contract_name] = {
            "edges": edges,
            "paths": paths[:top_k],
        }

    return result


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: python analyzer/generate_sequences.py "
            "<rw.json> [max_length] [top_k]",
            file=sys.stderr,
        )
        raise SystemExit(1)

    rw_path = Path(sys.argv[1])

    if not rw_path.is_file():
        print(f"Input file not found: {rw_path}", file=sys.stderr)
        raise SystemExit(1)

    max_length = int(sys.argv[2]) if len(sys.argv) >= 3 else 3
    top_k = int(sys.argv[3]) if len(sys.argv) >= 4 else 20

    if max_length < 2:
        print("max_length must be at least 2", file=sys.stderr)
        raise SystemExit(1)

    with rw_path.open("r", encoding="utf-8") as file:
        rw_data = json.load(file)

    result = analyze_contracts(
        rw_data=rw_data,
        max_length=max_length,
        top_k=top_k,
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
