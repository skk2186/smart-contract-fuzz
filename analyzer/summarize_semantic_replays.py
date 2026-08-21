#!/usr/bin/env python3

"""Build the V1 semantic replay summary and report from validated logs."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


TRACE_CASES = (
    ("formal", "branch-value", "formal-replay", "echidna_branch_value_trace_agrees", "0.8.20", "supported"),
    ("formal", "noisy-four-step", "formal-replay", "echidna_noisy_trace_agrees", "0.8.20", "supported"),
    ("formal", "repeated-call", "formal-replay", "echidna_repeated_call_trace_agrees", "0.8.20", "supported"),
    ("formal", "reset-example", "formal-replay", "echidna_reset_trace_agrees", "0.8.20", "supported"),
    ("formal-b2", "alternative-path", "formal-replay", "echidna_alternative_path_trace_agrees", "0.8.20", "supported"),
    ("formal-b2", "multi-property", "formal-replay", "echidna_multi_property_trace_agrees", "0.8.20", "supported"),
    ("public-c1", "echidna-flags", "public-v8-replay", "echidna_public_flags_trace_agrees", "0.8.20", "supported"),
    ("public-c1", "echidna-multi", "public-v8-replay", "echidna_public_multi_trace_agrees", "0.8.20", "supported"),
    ("public-c1", "exercise2-access-control", "public-v8-replay", "echidna_exercise2_same_caller_trace_agrees", "0.8.20", "conditional"),
    ("public-c1", "smartbugs-multifunc", "public-v4-replay", "echidna_smartbugs_multifunc_trace_agrees", "0.4.25", "supported"),
    ("public-c1", "smartbugs-onefunc", "public-v4-replay", "echidna_smartbugs_onefunc_trace_agrees", "0.4.25", "supported"),
)

CSV_FIELDS = (
    "cohort",
    "benchmark",
    "profile",
    "property",
    "compiler",
    "static_classification",
    "replay_result",
    "replay_scope",
)


def load_validation(path: Path, expected_profile: str) -> dict[str, object]:
    if not path.is_file():
        raise ValueError(f"Missing validation file: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("profile") != expected_profile:
        raise ValueError(f"Unexpected profile in {path}")
    if data.get("all_passed") is not True:
        raise ValueError(f"Profile did not pass: {expected_profile}")
    return data


def build_rows(input_dir: Path) -> list[dict[str, str]]:
    profiles = sorted({case[2] for case in TRACE_CASES})
    validations = {
        profile: load_validation(
            input_dir / f"{profile}-validation.json", profile
        )
        for profile in profiles
    }
    rows: list[dict[str, str]] = []
    for cohort, benchmark, profile, prop, compiler, classification in TRACE_CASES:
        passed = validations[profile].get("passed_properties", [])
        if prop not in passed:
            raise ValueError(f"Missing passed property {prop} in {profile}")
        rows.append(
            {
                "cohort": cohort,
                "benchmark": benchmark,
                "profile": profile,
                "property": prop,
                "compiler": compiler,
                "static_classification": classification,
                "replay_result": "passed",
                "replay_scope": "fixed_successful_trace_same_caller_relation",
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def build_report(rows: list[dict[str, str]]) -> str:
    supported = sum(row["static_classification"] == "supported" for row in rows)
    conditional = sum(row["static_classification"] == "conditional" for row in rows)
    lines = [
        "# V1 Harness差分语义回归报告",
        "",
        "## 结论",
        "",
        f"- 已知固定成功路径重放：{len(rows)}/{len(rows)}通过；",
        f"- 静态supported目标：{supported}/{supported}通过固定路径重放；",
        f"- conditional目标：{conditional}/{conditional}在同一调用者关系下通过；",
        "- 通用负面对照确认：调用者交替和wrapper原子回滚会产生可观察差异。",
        "",
        "这支持一个窄结论：在固定参数、每一步均成功、没有检出的环境依赖且调用者关系对齐时，现有11个目标的直接调用路径和实际生成Harness得到相同的属性相关最终结果。",
        "",
        "它不证明真实跨区块多交易与wrapper单交易完全等价。直接路径是在本地EVM属性检查中以独立外部调用帧重放，不能模拟区块推进、完整交易调度或任意失败前缀。",
        "",
        "## 逐目标结果",
        "",
        "| cohort | benchmark | compiler | static | replay |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['cohort']} | {row['benchmark']} | {row['compiler']} | "
            f"{row['static_classification']} | {row['replay_result']} |"
        )
    lines.extend(
        [
            "",
            "## 对论文结论的影响",
            "",
            "- 10个supported目标可以进入后续公开基准筛选，但必须继续保留atomicity caveat；",
            "- exercise2只能作为同调用者条件下的结果，不能用来隔离纯序列排序收益；",
            "- 当前Harness仍默认不支持payable/msg.value、构造参数及高风险delegatecall/selfdestruct案例；",
            "- 后续公开基准必须先经过静态适用性检查，再决定进入主比较、条件分析或排除流程。",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output-csv", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows(args.input_dir)
    write_csv(args.output_csv, rows)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(build_report(rows), encoding="utf-8")
    print(f"Summarized trace replays: {len(rows)}")


if __name__ == "__main__":
    main()
