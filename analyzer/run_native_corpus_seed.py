#!/usr/bin/env python3
"""Run a frozen native corpus-seed smoke manifest serially.

The runner intentionally has no parallel worker option.  Echidna and Slither
in this environment share ``crytic-export`` state, so concurrent processes can
compile/analyze the wrong source.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

try:
    from .materialize_echidna_corpus_seed import materialize
except ImportError:  # pragma: no cover - direct script execution
    from materialize_echidna_corpus_seed import materialize  # type: ignore


COMPLETION_MARKER = "NATIVE_CORPUS_RUN_COMPLETED=1"
FAILURE_PATTERNS = (
    r"compilation failed",
    r"ParserError",
    r"Source .* not found",
    r"Could not compile",
    r"crytic-compile .* (?:error|failed)",
)
FAILED_PROPERTY = re.compile(r"(?:Test\s+)?echidna_[A-Za-z0-9_]+\s*(?::\s*|\s+)(?:failed|falsified)!?", re.I)
PASSED_PROPERTY = re.compile(r"echidna_[A-Za-z0-9_]+\s*:\s*(?:passed|passing)!?", re.I)
FUZZING_COUNT = re.compile(r"fuzzing:\s*(\d+)/(\d+)", re.I)


@dataclass(frozen=True)
class Case:
    name: str
    source: Path
    contract: str
    ranked: Path
    predicate: Path
    property_name: str
    fuzz_seed: int
    test_limit: int
    timeout: int


def load_manifest(path: Path, root: Path) -> list[Case]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {
            "name", "source", "contract", "ranked", "predicate", "property",
            "fuzz_seed", "test_limit", "timeout",
        }
        if set(reader.fieldnames or []) != required:
            raise ValueError(f"manifest columns differ from schema: {reader.fieldnames}")
        cases = []
        seen: set[tuple[str, int]] = set()
        for row in reader:
            name = row["name"]
            fuzz_seed = int(row["fuzz_seed"])
            key = (name, fuzz_seed)
            if key in seen:
                raise ValueError(f"duplicate case/seed: {name}/{fuzz_seed}")
            seen.add(key)
            case = Case(
                name=name,
                source=root / row["source"],
                contract=row["contract"],
                ranked=root / row["ranked"],
                predicate=root / row["predicate"],
                property_name=row["property"],
                fuzz_seed=fuzz_seed,
                test_limit=int(row["test_limit"]),
                timeout=int(row["timeout"]),
            )
            if case.test_limit <= 0 or case.timeout <= 0:
                raise ValueError(f"non-positive budget in case {name}")
            cases.append(case)
    if not cases:
        raise ValueError("manifest is empty")
    return cases


def classify_output(text: str, exit_code: int) -> str:
    if any(re.search(pattern, text, re.I) for pattern in FAILURE_PATTERNS):
        return "startup_error"
    if FAILED_PROPERTY.search(text):
        return "falsified"
    if PASSED_PROPERTY.search(text):
        return "passed"
    if exit_code != 0:
        return "startup_error"
    if re.search(r"Test limit reached\. Stopping\.", text, re.I):
        return "budget_exhausted"
    return "incomplete"


def run_case(
    case: Case,
    root: Path,
    output_root: Path,
    conda: str,
    env_name: str,
    force: bool,
    safe_boundary: bool,
    violation_boundary: bool,
) -> dict[str, str]:
    case_root = output_root / case.name / f"seed-{case.fuzz_seed}"
    coverage_dir = case_root / "coverage"
    log_path = case_root / "run.log"
    if log_path.exists() and COMPLETION_MARKER in log_path.read_text(encoding="utf-8") and not force:
        text = log_path.read_text(encoding="utf-8")
        return _summary(case, "skipped", text, 0, log_path)
    if force and case_root.exists():
        # The target is one validated benchmark/seed directory, never a broad
        # workspace path; a forced rerun must not inherit old corpus entries.
        shutil.rmtree(case_root)
    case_root.mkdir(parents=True, exist_ok=True)

    materialize(
        case.source,
        case.contract,
        case.ranked,
        case.predicate,
        coverage_dir,
        property_name=case.property_name,
        derive_violation_values=violation_boundary,
        safe_boundary_values=safe_boundary,
    )
    command = [
        conda, "run", "--no-capture-output", "-n", env_name, "echidna",
        str(case.source), "--contract", case.contract, "--corpus-dir", str(case_root),
        "--test-mode", "property", "--seq-len", "5", "--test-limit", str(case.test_limit),
        "--timeout", str(case.timeout), "--workers", "1", "--seed", str(case.fuzz_seed),
        "--format", "text",
    ]
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=case.timeout + 60,
            check=False,
        )
        output = completed.stdout
        exit_code = completed.returncode
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + "\nRUNNER_TIMEOUT\n"
        exit_code = 124
    wall = time.monotonic() - started
    header = [
        f"CASE={case.name}",
        f"FUZZ_SEED={case.fuzz_seed}",
        f"SOURCE={case.source}",
        f"COMMAND={' '.join(command)}",
        f"START_TIME={datetime.now(timezone.utc).isoformat()}",
        "",
    ]
    status = classify_output(output, exit_code)
    log_path.write_text(
        "\n".join(header)
        + output
        + f"\nEXIT_CODE={exit_code}\nSTATUS={status}\nPROCESS_WALL_SECONDS={wall:.6f}\n{COMPLETION_MARKER}\n",
        encoding="utf-8",
    )
    return _summary(case, status, output, exit_code, log_path)


def _summary(case: Case, status: str, output: str, exit_code: int, log_path: Path) -> dict[str, str]:
    match = FUZZING_COUNT.search(output)
    return {
        "name": case.name,
        "fuzz_seed": str(case.fuzz_seed),
        "test_limit": str(case.test_limit),
        "status": status,
        "exit_code": str(exit_code),
        "observed_fuzzing": match.group(1) if match else "",
        "log": str(log_path),
    }


def main(argv: list[str] | None = None) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=repo_root / "results/native-corpus-seed-fair/manifest.tsv")
    parser.add_argument("--output-root", type=Path, default=repo_root / "results/native-corpus-seed-fair/runs")
    parser.add_argument("--repo-root", type=Path, default=repo_root)
    parser.add_argument("--conda", default=shutil.which("conda") or "conda")
    parser.add_argument("--env-name", default="contract-fuzz")
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--safe-boundary",
        action="store_true",
        help="seed the closest property-safe boundary value instead of zero",
    )
    parser.add_argument(
        "--violation-boundary",
        action="store_true",
        help="seed the statically derived property-violating boundary value",
    )
    args = parser.parse_args(argv)
    if args.safe_boundary and args.violation_boundary:
        parser.error("--safe-boundary and --violation-boundary are mutually exclusive")
    cases = load_manifest(args.manifest, args.repo_root)
    rows = []
    for case in cases:
        rows.append(
            run_case(
                case,
                args.repo_root,
                args.output_root,
                args.conda,
                args.env_name,
                args.force,
                args.safe_boundary,
                args.violation_boundary,
            )
        )
    args.output_root.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_root / "summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(summary_path)
    return 0 if all(row["status"] in {"falsified", "passed", "budget_exhausted"} for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
