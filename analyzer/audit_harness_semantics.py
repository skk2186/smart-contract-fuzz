#!/usr/bin/env python3

"""Conservative source-level audit for generated Harness applicability.

The generated V1 Harness deploys a target and executes multiple target calls
inside one wrapper transaction.  This script does not prove equivalence.  It
identifies source constructs that can make the Harness execution model differ
from Original Echidna multi-transaction execution.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path


IMPORT_RE = re.compile(
    r"\bimport\s+(?:[^;]*?\s+from\s+)?[\"']([^\"']+)[\"']\s*;"
)
CONTRACT_RE = re.compile(
    r"\b(?:abstract\s+)?(?:contract|library|interface)\s+([A-Za-z_]\w*)"
)


FEATURE_PATTERNS: dict[str, re.Pattern[str]] = {
    "msg_sender": re.compile(r"\bmsg\s*\.\s*sender\b"),
    "tx_origin": re.compile(r"\btx\s*\.\s*origin\b"),
    "msg_value": re.compile(r"\bmsg\s*\.\s*value\b"),
    "payable": re.compile(r"\bpayable\b"),
    "block_number": re.compile(r"\bblock\s*\.\s*number\b"),
    "block_timestamp": re.compile(
        r"\b(?:block\s*\.\s*timestamp|now)\b"
    ),
    "blockhash": re.compile(r"\bblockhash\s*\("),
    "delegatecall": re.compile(r"\.\s*delegatecall\s*(?:\{|\()"),
    "low_level_call": re.compile(
        r"\.\s*(?:call|callcode|staticcall)\s*(?:\{|\()"
    ),
    "ether_send_transfer": re.compile(r"\.\s*(?:send|transfer)\s*\("),
    "selfdestruct": re.compile(r"\b(?:selfdestruct|suicide)\s*\("),
    "contract_creation": re.compile(r"\bnew\s+[A-Za-z_]\w*\s*\("),
    "address_keyed_mapping": re.compile(
        r"\bmapping\s*\(\s*address(?:\s+payable)?\s*=>"
    ),
    "fallback_or_receive": re.compile(
        r"\b(?:fallback|receive)\s*\("
    ),
}


CSV_FIELDS = [
    "cohort",
    "benchmark",
    "source_file",
    "target_contract",
    "source_files_scanned",
    "contract_declarations",
    "constructor_parameters",
    *FEATURE_PATTERNS.keys(),
    "atomicity_caveat",
    "classification",
    "reasons",
    "evidence",
]


@dataclass(frozen=True)
class SourceUnit:
    path: Path
    clean_text: str
    local_imports: tuple[str, ...]


def strip_comments_and_strings(text: str) -> str:
    """Replace comments and string contents while preserving line numbers."""

    result: list[str] = []
    index = 0
    state = "code"
    quote = ""

    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""

        if state == "code":
            if char == "/" and next_char == "/":
                result.extend("  ")
                index += 2
                state = "line_comment"
                continue
            if char == "/" and next_char == "*":
                result.extend("  ")
                index += 2
                state = "block_comment"
                continue
            if char in {"'", '"'}:
                quote = char
                result.append(" ")
                index += 1
                state = "string"
                continue
            result.append(char)
            index += 1
            continue

        if state == "line_comment":
            if char == "\n":
                result.append("\n")
                state = "code"
            else:
                result.append(" ")
            index += 1
            continue

        if state == "block_comment":
            if char == "*" and next_char == "/":
                result.extend("  ")
                index += 2
                state = "code"
                continue
            result.append("\n" if char == "\n" else " ")
            index += 1
            continue

        if state == "string":
            if char == "\\" and index + 1 < len(text):
                result.append(" ")
                result.append(
                    "\n" if text[index + 1] == "\n" else " "
                )
                index += 2
                continue
            if char == quote:
                result.append(" ")
                index += 1
                state = "code"
                continue
            result.append("\n" if char == "\n" else " ")
            index += 1
            continue

    return "".join(result)


def read_source(path: Path) -> SourceUnit:
    if not path.is_file():
        raise ValueError(f"Source file does not exist: {path}")
    text = path.read_text(encoding="utf-8", errors="strict")
    text_without_comments = strip_comments_preserve_strings(text)
    local_imports = tuple(
        match.group(1)
        for match in IMPORT_RE.finditer(text_without_comments)
        if match.group(1).startswith(".")
    )
    return SourceUnit(
        path=path.resolve(),
        clean_text=strip_comments_and_strings(text),
        local_imports=local_imports,
    )


def strip_comments_preserve_strings(text: str) -> str:
    """Strip comments for import parsing while preserving quoted paths."""

    result: list[str] = []
    index = 0
    state = "code"
    quote = ""

    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""
        if state == "code":
            if char == "/" and next_char == "/":
                result.extend("  ")
                index += 2
                state = "line_comment"
                continue
            if char == "/" and next_char == "*":
                result.extend("  ")
                index += 2
                state = "block_comment"
                continue
            if char in {"'", '"'}:
                quote = char
                state = "string"
            result.append(char)
            index += 1
            continue
        if state == "string":
            result.append(char)
            if char == "\\" and index + 1 < len(text):
                result.append(text[index + 1])
                index += 2
                continue
            if char == quote:
                state = "code"
            index += 1
            continue
        if state == "line_comment":
            if char == "\n":
                result.append("\n")
                state = "code"
            else:
                result.append(" ")
            index += 1
            continue
        if char == "*" and next_char == "/":
            result.extend("  ")
            index += 2
            state = "code"
            continue
        result.append("\n" if char == "\n" else " ")
        index += 1

    return "".join(result)


def collect_source_closure(root_source: Path) -> list[SourceUnit]:
    """Collect the root Solidity file and reachable local imports."""

    pending = [root_source.resolve()]
    visited: set[Path] = set()
    units: list[SourceUnit] = []

    while pending:
        path = pending.pop()
        if path in visited:
            continue
        unit = read_source(path)
        visited.add(path)
        units.append(unit)

        for import_value in unit.local_imports:
            imported = (path.parent / import_value).resolve()
            if not imported.is_file():
                raise ValueError(
                    f"Local import {import_value!r} from {path} does not exist"
                )
            pending.append(imported)

    return sorted(units, key=lambda item: str(item.path))


def find_target_contract_body(clean_text: str, contract_name: str) -> str | None:
    declaration = re.compile(
        rf"\b(?:abstract\s+)?contract\s+{re.escape(contract_name)}\b"
    ).search(clean_text)
    if declaration is None:
        return None

    opening = clean_text.find("{", declaration.end())
    if opening < 0:
        return None

    depth = 0
    for index in range(opening, len(clean_text)):
        if clean_text[index] == "{":
            depth += 1
        elif clean_text[index] == "}":
            depth -= 1
            if depth == 0:
                return clean_text[opening + 1 : index]
    return None


def count_constructor_parameters(
    units: list[SourceUnit], contract_name: str
) -> int:
    for unit in units:
        body = find_target_contract_body(unit.clean_text, contract_name)
        if body is None:
            continue
        match = re.search(r"\bconstructor\s*\(([^)]*)\)", body, re.S)
        if match is None:
            return 0
        parameters = match.group(1).strip()
        if not parameters:
            return 0
        return len([part for part in parameters.split(",") if part.strip()])
    raise ValueError(f"Target contract {contract_name!r} not found in source closure")


def relative_path(path: Path, project_root: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()


def feature_evidence(
    units: list[SourceUnit],
    pattern: re.Pattern[str],
    project_root: Path,
) -> list[str]:
    evidence: list[str] = []
    for unit in units:
        for match in pattern.finditer(unit.clean_text):
            line = unit.clean_text.count("\n", 0, match.start()) + 1
            evidence.append(f"{relative_path(unit.path, project_root)}:{line}")
    return evidence


def classify(features: dict[str, int], constructor_parameters: int) -> tuple[str, list[str]]:
    unsupported: list[str] = []
    conditional: list[str] = []

    if constructor_parameters:
        unsupported.append("constructor_parameters")
    for feature in ("msg_value", "payable", "delegatecall", "selfdestruct"):
        if features[feature]:
            unsupported.append(feature)

    for feature in (
        "msg_sender",
        "tx_origin",
        "block_number",
        "block_timestamp",
        "blockhash",
        "low_level_call",
        "ether_send_transfer",
        "contract_creation",
        "address_keyed_mapping",
        "fallback_or_receive",
    ):
        if features[feature]:
            conditional.append(feature)

    if unsupported:
        return "unsupported", sorted(set(unsupported + conditional))
    if conditional:
        return "conditional", sorted(set(conditional))
    return "supported", ["atomicity_caveat"]


def audit_target(
    project_root: Path,
    cohort: str,
    benchmark: str,
    source_file: str,
    target_contract: str,
) -> dict[str, str | int]:
    source_path = (project_root / source_file).resolve()
    units = collect_source_closure(source_path)
    constructor_parameters = count_constructor_parameters(units, target_contract)

    evidence_by_feature = {
        name: feature_evidence(units, pattern, project_root)
        for name, pattern in FEATURE_PATTERNS.items()
    }
    features = {
        name: int(bool(locations))
        for name, locations in evidence_by_feature.items()
    }
    declarations = sum(
        len(CONTRACT_RE.findall(unit.clean_text)) for unit in units
    )
    classification, reasons = classify(features, constructor_parameters)

    compact_evidence = {
        name: locations
        for name, locations in evidence_by_feature.items()
        if locations
    }

    row: dict[str, str | int] = {
        "cohort": cohort,
        "benchmark": benchmark,
        "source_file": relative_path(source_path, project_root),
        "target_contract": target_contract,
        "source_files_scanned": len(units),
        "contract_declarations": declarations,
        "constructor_parameters": constructor_parameters,
        **features,
        "atomicity_caveat": 1,
        "classification": classification,
        "reasons": ";".join(reasons),
        "evidence": json.dumps(
            compact_evidence,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
    }
    return row


def load_manifest(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise ValueError(f"Manifest does not exist: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {"cohort", "benchmark", "source_file", "target_contract"}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(
                "Manifest must contain cohort, benchmark, source_file, and "
                "target_contract columns"
            )
        rows = list(reader)
    if not rows:
        raise ValueError("Manifest is empty")
    keys = [(row["cohort"], row["benchmark"]) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Manifest contains duplicate cohort/benchmark rows")
    return rows


def write_csv(path: Path, rows: list[dict[str, str | int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def build_report(rows: list[dict[str, str | int]]) -> str:
    counts = {
        status: sum(row["classification"] == status for row in rows)
        for status in ("supported", "conditional", "unsupported")
    }
    lines = [
        "# V1 Harness语义适用性静态审计",
        "",
        "> 本报告是保守的源码特征筛查，不是Original多交易执行与Harness单交易执行的语义等价证明。",
        "",
        "## 汇总",
        "",
        f"- 审计目标：{len(rows)}",
        f"- supported：{counts['supported']}",
        f"- conditional：{counts['conditional']}",
        f"- unsupported：{counts['unsupported']}",
        "- 所有目标均带有`atomicity_caveat=1`，因为Harness把多步调用合并在一次wrapper交易内。",
        "",
        "## 逐目标结果",
        "",
        "| cohort | benchmark | classification | reasons |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['cohort']} | {row['benchmark']} | "
            f"{row['classification']} | {row['reasons']} |"
        )
    lines.extend(
        [
            "",
            "## 分类含义",
            "",
            "- `supported`：未检出额外高风险源码特征，但仍需验证交易原子性差异。",
            "- `conditional`：检出调用者、区块环境、外部交互等特征，只有在逐合同人工分析或差分重放后才能纳入可比实验。",
            "- `unsupported`：当前生成器不能忠实处理，或风险过高；默认不得进入Harness与Original性能比较。",
            "",
            "## 限制与下一步",
            "",
            "该检查器采用保守的源码模式匹配并递归读取本地import。它可能漏掉继承构造函数、经库封装的环境读取或复杂外部调用，也可能标记与目标属性无关的代码。下一步必须对条件支持目标进行人工复核和差分执行。",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-csv", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()
    manifest_rows = load_manifest(args.manifest)
    audited = [
        audit_target(
            project_root=project_root,
            cohort=row["cohort"],
            benchmark=row["benchmark"],
            source_file=row["source_file"],
            target_contract=row["target_contract"],
        )
        for row in manifest_rows
    ]
    audited.sort(key=lambda row: (str(row["cohort"]), str(row["benchmark"])))

    write_csv(args.output_csv, audited)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(build_report(audited), encoding="utf-8")
    print(f"Audited targets: {len(audited)}")
    print(f"CSV: {args.output_csv}")
    print(f"Report: {args.report}")


if __name__ == "__main__":
    main()
