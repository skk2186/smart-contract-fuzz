#!/usr/bin/env python3

"""Audit locally available comparison baselines without network access."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Baseline:
    name: str
    kind: str
    command: str
    local_directory: str
    same_property_oracle: str
    comparison_scope: str
    fairness_note: str


BASELINES = (
    Baseline(
        "original-echidna",
        "primary_internal",
        "echidna",
        "",
        "yes",
        "end_to_end_observed_behavior",
        "Same user property, but Original and generated Harness have different ABI, transaction atomicity, caller model, and target-call workload.",
    ),
    Baseline(
        "dependency-property-ablations",
        "internal_ablation",
        "",
        "contracts/harnesses",
        "yes",
        "component_contribution",
        "Existing component comparisons are benchmark-specific and are not an external state-of-the-art baseline.",
    ),
    Baseline(
        "random-matched-top-k",
        "internal_control",
        "",
        "contracts/harnesses/random",
        "yes",
        "sequence_selection_effect",
        "Existing early random data confounds ranking randomness with the Echidna seed; a new preregistered matched-K design is required.",
    ),
    Baseline(
        "smartian",
        "external_sota",
        "dotnet baselines/smartian/src/bin/Release/net8.0/Smartian.dll",
        "baselines/smartian",
        "no_direct_alignment",
        "common_sequence_reachability_or_aligned_bug_oracle_only",
        "SMARTIAN does not natively evaluate arbitrary Echidna boolean properties; raw bug counts would not be directly comparable.",
    ),
    Baseline(
        "medusa",
        "external_engineering",
        "medusa",
        "baselines/medusa",
        "potentially",
        "common_invariant_if_ported",
        "A property port and matched sender, budget, and transaction semantics would be required.",
    ),
    Baseline(
        "foundry-invariant",
        "external_engineering",
        "forge",
        "baselines/foundry",
        "potentially",
        "common_invariant_if_ported",
        "Foundry is an additional invariant engine, not a direct sequence-guidance state-of-the-art baseline.",
    ),
    Baseline(
        "confuzzius",
        "external_sota",
        "confuzzius",
        "",
        "no_direct_alignment",
        "aligned_bug_oracle_only",
        "Different hybrid execution and vulnerability oracles prevent a direct property-success comparison without adaptation.",
    ),
    Baseline(
        "ir-fuzz",
        "external_sota",
        "ir-fuzz",
        "",
        "no_direct_alignment",
        "aligned_bug_oracle_only",
        "Coverage and vulnerability objectives must be aligned before comparison.",
    ),
    Baseline(
        "mufuzz",
        "external_sota",
        "mufuzz",
        "",
        "no_direct_alignment",
        "aligned_bug_oracle_only",
        "Coverage and vulnerability objectives must be aligned before comparison.",
    ),
    Baseline(
        "ityfuzz",
        "external_sota",
        "ityfuzz",
        "",
        "no_direct_alignment",
        "aligned_bug_oracle_only",
        "Snapshot-based execution and bug oracles require a separately defined common task.",
    ),
)


CSV_FIELDS = (
    "baseline",
    "kind",
    "command",
    "command_available",
    "local_directory",
    "local_files",
    "artifact_status",
    "same_property_oracle",
    "comparison_scope",
    "feasibility_status",
    "fairness_note",
)


def count_files(project_root: Path, relative: str) -> int:
    if not relative:
        return 0
    directory = project_root / relative
    if not directory.is_dir():
        return 0
    return sum(
        path.is_file() and ".git" not in path.parts
        for path in directory.rglob("*")
    )


def audit_baselines(project_root: Path) -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    for baseline in BASELINES:
        if baseline.name == "smartian":
            command_available = (
                project_root / "baselines/smartian/src/bin/Release/net8.0/Smartian.dll"
            ).is_file() and bool(
                shutil.which("dotnet") or (project_root / ".tools/dotnet/dotnet").is_file()
            )
        else:
            command_available = bool(
                baseline.command and shutil.which(baseline.command)
            )
        local_files = count_files(project_root, baseline.local_directory)
        artifact_status = (
            "files_present"
            if local_files
            else "empty_or_absent"
        )

        if baseline.name == "original-echidna" and command_available:
            feasibility = "ready_with_semantic_caveats"
        elif baseline.name == "dependency-property-ablations" and local_files:
            feasibility = "ready_internal_only"
        elif baseline.name == "random-matched-top-k":
            feasibility = "requires_new_unconfounded_design"
        elif command_available or local_files:
            feasibility = "requires_compatibility_and_fairness_work"
        else:
            feasibility = "not_locally_available"

        rows.append(
            {
                "baseline": baseline.name,
                "kind": baseline.kind,
                "command": baseline.command,
                "command_available": int(command_available),
                "local_directory": baseline.local_directory,
                "local_files": local_files,
                "artifact_status": artifact_status,
                "same_property_oracle": baseline.same_property_oracle,
                "comparison_scope": baseline.comparison_scope,
                "feasibility_status": feasibility,
                "fairness_note": baseline.fairness_note,
            }
        )
    return rows


def command_version(command: list[str], prefer_prefix: str = "") -> str:
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unavailable"
    text = (result.stdout + "\n" + result.stderr).strip()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if prefer_prefix:
        preferred = [line for line in lines if line.startswith(prefer_prefix)]
        if preferred:
            return preferred[0]
    return lines[0] if lines else "unavailable"


def docker_runtime_status() -> str:
    if not shutil.which("docker"):
        return "missing"
    try:
        result = subprocess.run(
            ["docker", "image", "ls", "--format", "{{.ID}}"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "cli_present_runtime_unavailable"
    if result.returncode == 0:
        return "runtime_available"
    return "cli_present_runtime_unavailable"


def environment_snapshot(project_root: Path) -> dict[str, str]:
    local_dotnet = project_root / ".tools/dotnet/dotnet"
    dotnet_command = [str(local_dotnet), "--version"] if local_dotnet.is_file() else ["dotnet", "--version"]
    return {
        "echidna": command_version(["echidna", "--version"]),
        "solc": command_version(["solc", "--version"], "Version:"),
        "dotnet": command_version(dotnet_command),
        "slither_contract_fuzz": command_version(
            ["conda", "run", "--no-capture-output", "-n", "contract-fuzz", "slither", "--version"]
        ),
        "crytic_compile_contract_fuzz": command_version(
            ["conda", "run", "--no-capture-output", "-n", "contract-fuzz", "crytic-compile", "--version"]
        ),
        "docker": docker_runtime_status(),
    }


def write_csv(path: Path, rows: list[dict[str, str | int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def build_report(rows: list[dict[str, str | int]], environment: dict[str, str]) -> str:
    external = [row for row in rows if row["kind"] == "external_sota"]
    external_ready = [
        row for row in external
        if row["feasibility_status"] != "not_locally_available"
    ]
    lines = [
        "# C2公平基线本地可行性审计",
        "",
        "> 本审计只检查本机已有命令和项目目录；未联网、未下载、未安装，也未运行漏洞发现实验。",
        "",
        "## 结论",
        "",
        f"- 审计比较项：{len(rows)}；",
        f"- 外部SOTA候选：{len(external)}；",
        f"- 当前本地具有命令或代码的外部SOTA：{len(external_ready)}；",
            "- Original Echidna 与 SMARTIAN 均已有可执行入口，但只有 Original 直接对应本项目属性；",
        "- 已有组件消融可以继续使用，但不替代外部SOTA；",
        "- matched random Top-K必须重新设计，现有早期random数据不能进入主比较。",
        "",
        "## 环境",
        "",
    ]
    for name, value in environment.items():
        lines.append(f"- `{name}`：{value}")
    lines.extend(
        [
            "",
            "## 比较项",
            "",
            "| baseline | kind | command | files | status | oracle alignment |",
            "|---|---|---:|---:|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['baseline']} | {row['kind']} | {row['command_available']} | "
            f"{row['local_files']} | {row['feasibility_status']} | {row['same_property_oracle']} |"
        )
    lines.extend(
        [
            "",
            "## Go/No-Go判断",
            "",
            "SMARTIAN 已在本地固定版本并通过 Release 构建和 1 秒入口 smoke，但它原生使用 bug oracle，不直接评估任意 Echidna 布尔属性；因此仍不能把原始漏洞数量与本项目直接比较。正式外部SOTA比较还必须解决属性预言机、发送者、交易模型和预算对齐；其他外部候选仍没有本地命令或代码。",
            "",
            "在外部工具可用前，可以合法推进的工作是：冻结公开候选筛选流程、实现无混杂matched random Top-K，并继续使用Original与组件消融。缺少外部SOTA必须保留为论文限制。",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-csv", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--environment", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()
    rows = audit_baselines(project_root)
    environment = environment_snapshot(project_root)
    write_csv(args.output_csv, rows)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(build_report(rows, environment), encoding="utf-8")
    args.environment.parent.mkdir(parents=True, exist_ok=True)
    args.environment.write_text(
        json.dumps(environment, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Audited baseline entries: {len(rows)}")


if __name__ == "__main__":
    main()
