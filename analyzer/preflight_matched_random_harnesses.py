#!/usr/bin/env python3

"""Compile-check all frozen matched-random Harnesses without fuzzing."""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
from pathlib import Path


FIELDS = (
    "cohort",
    "benchmark",
    "selected_candidate_indices",
    "harness_file",
    "harness_contract",
    "compiler",
    "compile_status",
    "warning_lines",
    "stderr_file",
)


def compiler_path(root: Path, version: str) -> Path:
    return root / f"solc-{version}" / f"solc-{version}"


def run_preflight(
    project_root: Path,
    manifest: Path,
    solc_root: Path,
    log_root: Path,
) -> list[dict[str, str]]:
    with manifest.open("r", encoding="utf-8", newline="") as handle:
        harnesses = list(csv.DictReader(handle))
    if not harnesses:
        raise ValueError("Harness manifest is empty")

    rows: list[dict[str, str]] = []
    for harness in harnesses:
        compiler = compiler_path(solc_root, harness["compiler"])
        source = project_root / harness["harness_file"]
        if not compiler.is_file() or not os.access(compiler, os.X_OK):
            raise ValueError(f"Missing compiler: {compiler}")
        if not source.is_file():
            raise ValueError(f"Missing Harness: {source}")

        stderr_path = (
            log_root
            / harness["benchmark"]
            / f"candidate-{harness['selected_candidate_indices'].replace(';', '-')}.stderr.log"
        )
        stderr_path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            [
                str(compiler),
                "--allow-paths",
                str(project_root / "contracts"),
                "--bin",
                str(source),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        stderr_path.write_text(result.stderr, encoding="utf-8")
        rows.append(
            {
                "cohort": harness["cohort"],
                "benchmark": harness["benchmark"],
                "selected_candidate_indices": harness["selected_candidate_indices"],
                "harness_file": harness["harness_file"],
                "harness_contract": harness["harness_contract"],
                "compiler": harness["compiler"],
                "compile_status": "PASS" if result.returncode == 0 else "FAIL",
                "warning_lines": str(
                    sum("warning" in line.lower() for line in result.stderr.splitlines())
                ),
                "stderr_file": stderr_path.relative_to(project_root).as_posix(),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def build_report(rows: list[dict[str, str]]) -> str:
    passed = sum(row["compile_status"] == "PASS" for row in rows)
    warnings = sum(int(row["warning_lines"]) for row in rows)
    benchmarks = len({row["benchmark"] for row in rows})
    return "\n".join(
        [
            "# Matched Random Harness编译预检",
            "",
            f"- 基准：{benchmarks}；",
            f"- 去重Harness：{len(rows)}；",
            f"- 编译通过：{passed}/{len(rows)}；",
            f"- 编译器警告行计数：{warnings}；",
            "- 本预检没有运行Echidna，也没有产生正式成功率数据。",
            "",
            "只有全部Harness通过后，冻结的270行execution manifest才可进入正式运行。",
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--solc-root", type=Path)
    parser.add_argument("--log-root", required=True, type=Path)
    parser.add_argument("--output-csv", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()
    log_root = args.log_root
    if not log_root.is_absolute():
        log_root = project_root / log_root
    solc_root = args.solc_root or (
        Path.home() / ".solc-select" / "artifacts"
    )
    rows = run_preflight(
        project_root,
        args.manifest,
        solc_root,
        log_root,
    )
    write_csv(args.output_csv, rows)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(build_report(rows), encoding="utf-8")
    failures = [row for row in rows if row["compile_status"] != "PASS"]
    if failures:
        raise SystemExit(f"Harness compilation failures: {len(failures)}")
    print(f"Compiled matched-random Harnesses: {len(rows)}")


if __name__ == "__main__":
    main()
