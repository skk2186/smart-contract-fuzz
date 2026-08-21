#!/usr/bin/env python3
"""Summarize the frozen matched-random Top-1 control against Full-K1."""

from __future__ import annotations

import argparse
import csv
import math
import re
from pathlib import Path


VALID = {"falsified", "budget_exhausted", "passed"}
STATUS_MARKER = re.compile(r"MATCHED_RANDOM_RUN_STATUS=([A-Za-z_]+)")
BASELINE_PATHS = {
    "formal": "results/formal/runs",
    "formal-b2": "results/formal-b2/runs",
    "public-c1": "results/public-benchmarks/c1/runs",
}


def parse_status(path: Path, *, matched: bool = False) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if matched:
        match = STATUS_MARKER.search(text)
        return match.group(1) if match else "incomplete"
    if re.search(r"compilation failed|ParserError|Source .* not found|Could not compile", text, re.I):
        return "startup_error"
    if re.search(r"(?:Test\s+)?echidna_[A-Za-z0-9_]+\s+(?:falsified|failed)!?", text, re.I):
        return "falsified"
    if re.search(r"Test limit reached\. Stopping\.", text, re.I):
        return "budget_exhausted"
    if re.search(r"echidna_[A-Za-z0-9_]+\s*:\s*(?:passed|passing)!?", text, re.I):
        return "passed"
    return "incomplete"


def exact_mcnemar(discordant_random: int, discordant_full: int) -> float:
    total = discordant_random + discordant_full
    if total == 0:
        return 1.0
    smaller = min(discordant_random, discordant_full)
    tail = sum(math.comb(total, k) for k in range(smaller + 1)) / (2 ** total)
    return min(1.0, 2 * tail)


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total == 0:
        return (float("nan"), float("nan"))
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return centre - margin, centre + margin


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if not rows:
        raise ValueError("matched-random manifest is empty")
    return rows


def summarize(manifest: list[dict[str, str]], project_root: Path) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    paired: list[dict[str, object]] = []
    for row in manifest:
        cohort = row["cohort"]
        benchmark = row["benchmark"]
        seed = int(row["fuzz_seed"])
        random_path = project_root / "results/matched-random-v1/runs" / benchmark / row["method"] / f"seed-{seed}.log"
        baseline_path = project_root / BASELINE_PATHS[cohort] / benchmark / "full-k1" / f"seed-{seed}.log"
        random_status = parse_status(random_path, matched=True) if random_path.is_file() else "missing"
        baseline_status = parse_status(baseline_path) if baseline_path.is_file() else "missing"
        if random_status not in VALID or baseline_status not in VALID:
            raise ValueError(f"non-conclusive pair: {benchmark}/seed-{seed}: {random_status}/{baseline_status}")
        paired.append({
            "cohort": cohort,
            "benchmark": benchmark,
            "seed": seed,
            "random_status": random_status,
            "full_k1_status": baseline_status,
            "random_falsified": int(random_status == "falsified"),
            "full_k1_falsified": int(baseline_status == "falsified"),
        })

    summaries: list[dict[str, object]] = []
    keys = [(row["cohort"], row["benchmark"]) for row in paired]
    for cohort, benchmark in dict.fromkeys(keys):
        group = [row for row in paired if row["cohort"] == cohort and row["benchmark"] == benchmark]
        random_success = sum(int(row["random_falsified"]) for row in group)
        full_success = sum(int(row["full_k1_falsified"]) for row in group)
        random_only = sum(row["random_falsified"] == 1 and row["full_k1_falsified"] == 0 for row in group)
        full_only = sum(row["random_falsified"] == 0 and row["full_k1_falsified"] == 1 for row in group)
        lo, hi = wilson(random_success, len(group))
        summaries.append({
            "cohort": cohort,
            "benchmark": benchmark,
            "runs": len(group),
            "random_falsified": random_success,
            "random_rate": round(random_success / len(group), 6),
            "random_wilson95_low": round(lo, 6),
            "random_wilson95_high": round(hi, 6),
            "full_k1_falsified": full_success,
            "full_k1_rate": round(full_success / len(group), 6),
            "random_only": random_only,
            "full_k1_only": full_only,
            "mcnemar_exact_p": round(exact_mcnemar(random_only, full_only), 12),
        })
    return summaries, paired


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("cannot write empty CSV")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def report(summaries: list[dict[str, object]], paired_count: int) -> str:
    random_total = sum(int(row["random_falsified"]) for row in summaries)
    full_total = sum(int(row["full_k1_falsified"]) for row in summaries)
    total_runs = sum(int(row["runs"]) for row in summaries)
    lines = [
        "# Matched-random Top-1 对 Full-K1 配对分析",
        "",
        "> 事件定义：Echidna 在预算内报告目标属性 falsified；budget_exhausted 作为未发现事件保留。两组使用同一 benchmark、同一 fuzz seed，只有冻结的候选路径选择不同。",
        "",
        f"- 配对运行：{paired_count}；",
        f"- matched-random：{random_total}/{total_runs} = {random_total / total_runs:.4f}；",
        f"- Full-K1：{full_total}/{total_runs} = {full_total / total_runs:.4f}；",
        "",
        "| cohort | benchmark | runs | random | Full-K1 | random-only | Full-only | exact McNemar p |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summaries:
        lines.append(
            f"| {row['cohort']} | {row['benchmark']} | {row['runs']} | "
            f"{row['random_falsified']}/{row['runs']} | {row['full_k1_falsified']}/{row['runs']} | "
            f"{row['random_only']} | {row['full_k1_only']} | {row['mcnemar_exact_p']:.12g} |"
        )
    lines.extend([
        "",
        "## 解释边界",
        "",
        "这是一项候选池内部的因果控制，不是外部SOTA比较。它只评估在相同Full候选池中，将确定性Top-1替换为均衡随机Top-1的影响；不能据此宣称方法优于SMARTIAN、IR-Fuzz等外部工具。",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("results/matched-random-v1/execution-manifest.tsv"))
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-summary", type=Path, required=True)
    parser.add_argument("--output-paired", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    root = args.project_root.resolve()
    summaries, paired = summarize(load_manifest((root / args.manifest).resolve()), root)
    write_csv((root / args.output_summary).resolve(), summaries)
    write_csv((root / args.output_paired).resolve(), paired)
    report_path = (root / args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report(summaries, len(paired)), encoding="utf-8")
    print(f"Analyzed matched-random pairs: {len(paired)}")


if __name__ == "__main__":
    main()
