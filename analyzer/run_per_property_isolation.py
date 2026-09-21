#!/usr/bin/env python3

"""Run the controlled multi-property candidate-isolation experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from extract_rw import extract_rw
from generate_property_sequences import (
    build_edges,
    build_relevant_paths,
    find_property_variables,
    find_selected_property_variables,
    find_target_functions,
    is_property_function,
    resolve_property_function,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = (
    ROOT / "contracts" / "benchmarks"
    / "MultiPropertyInterference.sol"
)
DEFAULT_OUTPUT_DIR = ROOT / "results" / "per-property-isolation"
DEFAULT_CONTRACT = "MultiPropertyInterference"
DEFAULT_TARGET_PROPERTY = "echidna_target_safe"
EXPECTED_SEQUENCE = [
    "prepareTarget()",
    "triggerTarget()",
]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the controlled per-property candidate-isolation "
            "experiment without Echidna."
        )
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
    )
    parser.add_argument(
        "--contract",
        default=DEFAULT_CONTRACT,
    )
    parser.add_argument(
        "--target-property",
        default=DEFAULT_TARGET_PROPERTY,
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=6,
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=1000,
    )
    return parser.parse_args()


def git_commit() -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_candidate_container(
    functions: dict[str, dict[str, Any]],
    max_length: int,
    top_k: int,
    property_function: str | None,
) -> dict[str, Any]:
    edges = build_edges(functions)

    if property_function is None:
        property_variables = find_property_variables(functions)
        property_functions = sorted(
            name
            for name in functions
            if is_property_function(name)
        )
    else:
        property_variables = find_selected_property_variables(
            functions,
            property_function,
        )
        property_functions = [property_function]

    target_functions = find_target_functions(
        functions,
        property_variables,
    )
    paths = build_relevant_paths(
        edges,
        target_functions,
        max_length,
    )

    return {
        "property_function": property_function,
        "property_functions": property_functions,
        "property_variables": sorted(property_variables),
        "target_functions": sorted(target_functions),
        "max_length": max_length,
        "configured_top_k": top_k,
        "candidate_count": len(paths),
        "retained_candidate_count": min(len(paths), top_k),
        "paths": paths[:top_k],
    }


def target_rank(
    paths: list[dict[str, Any]],
    expected_sequence: list[str],
) -> int | None:
    expected = tuple(expected_sequence)

    for rank, path in enumerate(paths, start=1):
        if tuple(path.get("sequence", [])) == expected:
            return rank

    return None


def metric_block(
    candidates: dict[str, Any],
    target_functions: list[str],
    expected_sequence: list[str],
) -> dict[str, Any]:
    paths = candidates["paths"]
    # The runner configures top_k above the complete pool. This explicit
    # list keeps the statistic definition clear if a smaller value is passed.
    all_target_paths = [
        path
        for path in paths
        if path.get("target_function") in target_functions
    ]
    irrelevant_paths = [
        path
        for path in paths
        if path.get("target_function") not in target_functions
    ]
    rank = target_rank(paths, expected_sequence)
    candidate_count = candidates["candidate_count"]
    irrelevant_count = len(irrelevant_paths)

    def top_k_hit(k: int) -> bool:
        return rank is not None and rank <= k

    return {
        "property_variable_count": len(
            candidates["property_variables"]
        ),
        "property_variables": candidates["property_variables"],
        "target_function_count": len(
            candidates["target_functions"]
        ),
        "target_functions": candidates["target_functions"],
        "candidate_count": candidate_count,
        "related_candidate_count": len(all_target_paths),
        "irrelevant_candidate_count": irrelevant_count,
        "irrelevant_candidate_ratio": (
            irrelevant_count / candidate_count
            if candidate_count
            else 0.0
        ),
        "expected_sequence_rank": rank,
        "target_rank": rank,
        "top1_hit": top_k_hit(1),
        "top3_hit": top_k_hit(3),
        "top5_hit": top_k_hit(5),
        "configured_top_k": candidates["configured_top_k"],
        "retained_candidate_count": candidates[
            "retained_candidate_count"
        ],
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    arguments = parse_arguments()

    if arguments.max_length < 2:
        raise SystemExit("--max-length must be at least 2")
    if arguments.top_k <= 0:
        raise SystemExit("--top-k must be greater than zero")
    if not arguments.source.is_file():
        raise SystemExit(f"Benchmark not found: {arguments.source}")

    rw_data = extract_rw(str(arguments.source))
    if arguments.contract not in rw_data:
        raise SystemExit(
            f"Contract {arguments.contract!r} not found in extracted rw data"
        )

    functions = rw_data[arguments.contract]
    target_property = resolve_property_function(
        functions,
        arguments.target_property,
    )

    union_candidates = build_candidate_container(
        functions=functions,
        max_length=arguments.max_length,
        top_k=arguments.top_k,
        property_function=None,
    )
    per_property_candidates = build_candidate_container(
        functions=functions,
        max_length=arguments.max_length,
        top_k=arguments.top_k,
        property_function=target_property,
    )

    common = {
        "benchmark": arguments.source.stem,
        "benchmark_path": arguments.source.relative_to(ROOT).as_posix(),
        "benchmark_sha256": sha256(arguments.source),
        "contract": arguments.contract,
        "target_property": target_property,
        "expected_sequence": EXPECTED_SEQUENCE,
        "git_commit": git_commit(),
        "planner": {
            "name": "generate_property_sequences",
            "max_length": arguments.max_length,
            "top_k": arguments.top_k,
            "path_builder": "build_relevant_paths",
        },
    }

    union_output = {
        **common,
        "method": "LEGACY_UNION",
        "candidates": union_candidates,
    }
    per_property_output = {
        **common,
        "method": "PER_PROPERTY",
        "candidates": per_property_candidates,
    }

    summary = {
        **common,
        "legacy_union": metric_block(
            union_candidates,
            target_functions=per_property_candidates[
                "target_functions"
            ],
            expected_sequence=EXPECTED_SEQUENCE,
        ),
        "per_property": metric_block(
            per_property_candidates,
            target_functions=per_property_candidates[
                "target_functions"
            ],
            expected_sequence=EXPECTED_SEQUENCE,
        ),
    }

    arguments.output_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        arguments.output_dir / "candidates-union.json",
        union_output,
    )
    write_json(
        arguments.output_dir / "candidates-per-property.json",
        per_property_output,
    )
    write_json(
        arguments.output_dir / "summary.json",
        summary,
    )

    print(
        json.dumps(
            {
                "output_dir": str(arguments.output_dir),
                "summary": summary,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
