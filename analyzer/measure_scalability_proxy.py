#!/usr/bin/env python3
"""Build a source/candidate-size proxy table for the frozen local targets."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIELDS = (
    "cohort",
    "benchmark",
    "source_file",
    "source_files_scanned",
    "target_contract",
    "compiler",
    "semantic_classification",
    "source_lines",
    "source_bytes",
    "contract_declarations",
    "function_declarations",
    "public_external_functions",
    "state_variable_proxy",
    "generated_path_count",
    "retained_path_count",
    "max_candidate_sequence_length",
    "candidate_json",
)


TARGETS = (
    ("formal", "branch-value", "contracts/benchmarks/BranchValueExample.sol", "BranchValueExample", "0.8.20", "results/formal/candidates/branch-value/full.json", "BranchValueExample"),
    ("formal", "noisy-four-step", "contracts/benchmarks/NoisyFourStepExample.sol", "NoisyFourStepExample", "0.8.20", "results/formal/candidates/noisy-four-step/full.json", "NoisyFourStepExample"),
    ("formal", "repeated-call", "contracts/benchmarks/RepeatedCallExample.sol", "RepeatedCallExample", "0.8.20", "results/formal/candidates/repeated-call/full.json", "RepeatedCallExample"),
    ("formal", "reset-example", "contracts/benchmarks/ResetExample.sol", "ResetExample", "0.8.20", "results/formal/candidates/reset-example/full.json", "ResetExample"),
    ("formal-b2", "alternative-path", "contracts/benchmarks/AlternativePathExample.sol", "AlternativePathExample", "0.8.20", "results/formal-b2/preparation/alternative-path/full-sequences.json", "AlternativePathExample"),
    ("formal-b2", "multi-property", "contracts/benchmarks/MultiPropertyExample.sol", "MultiPropertyExample", "0.8.20", "results/formal-b2/preparation/multi-property/full-sequences.json", "MultiPropertyExample"),
    ("public-c1", "echidna-flags", "contracts/public-benchmarks/adapted/EchidnaFlagsTarget.sol", "PublicEchidnaFlagsTarget", "0.8.20", "results/public-benchmarks/c1/preparation/echidna-flags/full.json", "PublicEchidnaFlagsTarget"),
    ("public-c1", "echidna-multi", "contracts/public-benchmarks/raw/echidna/multi.sol", "C", "0.8.20", "results/public-benchmarks/c1/preparation/echidna-multi/full.json", "C"),
    ("public-c1", "exercise2-access-control", "contracts/public-benchmarks/raw/exercise2/solution.sol", "TestToken", "0.8.20", "results/public-benchmarks/c1/preparation/exercise2-access-control/full.json", "TestToken"),
    ("public-c1", "smartbugs-multifunc", "contracts/public-benchmarks/adapted/SmartBugsMultiFuncEchidna.sol", "SmartBugsMultiFuncEchidna", "0.4.25", "results/public-benchmarks/c1/preparation/smartbugs-multifunc/full.json", "SmartBugsMultiFuncEchidna"),
    ("public-c1", "smartbugs-onefunc", "contracts/public-benchmarks/adapted/SmartBugsOneFuncEchidna.sol", "SmartBugsOneFuncEchidna", "0.4.25", "results/public-benchmarks/c1/preparation/smartbugs-onefunc/full.json", "SmartBugsOneFuncEchidna"),
)


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//.*", "", text)


def state_variable_proxy(text: str) -> int:
    """Conservative line-level proxy, not a Solidity parser."""
    count = 0
    in_function = False
    depth = 0
    for line in text.splitlines():
        stripped = line.strip()
        depth += stripped.count("{") - stripped.count("}")
        if re.search(r"\bfunction\b|\bmodifier\b|\bevent\b|\bstruct\b|\benum\b", stripped):
            in_function = "function" in stripped or "modifier" in stripped
        if depth <= 1:
            in_function = False
        if depth == 1 and not in_function and stripped.endswith(";"):
            if not re.match(r"^(using|import|pragma|return|emit|assert|require)\b", stripped):
                count += 1
    return count


def load_semantics(path: Path) -> dict[tuple[str, str], str]:
    with path.open(encoding="utf-8", newline="") as handle:
        return {
            (row["cohort"], row["benchmark"]): row["classification"]
            for row in csv.DictReader(handle)
        }


def source_closure(root: Path, entry: Path) -> list[Path]:
    """Resolve relative Solidity imports within the repository."""
    seen: set[Path] = set()
    pending = [entry.resolve()]
    while pending:
        path = pending.pop()
        if path in seen or not path.is_file() or root not in path.parents:
            continue
        seen.add(path)
        text = path.read_text(encoding="utf-8")
        for imported in re.findall(r'import\s+["\']([^"\']+)["\']', text):
            candidate = (path.parent / imported).resolve()
            if candidate not in seen:
                pending.append(candidate)
    return sorted(seen)


def load_candidate(path: Path, contract: str) -> tuple[int, int, int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    entry = data[contract]
    paths = entry.get("paths", [])
    lengths = [len(item.get("sequence", [])) for item in paths]
    return (
        int(entry.get("generated_path_count", len(paths))),
        int(entry.get("retained_path_count", len(paths))),
        max(lengths, default=0),
    )


def build(project_root: Path) -> list[dict[str, object]]:
    semantics = load_semantics(project_root / "results/semantic-applicability/v1/applicability.csv")
    rows: list[dict[str, object]] = []
    for cohort, benchmark, source_rel, target, compiler, candidate_rel, candidate_contract in TARGETS:
        source = project_root / source_rel
        candidate = project_root / candidate_rel
        if not source.is_file() or not candidate.is_file():
            raise FileNotFoundError(f"missing input for {benchmark}: {source} / {candidate}")
        sources = source_closure(project_root, source)
        raw = "\n".join(path.read_text(encoding="utf-8") for path in sources)
        text = strip_comments(raw)
        generated, retained, max_length = load_candidate(candidate, candidate_contract)
        rows.append({
            "cohort": cohort,
            "benchmark": benchmark,
            "source_file": source_rel,
            "source_files_scanned": len(sources),
            "target_contract": target,
            "compiler": compiler,
            "semantic_classification": semantics[(cohort, benchmark)],
            "source_lines": len(raw.splitlines()),
            "source_bytes": len(raw.encode("utf-8")),
            "contract_declarations": len(re.findall(r"\bcontract\s+[A-Za-z_][A-Za-z0-9_]*", text)),
            "function_declarations": len(re.findall(r"\bfunction\s+[A-Za-z_][A-Za-z0-9_]*\s*\(", text)),
            "public_external_functions": len(re.findall(r"\bfunction\s+[^\n{;]+\b(?:public|external)\b", text)),
            "state_variable_proxy": state_variable_proxy(text),
            "generated_path_count": generated,
            "retained_path_count": retained,
            "max_candidate_sequence_length": max_length,
            "candidate_json": candidate_rel,
        })
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_report(path: Path, rows: list[dict[str, object]]) -> None:
    supported = sum(row["semantic_classification"] == "supported" for row in rows)
    conditional = sum(row["semantic_classification"] == "conditional" for row in rows)
    lines = [
        "# 本地目标规模代理表",
        "",
        "> 这是 11 个已冻结本地目标的源码/候选规模描述，不是大型真实合约的可扩展性证明。函数和状态变量数量来自保守正则/行级 proxy，不能替代 Solidity AST 统计。",
        "",
        f"- 目标：{len(rows)}；supported：{supported}；conditional：{conditional}；",
        f"- 源码行数范围：{min(row['source_lines'] for row in rows)}–{max(row['source_lines'] for row in rows)}；",
        f"- retained path 数范围：{min(row['retained_path_count'] for row in rows)}–{max(row['retained_path_count'] for row in rows)}；",
        "",
        "| cohort | benchmark | files | lines | functions | state proxy | retained paths | max sequence | semantic |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['cohort']} | {row['benchmark']} | {row['source_files_scanned']} | {row['source_lines']} | "
            f"{row['function_declarations']} | {row['state_variable_proxy']} | "
            f"{row['retained_path_count']} | {row['max_candidate_sequence_length']} | "
            f"{row['semantic_classification']} |"
        )
    lines.extend([
        "",
        "## 使用边界",
        "",
        "该表可用于报告当前数据集的异质性和候选增长起点；不能外推到大型真实项目，也不能由路径数与源码行数的相关性自动推出 fuzzing 性能。后续取得更大公开任务后，应用 AST/Slither 统计替换 proxy，并把失败、超时和截断纳入分母。",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    root = args.project_root.resolve()
    rows = build(root)
    write_csv((root / args.output_csv).resolve(), rows)
    write_report((root / args.report).resolve(), rows)
    print(f"Measured scalability proxies: {len(rows)} targets")


if __name__ == "__main__":
    main()
