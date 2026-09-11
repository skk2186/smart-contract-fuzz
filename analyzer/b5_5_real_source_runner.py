#!/usr/bin/env python3
"""B5-5 formal runner for the frozen supported adapted real-source registry.

This runner is separate from the B5 controlled runner.  It reuses the
existing PHS analyzers and Harness generator.  It is dry-run by default and
requires B5_5_REAL_SOURCE_AUTHORIZED=1 for the formal batch.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "paper-ready/v1/b5/b5_4_expected_real_source_runs.tsv"
PROV = ROOT / "paper-ready/v1/b5/b5_real_source_provenance_registry.tsv"
PACKETS = ROOT / "contracts/benchmarks/b5-real-source-adapted"
ANALYZER = ROOT / "analyzer"
RESULTS = ROOT / "paper-ready/v1/b5/b5_5_supported_real_source_results.tsv"
SUMMARY = ROOT / "paper-ready/v1/b5/b5_5_supported_real_source_summary.md"
DECISION = ROOT / "paper-ready/v1/b5/b5_5_decision.md"
RETRY_OF_FIRST = "b5-4-rs-b5-rs-echidna-flags-original-s1"

SUPPORTED = [
    "b5-rs-echidna-flags",
    "b5-rs-echidna-multi",
    "b5-rs-smartbugs-multifunc",
    "b5-rs-smartbugs-onefunc",
]
CANDIDATES = {
    "b5-rs-echidna-flags": ("PublicEchidnaFlagsTarget", "echidna_sometimesfalse", "0.8.20", "0.8.20"),
    "b5-rs-echidna-multi": ("C", "echidna_state3", "0.8.20", "0.8.20"),
    "b5-rs-smartbugs-multifunc": ("SmartBugsMultiFuncEchidna", "echidna_count_does_not_underflow", "0.4.25", None),
    "b5-rs-smartbugs-onefunc": ("SmartBugsOneFuncEchidna", "echidna_count_does_not_underflow", "0.4.25", None),
}
METHODS = {
    "Original": (0, "b5-controlled-original.yaml"),
    "Full-K1": (1, "b5-controlled-harness.yaml"),
    "Full-K5": (5, "b5-controlled-harness.yaml"),
}
BUDGET = "testLimit=100000;timeout=30s;workers=1;stopOnFail=false"
EXPECTED_FIELDS = [
    "run_id", "candidate_id", "stratum", "method", "seed", "budget",
    "source_packet_hash_status", "property_status", "semantic_gate_required",
    "expected",
]
RESULT_FIELDS = [
    "run_id", "prereg_row_id", "retry_of", "candidate_id", "stratum",
    "method", "seed",
    "budget", "property", "solc_version", "echidna_version", "status",
    "falsified", "calls_to_failure", "sequence_length", "fuzz_seconds",
    "wall_seconds", "exit_code", "stdout_path", "stderr_path", "artifact_dir",
    "experiment_class", "paper_usable", "artifact_complete", "checksum_pass",
    "notes",
]
STATUSES = {
    "falsified", "budget_exhausted", "compile_error", "tool_error", "timeout",
    "startup_error", "parser_error", "unknown_error", "incomplete",
}


class RunFailure(Exception):
    def __init__(self, status: str, message: str, code: int | None = None):
        super().__init__(message)
        self.status = status
        self.code = code


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def compact(value: str) -> str:
    return " | ".join(value.strip().splitlines())


def cmdline(command: list[Any]) -> str:
    return shlex.join(str(item) for item in command)


def capture(command: list[Any], cwd: Path, env: dict[str, str], commands: list[str]):
    command = [str(item) for item in command]
    commands.append(cmdline(command))
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, check=False)
    return result.returncode, result.stdout, result.stderr


def run_logged(
    command: list[Any],
    cwd: Path,
    env: dict[str, str],
    stdout_path: Path,
    stderr_path: Path,
    commands: list[str],
    timeout: float | None = None,
) -> tuple[int, float, bool]:
    command = [str(item) for item in command]
    commands.append(cmdline(command))
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    try:
        with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
            result = subprocess.run(
                command, cwd=cwd, env=env, stdout=stdout, stderr=stderr,
                check=False, timeout=timeout,
            )
        return result.returncode, time.monotonic() - started, False
    except subprocess.TimeoutExpired:
        return -124, time.monotonic() - started, True


def read_registry(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if not rows or list(rows[0]) != EXPECTED_FIELDS:
        raise SystemExit("BLOCKED: B5-4 registry header mismatch")
    if len(rows) != 120:
        raise SystemExit(f"BLOCKED: B5-4 supported rows={len(rows)}, expected=120")
    if len({row["run_id"] for row in rows}) != 120:
        raise SystemExit("BLOCKED: duplicate run_id in B5-4 registry")
    if {row["candidate_id"] for row in rows} != set(SUPPORTED):
        raise SystemExit("BLOCKED: candidate set differs from B5-4 supported set")
    if any("exercise2" in row["candidate_id"] for row in rows):
        raise SystemExit("BLOCKED: exercise2 appears in supported registry")
    for row in rows:
        if row["stratum"] != "supported_real_source":
            raise SystemExit("BLOCKED: unsupported stratum in frozen registry")
        if row["method"] not in METHODS or not 1 <= int(row["seed"]) <= 10:
            raise SystemExit("BLOCKED: method or seed differs from frozen plan")
        if row["budget"] != BUDGET:
            raise SystemExit("BLOCKED: budget differs from frozen plan")
    return rows


def read_provenance() -> dict[str, dict[str, str]]:
    with PROV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    result = {row["candidate_id"]: row for row in rows}
    if set(SUPPORTED) - set(result):
        raise SystemExit("BLOCKED: provenance registry incomplete")
    return result


def packet_source(candidate: str, row: dict[str, str]) -> tuple[Path, str]:
    paths = [item.strip() for item in row["local_adapted_path"].split(";")]
    if len(paths) != 1:
        raise RunFailure("tool_error", "supported adapted path is not singular")
    source = PACKETS / candidate / paths[0]
    if not source.is_file():
        raise RunFailure("tool_error", f"adapted source missing: {source}")
    expected = ""
    for item in row["adapted_sha256"].split(";"):
        name, _, value = item.strip().rpartition("=")
        if name == row["local_adapted_path"]:
            expected = value
    actual = digest(source)
    if not expected or expected != actual:
        raise RunFailure("tool_error", f"adapted hash mismatch expected={expected} actual={actual}")
    if not (PACKETS / candidate / "original" / "LICENSE").is_file():
        raise RunFailure("tool_error", "archived license missing")
    return source, actual


def write_env(batch: Path, env: dict[str, str], commands: list[str]) -> dict[str, str]:
    directory = batch / "raw" / "environment"
    directory.mkdir(parents=True, exist_ok=True)
    probes = [
        ("python_version", ["python", "--version"]),
        ("which_python", ["bash", "-lc", "command -v python"]),
        ("conda_info_envs", ["conda", "info", "--envs"]),
        ("which_echidna", ["bash", "-lc", "command -v echidna"]),
        ("echidna_version", ["echidna", "--version"]),
        ("which_solc", ["bash", "-lc", "command -v solc"]),
        ("solc_version", ["solc", "--version"]),
        ("solc_select_versions", ["solc-select", "versions"]),
    ]
    values: dict[str, str] = {}
    command_lines = []
    for name, command in probes:
        command_lines.append(cmdline(command))
        try:
            result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, check=False)
            raw = (result.stdout + result.stderr).strip()
        except OSError as error:
            raw = f"unavailable: {error}"
        values[name] = compact(raw)
        (directory / f"{name}.txt").write_text(raw + "\n", encoding="utf-8")
    commands.extend(command_lines)
    (directory / "commands.txt").write_text("\n".join(command_lines) + "\n", encoding="utf-8")
    (batch / "environment.txt").write_text(
        "\n".join(f"{key}={value}" for key, value in values.items()) + "\n",
        encoding="utf-8",
    )
    return values


def status_from_log(text: str, prop: str, code: int) -> str:
    prop = re.escape(prop)
    if re.search(
        rf"Test\s+{prop}(?:\(\))?\s+(?:falsified|failed)|"
        rf"\b{prop}(?:\(\))?\s*:\s*(?:false|failed|falsified)",
        text,
        re.IGNORECASE,
    ):
        return "falsified"
    if re.search(
        r"test limit reached|maximum number of tests|testLimit.*reached|"
        r"time limit reached",
        text,
        re.IGNORECASE,
    ):
        return "budget_exhausted"
    return "tool_error" if code else "incomplete"


def failure_length(text: str) -> tuple[str, str]:
    match = re.search(
        r"Call sequence:\s*(.*?)(?:\n\s*\n|\nUnique instructions|\Z)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return "", ""
    calls = re.findall(r"(?m)^\s*[\w.]+\([^)]*\)", match.group(1))
    value = str(len(calls)) if calls else ""
    return value, value


def artifact_checksum(run_dir: Path) -> tuple[bool, str]:
    checksum_file = run_dir / "status" / "checksums.sha256"
    files = [
        path for path in sorted(run_dir.rglob("*"))
        if path.is_file() and path.name not in {"checksums.sha256", "checksum-verification.txt", "manifest.tsv", "status.env"}
    ]
    checksum_file.write_text(
        "\n".join(f"{digest(path)}  {path.relative_to(ROOT).as_posix()}" for path in files) + "\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        ["sha256sum", "-c", str(checksum_file)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    (run_dir / "status" / "checksum-verification.txt").write_text(
        result.stdout + result.stderr, encoding="utf-8",
    )
    return result.returncode == 0, "pass" if result.returncode == 0 else "fail"


def kv(path: Path, values: dict[str, Any]) -> None:
    path.write_text("\n".join(f"{key}={value}" for key, value in values.items()) + "\n", encoding="utf-8")


def run_one(
    row: dict[str, str],
    batch: Path,
    provenance: dict[str, dict[str, str]],
    base_env: dict[str, str],
    echidna_version: str,
    retry_of: str,
) -> dict[str, str]:
    candidate = row["candidate_id"]
    contract, prop, compiler, fallback = CANDIDATES[candidate]
    method = row["method"]
    run_dir = batch / row["run_id"]
    if run_dir.exists() or run_dir.is_symlink():
        raise SystemExit(f"REFUSED_COLLISION: {run_dir}")
    for name in ("generated", "raw", "parsed", "summary", "status"):
        (run_dir / name).mkdir(parents=True)
    commands: list[str] = []
    status = "incomplete"
    exit_code: int | str = ""
    solc_version = ""
    fuzz_seconds = ""
    wall_seconds = ""
    calls = ""
    sequence = ""
    notes = ["adapted_real_source_evidence", f"source_packet={candidate}", "target_rank_not_declared"]
    source_path = ""
    target = ""
    config_name = ""
    env = base_env.copy()
    env["B5_5_RUN_ID"] = row["run_id"]
    env["B5_5_EXPERIMENT_CLASS"] = "formal"
    started_at = datetime.now(timezone.utc).isoformat()
    try:
        source, source_hash = packet_source(candidate, provenance[candidate])
        source_path = source.relative_to(ROOT).as_posix()
        notes.append(f"adapted_sha256={source_hash}")
        rc, out, err = capture(["solc-select", "use", compiler], ROOT, env, commands)
        (run_dir / "raw" / "solc_select.stdout").write_text(out, encoding="utf-8")
        (run_dir / "raw" / "solc_select.stderr").write_text(err, encoding="utf-8")
        if rc:
            raise RunFailure("tool_error", "solc-select failed", rc)
        rc, out, err = capture(["solc", "--version"], ROOT, env, commands)
        version_text = (out + err).strip()
        (run_dir / "raw" / "solc_version.txt").write_text(version_text + "\n", encoding="utf-8")
        solc_version = compact(version_text)
        if rc or not solc_version:
            raise RunFailure("tool_error", "solc version probe failed", rc)
        generated = run_dir / "generated"
        rw = generated / "rw.json"
        dependency = generated / "dependency.json"
        property_json = generated / "property.json"
        repeat = generated / "repeat.json"
        value = generated / "value.json"
        selected = generated / "selected.json"
        steps = [
            ([sys.executable, ANALYZER / "extract_rw.py", source], rw, "extract_rw.stderr"),
            ([sys.executable, ANALYZER / "generate_sequences.py", rw, 6, 500], dependency, "generate_sequences.stderr"),
            ([sys.executable, ANALYZER / "generate_property_sequences.py", rw, 6, 500], property_json, "generate_property_sequences.stderr"),
            ([sys.executable, ANALYZER / "generate_repetition_aware_sequences.py", rw, 6, 500, "--contract", contract, "--max-function-visits", 2], repeat, "generate_repetition.stderr"),
            ([sys.executable, ANALYZER / "extract_value_constraints.py", source, "--contract", contract], value, "extract_value.stderr"),
        ]
        for command, output, error_name in steps:
            rc, _, _ = run_logged(command, ROOT, env, output, run_dir / "raw" / error_name, commands)
            if rc:
                raise RunFailure("tool_error", f"{Path(str(command[1])).name} failed", rc)
        k, config_name = METHODS[method]
        if method == "Original":
            shutil.copyfile(dependency, selected)
            input_sol = generated / "input.sol"
            shutil.copyfile(source, input_sol)
            target = contract
            commands.append(f"copy {source} {input_sol}")
        else:
            rc, _, _ = run_logged(
                [sys.executable, ANALYZER / "generate_value_guided_sequences.py", repeat, value, "--contract", contract, "--top-k", k],
                ROOT, env, selected, run_dir / "raw" / "generate_value_guided.stderr", commands,
            )
            if rc:
                raise RunFailure("tool_error", "value-guided selection failed", rc)
            target = f"B5_5_{candidate.replace('-', '_')}_{method.lower().replace('-', '')}_Harness"
            base_harness = generated / "base_harness.sol"
            command = [
                sys.executable, ANALYZER / "generate_harness_from_paths.py",
                "--source", source, "--sequences", selected,
                "--target-contract", contract, "--harness-contract", target,
                "--output", base_harness, "--prefix", "b5_5", "--top-k", k,
            ]
            if fallback:
                command.extend(["--solidity-pragma", fallback])
            rc, _, _ = run_logged(
                command, ROOT, env, run_dir / "raw" / "generate_harness.stdout",
                run_dir / "raw" / "generate_harness.stderr", commands,
            )
            if rc:
                raise RunFailure("tool_error", "Harness generation failed", rc)
            input_sol = generated / "input.sol"
            shutil.copyfile(base_harness, input_sol)
            commands.append(f"copy {base_harness} {input_sol}")
        config = generated / "echidna.yaml"
        config_text = (ROOT / "configs" / config_name).read_text(encoding="utf-8")
        if len(re.findall(r"(?m)^testLimit:\s*\d+\s*$", config_text)) != 1:
            raise RunFailure("tool_error", "config testLimit is not singular")
        config.write_text(re.sub(r"(?m)^testLimit:\s*\d+\s*$", "testLimit: 100000", config_text), encoding="utf-8")
        if candidate.startswith("b5-rs-smartbugs-"):
            compile_command = ["solc", "--bin", input_sol.name]
            compile_cwd = generated
        else:
            compile_command = ["solc", "--base-path", ROOT, "--allow-paths", ROOT, input_sol]
            compile_cwd = ROOT
        rc, _, _ = run_logged(
            compile_command, compile_cwd, env, run_dir / "raw" / "solc.stdout",
            run_dir / "raw" / "solc.stderr", commands,
        )
        if rc:
            raise RunFailure("compile_error", "solc compile failed", rc)
        echidna = [
            "/usr/bin/time", "-f", "PROCESS_WALL_SECONDS=%e", "echidna",
            input_sol, "--contract", target, "--config", config, "--seed", row["seed"],
        ]
        rc, elapsed, timed_out = run_logged(
            echidna, ROOT, env, run_dir / "raw" / "echidna.stdout",
            run_dir / "raw" / "echidna.stderr", commands, timeout=45,
        )
        exit_code = rc
        wall_seconds = f"{elapsed:.6f}"
        text = (
            (run_dir / "raw" / "echidna.stdout").read_text(encoding="utf-8", errors="replace")
            + "\n"
            + (run_dir / "raw" / "echidna.stderr").read_text(encoding="utf-8", errors="replace")
        )
        status = "timeout" if timed_out else status_from_log(text, prop, rc)
        match = re.search(r"PROCESS_WALL_SECONDS=([0-9.]+)", text)
        fuzz_seconds = match.group(1) if match else ""
        calls, sequence = failure_length(text)
    except RunFailure as error:
        status = error.status
        exit_code = "" if error.code is None else error.code
        notes.append(str(error))
        (run_dir / "raw" / "runner-error.txt").write_text(f"status={status}\nerror={error}\n", encoding="utf-8")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        status = "unknown_error"
        notes.append(str(error))
        (run_dir / "raw" / "runner-error.txt").write_text(f"status={status}\nerror={error}\n", encoding="utf-8")
    (run_dir / "raw" / "commands.txt").write_text("\n".join(commands) + "\n", encoding="utf-8")
    write_key_value = {
        "run_id": row["run_id"], "prereg_row_id": row["run_id"],
        "retry_of": retry_of,
        "candidate_id": candidate, "stratum": row["stratum"], "method": method,
        "source_path": source_path, "target_contract": target,
        "config_name": config_name, "command_path": "raw/commands.txt",
        "seed": row["seed"], "budget": row["budget"], "property": prop,
        "solc_version": solc_version, "echidna_version": echidna_version,
        "experiment_class": "formal", "paper_usable": "pending",
        "status": status, "started_at": started_at if "started_at" in locals() else "",
        "ended_at": datetime.now(timezone.utc).isoformat(),
    }
    kv(run_dir / "manifest.tsv", write_key_value)
    checksum_ok, checksum_status = artifact_checksum(run_dir)
    paper_usable = str(status in {"falsified", "budget_exhausted"}).lower()
    write_key_value["paper_usable"] = paper_usable
    write_key_value["artifact_complete"] = str(checksum_ok).lower()
    write_key_value["checksum_pass"] = checksum_status
    write_key_value["status"] = status
    kv(run_dir / "manifest.tsv", write_key_value)
    kv(run_dir / "status" / "status.env", {
        "STATUS": status, "PAPER_USABLE": paper_usable,
        "EXPERIMENT_CLASS": "FORMAL", "CHECKSUM_PASS": checksum_status,
        "EXIT_CODE": exit_code,
    })
    if not checksum_ok:
        notes.append("artifact_checksum_failed")
    return {
        "run_id": row["run_id"], "prereg_row_id": row["run_id"],
        "retry_of": retry_of,
        "candidate_id": candidate, "stratum": row["stratum"], "method": method,
        "seed": row["seed"], "budget": row["budget"], "property": prop,
        "solc_version": solc_version, "echidna_version": echidna_version,
        "status": status if status in STATUSES else "unknown_error",
        "falsified": str(int(status == "falsified")), "calls_to_failure": calls,
        "sequence_length": sequence, "fuzz_seconds": fuzz_seconds,
        "wall_seconds": wall_seconds, "exit_code": str(exit_code),
        "stdout_path": (run_dir / "raw" / "echidna.stdout").relative_to(ROOT).as_posix()
        if (run_dir / "raw" / "echidna.stdout").is_file() else "",
        "stderr_path": (run_dir / "raw" / "echidna.stderr").relative_to(ROOT).as_posix()
        if (run_dir / "raw" / "echidna.stderr").is_file() else "",
        "artifact_dir": run_dir.relative_to(ROOT).as_posix(),
        "experiment_class": "formal", "paper_usable": paper_usable,
        "artifact_complete": str(checksum_ok).lower(),
        "checksum_pass": checksum_status, "notes": ";".join(compact(n) for n in notes),
    }


def append(path: Path, row: dict[str, str]) -> None:
    with path.open("a", encoding="utf-8", newline="") as handle:
        csv.DictWriter(handle, fieldnames=RESULT_FIELDS, delimiter="\t").writerow(row)
        handle.flush()
        os.fsync(handle.fileno())


def write_summary(batch: Path, rows: list[dict[str, str]], summary_path: Path) -> None:
    lines = [
        "# B5-5 Supported Real-Source Summary", "",
        "Status: FORMAL_EXECUTION_COMPLETE" if len(rows) == 120 else "Status: PARTIAL_FORMAL_EXECUTION", "",
        "This is adapted real-source evidence under the B5-4 declared execution models. It is separate from B5-Min controlled/custom evidence and B4/B5-2/frozen/matched-random evidence.", "",
        f"- Batch run directory: {batch.relative_to(ROOT).as_posix()}",
        f"- Frozen supported rows: 120",
        f"- Executed rows with preserved records: {len(rows)}/120",
        "- Exercise2 executed: NO", "- B5-4 gate artifacts overwritten: NO",
        "- Historical evidence modified: NO", "",
        "## Candidate and method counts", "",
        "| Candidate | Original | Full-K1 | Full-K5 | Total |",
        "|---|---:|---:|---:|---:|",
    ]
    for candidate in SUPPORTED:
        counts = [sum(row["candidate_id"] == candidate and row["method"] == method for row in rows) for method in METHODS]
        lines.append(f"| {candidate} | {counts[0]} | {counts[1]} | {counts[2]} | {sum(counts)} |")
    lines += ["", "## Status counts", "", "| Status | Count |", "|---|---:|"]
    for status in sorted(STATUSES):
        lines.append(f"| {status} | {sum(row['status'] == status for row in rows)} |")
    discovered = [float(row["calls_to_failure"]) for row in rows if row["status"] == "falsified" and row["calls_to_failure"]]
    calls_text = "not available from preserved logs"
    if discovered:
        ordered = sorted(discovered)
        middle = len(ordered) // 2
        median = ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2
        calls_text = f"median={median:g}; mean={sum(ordered) / len(ordered):g}; n={len(ordered)}"
    discovered_sequences = [
        float(row["sequence_length"])
        for row in rows
        if row["status"] == "falsified" and row["sequence_length"]
    ]
    sequence_text = "not available from preserved logs"
    if discovered_sequences:
        ordered = sorted(discovered_sequences)
        middle = len(ordered) // 2
        median = ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2
        sequence_text = f"median={median:g}; mean={sum(ordered) / len(ordered):g}; n={len(ordered)}"
    lines += [
        "", f"Successful discovery calls-to-failure summary: {calls_text}.",
        f"Successful discovery sequence-length summary: {sequence_text}.", "",
        "A falsified row records an observed violation under the declared model. A budget_exhausted row is right-censored: no counterexample was observed within budget; it is not property passed or safe.", "",
        "Original and Harness are distinct execution models; no semantic equivalence is claimed. Total calls is not a speedup measure. Exercise2 is outside the supported pool.", "",
        "The first B5-5R row is an explicitly labeled retry of the preserved B5-5 tool_error record; the B5-5 blocked artifact was not overwritten.", "",
        "If complete and parseable, this batch can support separately labeled adapted real-source external-validity analysis for the four preregistered candidates. It does not establish ecosystem-wide superiority.",
    ]
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_decision(batch: Path, rows: list[dict[str, str]], decision_path: Path) -> None:
    unparseable = sum(row["status"] in {"incomplete", "unknown_error", "parser_error"} for row in rows)
    errors = sum(row["status"] in {"tool_error", "compile_error", "timeout", "startup_error"} for row in rows)
    if len(rows) < 120:
        decision = "PARTIAL_GO_TO_B5_5R_COMPLETION_OR_ANALYSIS"
        reason = f"Only {len(rows)}/120 rows have preserved records."
    elif unparseable:
        decision = "BLOCKED_NEEDS_ENV_OR_RUNNER_FIX"
        reason = f"{unparseable} rows are not parseable."
    elif errors == len(rows):
        decision = "BLOCKED_NEEDS_ENV_OR_RUNNER_FIX"
        reason = "All rows ended in engineering statuses."
    else:
        decision = "GO_TO_B5_6_REAL_SOURCE_ANALYSIS"
        reason = "All 120 frozen rows have preserved parseable records."
    decision_path.write_text(
        "\n".join([
            "# B5-5 Decision", "", f"Decision: {decision}", "",
            f"Batch: {batch.relative_to(ROOT).as_posix()}",
            f"Frozen supported rows: 120", f"Result records: {len(rows)}", "",
            reason, "",
            "Exercise2 was not executed and is not in the supported pool. B5-4 gate artifacts and historical evidence were not modified.",
            "budget_exhausted remains right-censored; it is not property passed or safe. Original and Harness are not claimed semantically equivalent.",
        ]) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=PREREG)
    parser.add_argument("--batch-dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute-formal", action="store_true")
    parser.add_argument("--results", type=Path)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--decision", type=Path)
    args = parser.parse_args()
    registry = read_registry(args.registry)
    provenance = read_provenance()
    batch = args.batch_dir or (ROOT / "work" / "v1-restart" / datetime.now().strftime("b5-5-formal-real-source-%Y%m%d-%H%M%S"))
    if not batch.is_absolute():
        batch = ROOT / batch
    results_path = args.results or RESULTS
    summary_path = args.summary or SUMMARY
    decision_path = args.decision or DECISION
    results_path = results_path if results_path.is_absolute() else ROOT / results_path
    summary_path = summary_path if summary_path.is_absolute() else ROOT / summary_path
    decision_path = decision_path if decision_path.is_absolute() else ROOT / decision_path
    if not args.execute_formal or args.dry_run:
        print("B5-5 DRY_RUN")
        print(f"registry_rows={len(registry)}")
        print(f"candidates={','.join(SUPPORTED)}")
        print("methods=Original,Full-K1,Full-K5")
        print("seeds=1..10")
        print(f"budget={BUDGET}")
        for method, (top_k, config_name) in METHODS.items():
            print(f"method_config={method}:{config_name}:top_k={top_k}")
        print(f"planned_batch={batch}")
        print("exercise2=NOT_RUN")
        print("formal_execution=NOT_RUN")
        return 0
    if os.environ.get("B5_5_REAL_SOURCE_AUTHORIZED") != "1":
        raise SystemExit("BLOCKED: B5_5_REAL_SOURCE_AUTHORIZED=1 is required")
    if batch.exists():
        raise SystemExit(f"REFUSED_COLLISION: batch directory exists: {batch}")
    if results_path.exists() or summary_path.exists() or decision_path.exists():
        raise SystemExit("REFUSED_OVERWRITE: B5-5 result/summary/decision exists")
    changed = subprocess.run(["git", "diff", "--name-only"], cwd=ROOT, capture_output=True, text=True, check=False).stdout.splitlines()
    forbidden = [path for path in changed if path.startswith("results/") or path.startswith("paper-ready/v1/main10_") or path.startswith("paper-ready/v1/b5/b5_results_")]
    if forbidden:
        raise SystemExit("BLOCKED: forbidden historical paths modified: " + ",".join(forbidden))
    batch.mkdir(parents=True)
    (batch / "raw").mkdir()
    base_env = os.environ.copy()
    base_env["PYTHONDONTWRITEBYTECODE"] = "1"
    commands: list[str] = []
    versions = write_env(batch, base_env, commands)
    (batch / "raw" / "batch_commands.txt").write_text("\n".join(commands) + "\n", encoding="utf-8")
    git_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False)
    (batch / "raw" / "git_commit.txt").write_text(git_commit.stdout.strip() + "\n", encoding="utf-8")
    (batch / "raw" / "formal_authorization.txt").write_text("B5_5_REAL_SOURCE_AUTHORIZED=1\n", encoding="utf-8")
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with results_path.open("w", encoding="utf-8", newline="") as handle:
        csv.DictWriter(handle, fieldnames=RESULT_FIELDS, delimiter="\t").writeheader()
    output_rows = []
    for index, row in enumerate(registry, 1):
        print(f"[{index}/120] {row['run_id']}", flush=True)
        retry_of = RETRY_OF_FIRST if index == 1 else ""
        result = run_one(row, batch, provenance, base_env, versions.get("echidna_version", ""), retry_of)
        append(results_path, result)
        output_rows.append(result)
        print(f"  {result['status']}", flush=True)
    write_summary(batch, output_rows, summary_path)
    write_decision(batch, output_rows, decision_path)
    print(f"results={results_path}")
    print(f"summary={summary_path}")
    print(f"decision={decision_path}")
    print(f"executed={len(output_rows)}/120")
    return 0 if len(output_rows) == 120 else 2


if __name__ == "__main__":
    raise SystemExit(main())
