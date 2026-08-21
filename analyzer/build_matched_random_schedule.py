#!/usr/bin/env python3

"""Build a deterministic, balanced matched-random Top-K schedule."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


MANIFEST_FIELDS = {
    "cohort",
    "benchmark",
    "source_file",
    "target_contract",
    "compiler",
    "sequence_json",
    "harness_config",
    "semantic_classification",
}

SCHEDULE_FIELDS = (
    "cohort",
    "benchmark",
    "fuzz_seed",
    "schedule_seed",
    "selection_id",
    "candidate_count",
    "top_k",
    "selected_candidate_indices",
    "selected_sequences",
    "selection_sha256",
    "sequence_json_sha256",
    "source_file",
    "target_contract",
    "compiler",
    "harness_config",
    "semantic_classification",
)


def stable_permutation(
    size: int,
    schedule_seed: int,
    benchmark: str,
    block: int,
    purpose: str,
) -> list[int]:
    keyed: list[tuple[bytes, int]] = []
    for index in range(size):
        material = (
            f"matched-random-v1|{schedule_seed}|{benchmark}|"
            f"{block}|{purpose}|{index}"
        ).encode("utf-8")
        keyed.append((hashlib.sha256(material).digest(), index))
    return [index for _, index in sorted(keyed)]


def balanced_schedule(
    candidate_count: int,
    runs: int,
    top_k: int,
    schedule_seed: int,
    benchmark: str,
) -> list[tuple[int, int, list[int]]]:
    if candidate_count < 1:
        raise ValueError("candidate_count must be positive")
    if runs < 1:
        raise ValueError("runs must be positive")
    if top_k < 1 or top_k > candidate_count:
        raise ValueError("top_k must be between 1 and candidate_count")

    selections: list[tuple[int, int, list[int]]] = []
    block = 0
    while len(selections) < runs:
        candidate_order = stable_permutation(
            candidate_count, schedule_seed, benchmark, block, "candidates"
        )
        offset_order = stable_permutation(
            candidate_count, schedule_seed, benchmark, block, "offsets"
        )
        for offset in offset_order:
            selected = [
                candidate_order[(offset + step) % candidate_count]
                for step in range(top_k)
            ]
            selections.append((block, offset, selected))
            if len(selections) == runs:
                break
        block += 1
    return selections


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None or not MANIFEST_FIELDS.issubset(reader.fieldnames):
            raise ValueError("Matched-random manifest is missing required columns")
        rows = list(reader)
    if not rows:
        raise ValueError("Matched-random manifest is empty")
    ids = [(row["cohort"], row["benchmark"]) for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate cohort/benchmark in matched-random manifest")
    return rows


def load_paths(path: Path, contract: str) -> list[list[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if contract not in data:
        raise ValueError(f"Contract {contract!r} missing from {path}")
    paths = [
        entry.get("sequence", [])
        for entry in data[contract].get("paths", [])
    ]
    paths = [sequence for sequence in paths if len(sequence) >= 2]
    if not paths:
        raise ValueError(f"No usable multi-step paths in {path}")
    normalized = [tuple(sequence) for sequence in paths]
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"Duplicate sequences in candidate pool: {path}")
    return paths


def build(
    manifest_path: Path,
    project_root: Path,
    runs: int,
    top_k: int,
    schedule_seed: int,
) -> tuple[list[dict[str, str | int]], list[dict[str, str | int]]]:
    manifest = load_manifest(manifest_path)
    schedule_rows: list[dict[str, str | int]] = []
    case_rows: list[dict[str, str | int]] = []

    for case in manifest:
        source = project_root / case["source_file"]
        sequence_json = project_root / case["sequence_json"]
        if not source.is_file():
            raise ValueError(f"Missing source file: {source}")
        if not sequence_json.is_file():
            raise ValueError(f"Missing sequence JSON: {sequence_json}")
        paths = load_paths(sequence_json, case["target_contract"])
        candidate_count = len(paths)
        if top_k > candidate_count:
            raise ValueError(
                f"top_k exceeds candidate count for {case['benchmark']}"
            )
        degenerate = candidate_count == top_k
        selections = [] if degenerate else balanced_schedule(
            candidate_count,
            runs,
            top_k,
            schedule_seed,
            case["benchmark"],
        )
        inclusion: Counter[int] = Counter()
        sequence_json_hash = sha256_file(sequence_json)

        for fuzz_seed, (block, offset, selected) in enumerate(
            selections, start=1
        ):
            inclusion.update(selected)
            selected_sequences = [paths[index] for index in selected]
            canonical = json.dumps(
                selected_sequences,
                ensure_ascii=False,
                separators=(",", ":"),
            )
            selection_hash = hashlib.sha256(
                canonical.encode("utf-8")
            ).hexdigest()
            schedule_rows.append(
                {
                    "cohort": case["cohort"],
                    "benchmark": case["benchmark"],
                    "fuzz_seed": fuzz_seed,
                    "schedule_seed": schedule_seed,
                    "selection_id": f"b{block:02d}-o{offset:03d}",
                    "candidate_count": candidate_count,
                    "top_k": top_k,
                    "selected_candidate_indices": ";".join(
                        str(index + 1) for index in selected
                    ),
                    "selected_sequences": " || ".join(
                        " -> ".join(sequence)
                        for sequence in selected_sequences
                    ),
                    "selection_sha256": selection_hash,
                    "sequence_json_sha256": sequence_json_hash,
                    "source_file": case["source_file"],
                    "target_contract": case["target_contract"],
                    "compiler": case["compiler"],
                    "harness_config": case["harness_config"],
                    "semantic_classification": case["semantic_classification"],
                }
            )

        counts = [inclusion[index] for index in range(candidate_count)]
        case_rows.append(
            {
                "cohort": case["cohort"],
                "benchmark": case["benchmark"],
                "candidate_count": candidate_count,
                "top_k": top_k,
                "planned_runs": len(selections),
                "degenerate_same_as_full": int(degenerate),
                "min_candidate_inclusions": min(counts) if counts else 0,
                "max_candidate_inclusions": max(counts) if counts else 0,
                "top_ranked_candidate_inclusions": inclusion[0],
                "sequence_json": case["sequence_json"],
                "semantic_classification": case["semantic_classification"],
            }
        )

    return schedule_rows, case_rows


def write_schedule(path: Path, rows: list[dict[str, str | int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SCHEDULE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_case_summary(path: Path, rows: list[dict[str, str | int]]) -> None:
    fields = tuple(rows[0].keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build_report(
    schedule_rows: list[dict[str, str | int]],
    case_rows: list[dict[str, str | int]],
    runs: int,
    top_k: int,
    schedule_seed: int,
) -> str:
    nondegenerate = [row for row in case_rows if not row["degenerate_same_as_full"]]
    balanced = all(
        int(row["max_candidate_inclusions"])
        - int(row["min_candidate_inclusions"])
        <= 1
        for row in nondegenerate
    )
    lines = [
        "# Matched Random Top-K预注册报告",
        "",
        "## 设计",
        "",
        f"- 候选池：V1 Full阶段保留的同一组路径；",
        f"- Top-K：{top_k}；",
        f"- 每个非退化目标计划运行：{runs}个fuzz seed；",
        f"- 独立调度种子：{schedule_seed}；",
        "- 排列算法：SHA-256键排序与循环窗口，不依赖Python随机数实现；",
        "- fuzz seed只决定Echidna随机过程，路径选择由预先冻结的调度表决定；",
        "- 每个候选的入选次数最大差值不超过1。",
        "",
        "该基线只隔离Full候选池内部的排序/Top-1选择效果，不评估Property或Repeat是否应把路径保留进候选池。",
        "",
        "## 汇总",
        "",
        f"- 目标数：{len(case_rows)}；",
        f"- 非退化目标：{len(nondegenerate)}；",
        f"- 与Full完全相同而不运行的单候选目标：{len(case_rows) - len(nondegenerate)}；",
        f"- 计划随机基线运行：{len(schedule_rows)}；",
        f"- 入选平衡检查：{'PASS' if balanced else 'FAIL'}。",
        "",
        "| cohort | benchmark | candidates | runs | min includes | max includes | full-rank1 includes | scope |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in case_rows:
        lines.append(
            f"| {row['cohort']} | {row['benchmark']} | {row['candidate_count']} | "
            f"{row['planned_runs']} | {row['min_candidate_inclusions']} | "
            f"{row['max_candidate_inclusions']} | {row['top_ranked_candidate_inclusions']} | "
            f"{row['semantic_classification']} |"
        )
    lines.extend(
        [
            "",
            "## 分析边界",
            "",
            "- path count为1的目标不运行random-K1，因为结果与Full-K1完全相同；",
            "- exercise2仍是conditional，只能在调用者关系限制下解释；",
            "- 计划运行前必须从调度表生成Harness并完成编译预检；",
            "- 不得重新抽取一个对结果更有利的调度表；",
            "- 该内部控制不能替代外部SOTA比较。",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--top-k", type=int, default=1)
    parser.add_argument("--schedule-seed", type=int, default=20260805)
    parser.add_argument("--output-schedule", required=True, type=Path)
    parser.add_argument("--output-cases", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    schedule_rows, case_rows = build(
        args.manifest,
        args.project_root.resolve(),
        args.runs,
        args.top_k,
        args.schedule_seed,
    )
    write_schedule(args.output_schedule, schedule_rows)
    write_case_summary(args.output_cases, case_rows)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        build_report(
            schedule_rows,
            case_rows,
            args.runs,
            args.top_k,
            args.schedule_seed,
        ),
        encoding="utf-8",
    )
    print(
        f"Built matched-random schedule: cases={len(case_rows)}, "
        f"planned_runs={len(schedule_rows)}"
    )


if __name__ == "__main__":
    main()
