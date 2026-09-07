#!/usr/bin/env python3
"""Build an auditable, deterministic semantic gate for the B2 public tasks.

This runner deliberately does not invoke Echidna, Slither, solc, or an EVM.
It validates preregistered source/config paths and existing B1/Phase 06A
preflight artifacts, then records a static gate. A static gate is never a
native replay result.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "work" / "v1-restart" / "b2-native-replay-gate"
REGISTRY_PATH = REPO_ROOT / "paper-ready" / "v1" / "public_benchmark_registry.tsv"
PREREG_PATH = REPO_ROOT / "docs" / "v1-restart" / "phase05-public-preregistration.tsv"

BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "echidna-flags": {
        "benchmark_id": "PUB01",
        "source_path": "contracts/public-benchmarks/adapted/EchidnaFlagsTarget.sol",
        "contract_name": "PublicEchidnaFlagsTarget",
        "property": "echidna_sometimesfalse",
        "known_sequence": "set0(100*k) -> set1(10*m)",
        "sequence_calls": ["set0(int256)", "set1(int256)"],
        "caller_model": "same caller sufficient; no alternation required",
        "value_model": "set0 input val % 100 == 0; set1 input val % 10 == 0; no msg.value",
        "block_time_model": "no block.timestamp or block.number dependency observed",
        "external_call_model": "no external call, delegatecall, or reentrancy dependency observed",
        "rollback_model": "low for intended successful inputs; retain wrapper atomicity caveat",
        "main_table_gate": "yes_after_b3_prereg",
        "b3_action": "include_in_b3_supported",
        "limitations": "Static gate only; does not prove Original multi-transaction and Harness wrapper equivalence.",
        "notes": "Adapted public source preserves flag0/flag1 transition and the declared property.",
        "preflight_candidates": [
            "work/v1-restart/phase06a-public-supported-3seed/echidna-flags-preflight-phase06a-echidna-flags-preflight-r2",
            "work/v1-restart/phase05-public-smoke/echidna-flags-preflight",
        ],
    },
    "echidna-multi": {
        "benchmark_id": "PUB02",
        "source_path": "contracts/public-benchmarks/raw/echidna/multi.sol",
        "contract_name": "C",
        "property": "echidna_state3",
        "known_sequence": "f(12) -> g(8) -> h(z)",
        "sequence_calls": ["f(uint256)", "g(uint256)", "h(uint256)"],
        "caller_model": "same caller sufficient; no alternation required",
        "value_model": "f requires x == 12; g requires y == 8; h parameter is not state-relevant; no msg.value",
        "block_time_model": "no block.timestamp or block.number dependency observed",
        "external_call_model": "no external call, delegatecall, or reentrancy dependency observed",
        "rollback_model": "medium; require guards make the valid prefix explicit and wrapper atomicity remains a caveat",
        "main_table_gate": "yes_after_b3_prereg",
        "b3_action": "include_in_b3_supported",
        "limitations": "Static gate only; Original seed 1 budget_exhausted remains a budget observation, not property passed.",
        "notes": "The valid three-step require chain is retained. The h parameter is intentionally unconstrained by the source.",
        "preflight_candidates": [
            "work/v1-restart/phase06a-public-supported-3seed/echidna-multi-preflight-phase06a-echidna-multi-preflight",
            "work/v1-restart/phase05-public-smoke/echidna-multi-preflight",
        ],
    },
    "smartbugs-multifunc": {
        "benchmark_id": "PUB03",
        "source_path": "contracts/public-benchmarks/adapted/SmartBugsMultiFuncEchidna.sol",
        "contract_name": "SmartBugsMultiFuncEchidna",
        "property": "echidna_count_does_not_underflow",
        "known_sequence": "init() -> run(uint256) -> run(uint256)",
        "sequence_calls": ["init()", "run(uint256)", "run(uint256)"],
        "caller_model": "same caller sufficient; no alternation required",
        "value_model": "no msg.value; init establishes initialized and repeated run input controls unchecked count decrement",
        "block_time_model": "no block.timestamp or block.number dependency observed",
        "external_call_model": "no external call, delegatecall, or reentrancy dependency observed",
        "rollback_model": "low for intended path; record Solidity 0.4.x unchecked arithmetic and wrapper atomicity caveat",
        "main_table_gate": "yes_after_b3_prereg",
        "b3_action": "include_in_b3_supported",
        "limitations": "Static gate only; adapted small arithmetic task is bounded integration evidence, not broad ecosystem evidence.",
        "notes": "The repeated run is required after init; compiler semantics are Solidity 0.4.x with the preregistered 0.4.25 tool path.",
        "preflight_candidates": [
            "work/v1-restart/phase06a-public-supported-3seed/smartbugs-multifunc-preflight-phase06a-smartbugs-multifunc-preflight",
            "work/v1-restart/phase05-public-smoke/smartbugs-multifunc-preflight",
        ],
    },
    "smartbugs-onefunc": {
        "benchmark_id": "PUB04",
        "source_path": "contracts/public-benchmarks/adapted/SmartBugsOneFuncEchidna.sol",
        "contract_name": "SmartBugsOneFuncEchidna",
        "property": "echidna_count_does_not_underflow",
        "known_sequence": "run(uint256) -> run(uint256)",
        "sequence_calls": ["run(uint256)", "run(uint256)"],
        "caller_model": "same caller sufficient; no alternation required",
        "value_model": "no msg.value; first run initializes and repeated run input controls unchecked count decrement",
        "block_time_model": "no block.timestamp or block.number dependency observed",
        "external_call_model": "no external call, delegatecall, or reentrancy dependency observed",
        "rollback_model": "low for intended path; record Solidity 0.4.x unchecked arithmetic and wrapper atomicity caveat",
        "main_table_gate": "yes_after_b3_prereg",
        "b3_action": "include_in_b3_supported",
        "limitations": "Static gate only; repeated single-function integration evidence is not multi-function ordering evidence.",
        "notes": "Initialization and trigger are both inside run; this task must not be presented as a multi-function ordering advantage.",
        "preflight_candidates": [
            "work/v1-restart/phase06a-public-supported-3seed/smartbugs-onefunc-preflight-phase06a-smartbugs-onefunc-preflight",
            "work/v1-restart/phase05-public-smoke/smartbugs-onefunc-preflight",
        ],
    },
    "exercise2-access-control": {
        "benchmark_id": "PUB05",
        "source_path": "contracts/public-benchmarks/raw/exercise2/solution.sol",
        "contract_name": "TestToken",
        "property": "echidna_no_transfer",
        "known_sequence": "Owner() -> resume()",
        "sequence_calls": ["Owner()", "resume()"],
        "caller_model": "caller-controlled replay required; compare same-caller and alternating-caller schedules",
        "value_model": "no msg.value or payable dependency observed",
        "block_time_model": "no block.timestamp or block.number dependency observed",
        "external_call_model": "no external call, delegatecall, or reentrancy dependency observed; imported token closure is part of the audit",
        "rollback_model": "high; onlyOwner revert and wrapper-wide rollback differ from independent transaction failure scope",
        "main_table_gate": "conditional_only",
        "b3_action": "include_in_b3_conditional",
        "limitations": "Static gate only; cannot replace caller-controlled native replay or upgrade this task into supported pooled evidence.",
        "notes": "msg.sender, owner equality, and the imported address-keyed balances mapping keep this task conditional.",
        "preflight_candidates": [
            "work/v1-restart/phase05-public-smoke/exercise2-access-control-preflight",
        ],
    },
}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_path(path: Optional[Path]) -> Optional[str]:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def read_tsv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def parse_kv_file(path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def git_value(args: Sequence[str], fallback: str = "unknown") -> str:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=REPO_ROOT, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return fallback


def choose_preflight(definition: Dict[str, Any]) -> Optional[Path]:
    for candidate in definition["preflight_candidates"]:
        path = REPO_ROOT / candidate
        status = parse_kv_file(path / "status" / "status.env")
        if status.get("STATUS") == "preflight_pass" and status.get("RUN_COMPLETED") == "1":
            return path
    return None


def source_features(source: str) -> Dict[str, bool]:
    return {
        "caller": bool(re.search(r"\b(msg\.sender|tx\.origin)\b", source)),
        "address_keyed_mapping": bool(re.search(r"\bmapping\s*\(", source)) and bool(
            re.search(r"\[[^\]]*(msg\.sender|address)\s*\]", source)
        ),
        "value": bool(re.search(r"\bmsg\.value\b|\bpayable\b", source)),
        "block_time": bool(re.search(r"\b(block\.timestamp|block\.number)\b", source)),
        "external_call": bool(
            re.search(r"\.(call|delegatecall|staticcall|send|transfer)\s*(?:\{|\(|$)", source)
        ),
        "revert_or_require": bool(re.search(r"\b(require|revert|assert)\s*\(", source)),
    }


def property_present(source: str, property_name: str) -> bool:
    return bool(re.search(r"\bfunction\s+" + re.escape(property_name) + r"\s*\(", source))


def sequence_from_full_json(path: Path, contract_name: str) -> Tuple[List[List[str]], Optional[str]]:
    if not path.exists():
        return [], "missing full-sequences.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        contract = data.get(contract_name)
        if not isinstance(contract, dict):
            return [], "contract entry missing from full-sequences.json"
        paths = contract.get("paths")
        if not isinstance(paths, list):
            return [], "paths entry missing from full-sequences.json"
        sequences: List[List[str]] = []
        for item in paths:
            if isinstance(item, dict) and isinstance(item.get("sequence"), list):
                sequences.append([str(value) for value in item["sequence"]])
        return sequences, None
    except (OSError, json.JSONDecodeError) as exc:
        return [], f"cannot parse full-sequences.json: {exc}"


def validate_preflight(
    preflight: Optional[Path], definition: Dict[str, Any]
) -> Tuple[Dict[str, Any], List[Tuple[Path, str]]]:
    checks: Dict[str, Any] = {
        "preflight_directory": relative_path(preflight),
        "status": "missing",
        "run_completed": False,
        "summary_all_true": False,
        "known_sequence_present": False,
        "artifact_errors": [],
    }
    files_to_hash: List[Tuple[Path, str]] = []
    if preflight is None:
        checks["artifact_errors"].append("no preflight_pass artifact found")
        return checks, files_to_hash

    status_path = preflight / "status" / "status.env"
    status = parse_kv_file(status_path)
    checks["status"] = status.get("STATUS", "missing")
    checks["run_completed"] = status.get("RUN_COMPLETED") == "1"
    if status_path.exists():
        files_to_hash.append((status_path, "preflight/status/status.env"))

    summary_path = preflight / "summary" / "preflight.tsv"
    summary_rows = read_tsv(summary_path) if summary_path.exists() else []
    if summary_path.exists():
        files_to_hash.append((summary_path, "preflight/summary/preflight.tsv"))
    if summary_rows:
        row = summary_rows[0]
        expected = [
            "original_exists", "original_compiles", "rw_extracted", "full_sequences",
            "harness_k1_generated", "harness_k1_compiles", "harness_k5_generated",
            "harness_k5_compiles",
        ]
        checks["summary_all_true"] = all(row.get(key) == "true" for key in expected)
        checks["preflight_summary"] = row
    else:
        checks["artifact_errors"].append("missing or empty preflight summary")

    full_json = preflight / "generated" / "full-sequences.json"
    sequences, sequence_error = sequence_from_full_json(full_json, definition["contract_name"])
    checks["generated_sequences"] = sequences
    checks["known_sequence_present"] = definition["sequence_calls"] in sequences
    if sequence_error:
        checks["artifact_errors"].append(sequence_error)
    if full_json.exists():
        files_to_hash.append((full_json, "preflight/generated/full-sequences.json"))

    for name, label in [
        ("rw.json", "preflight/generated/rw.json"),
        ("value-constraints.json", "preflight/generated/value-constraints.json"),
        ("harness-k1.sol", "preflight/generated/harness-k1.sol"),
        ("harness-k5.sol", "preflight/generated/harness-k5.sol"),
        ("checksums.sha256", "preflight/status/checksums.sha256"),
    ]:
        artifact = preflight / "generated" / name
        if name == "checksums.sha256":
            artifact = preflight / "status" / name
        if artifact.exists():
            files_to_hash.append((artifact, label))
        elif name in {"rw.json", "value-constraints.json", "harness-k1.sol", "harness-k5.sol"}:
            checks["artifact_errors"].append(f"missing {name}")
    return checks, files_to_hash


def build_record(
    name: str,
    definition: Dict[str, Any],
    registry_row: Dict[str, str],
    prereg_row: Dict[str, str],
    start_time: str,
) -> Tuple[Dict[str, Any], List[Tuple[Path, str]]]:
    source_path = REPO_ROOT / definition["source_path"]
    config_rel = prereg_row.get("original_config") or "configs/public-c1-original.yaml"
    config_path = REPO_ROOT / config_rel
    harness_config_rel = prereg_row.get("harness_config") or "configs/public-c1-harness.yaml"
    harness_config_path = REPO_ROOT / harness_config_rel
    preflight = choose_preflight(definition)
    source_text = source_path.read_text(encoding="utf-8", errors="replace") if source_path.exists() else ""
    features = source_features(source_text)
    preflight_checks, artifact_files = validate_preflight(preflight, definition)

    static_errors: List[str] = []
    if not source_path.exists():
        static_errors.append("source path missing")
    if not config_path.exists():
        static_errors.append("original config path missing")
    if not harness_config_path.exists():
        static_errors.append("harness config path missing")
    if not property_present(source_text, definition["property"]):
        static_errors.append("property function missing from source")
    if preflight_checks["status"] != "preflight_pass" or not preflight_checks["run_completed"]:
        static_errors.append("existing preflight is not complete with STATUS=preflight_pass")
    if not preflight_checks["summary_all_true"]:
        static_errors.append("existing preflight summary is not all true")
    if not preflight_checks["known_sequence_present"]:
        static_errors.append("known sequence is not present in existing full-sequences artifact")
    static_errors.extend(preflight_checks["artifact_errors"])

    if static_errors:
        gate_status = "needs_manual_review"
        main_table_gate = "needs_review"
        b3_action = "manual_review_before_b3"
    elif name == "exercise2-access-control":
        gate_status = "conditional_replay_required"
        main_table_gate = definition["main_table_gate"]
        b3_action = definition["b3_action"]
    else:
        gate_status = "static_gate_pass"
        main_table_gate = definition["main_table_gate"]
        b3_action = definition["b3_action"]

    source_sha = sha256_file(source_path) if source_path.exists() else None
    config_sha = sha256_file(config_path) if config_path.exists() else None
    harness_config_sha = sha256_file(harness_config_path) if harness_config_path.exists() else None
    compiler = prereg_row.get("compiler") or "not recorded in preregistration"
    if preflight and (preflight / "manifest.tsv").exists():
        preflight_rows = read_tsv(preflight / "manifest.tsv")
        if preflight_rows and preflight_rows[0].get("compiler"):
            compiler = preflight_rows[0]["compiler"]

    input_files: List[Tuple[Path, str]] = []
    for path, label in [
        (source_path, "source"), (config_path, "original_config"),
        (harness_config_path, "harness_config"),
    ]:
        if path.exists():
            input_files.append((path, label))
    if preflight and (preflight / "manifest.tsv").exists():
        input_files.append((preflight / "manifest.tsv", "preflight/manifest.tsv"))
    input_files.extend(artifact_files)

    record: Dict[str, Any] = {
        "run_id": "b2-native-replay-gate",
        "benchmark_id": definition["benchmark_id"],
        "benchmark_name": name,
        "commit_sha": git_value(["rev-parse", "HEAD"]),
        "method_version": "B2-native-replay-gate-v1-static",
        "stage": "B2",
        "classification_before_b2": registry_row.get("classification", "unknown"),
        "gate_status": gate_status,
        "execution_mode": "static_gate_only",
        "native_replay_attempted": False,
        "source_path": definition["source_path"],
        "source_sha256": source_sha,
        "config_path": config_rel,
        "config_sha256": config_sha,
        "harness_config_path": harness_config_rel,
        "harness_config_sha256": harness_config_sha,
        "compiler": compiler,
        "contract_name": definition["contract_name"],
        "property": definition["property"],
        "known_sequence": definition["known_sequence"],
        "known_sequence_calls": definition["sequence_calls"],
        "caller_model": definition["caller_model"],
        "value_model": definition["value_model"],
        "block_time_model": definition["block_time_model"],
        "external_call_model": definition["external_call_model"],
        "rollback_model": definition["rollback_model"],
        "source_feature_scan": features,
        "semantic_checks": {
            "source_exists": source_path.exists(),
            "property_present": property_present(source_text, definition["property"]),
            "config_exists": config_path.exists(),
            "harness_config_exists": harness_config_path.exists(),
            "preflight": preflight_checks,
        },
        "main_table_gate": main_table_gate,
        "b3_action": b3_action,
        "limitations": definition["limitations"],
        "notes": definition["notes"],
        "static_errors": static_errors,
        "execution_note": "No EVM/native replay was attempted; this record is static_gate_only and cannot support replay_pass.",
        "seed": "not_run",
        "test_limit": "not_run",
        "timeout": "not_applicable",
        "workers": "not_applicable",
        "stop_on_fail": "not_applicable",
        "start_time": start_time,
    }
    return record, input_files


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_notes(path: Path, record: Dict[str, Any]) -> None:
    checks = record["semantic_checks"]
    feature_scan = record["source_feature_scan"]
    lines = [
        f"# B2 semantic gate: {record['benchmark_name']}", "",
        f"- Gate status: {record['gate_status']}",
        f"- Execution mode: {record['execution_mode']}",
        f"- Source: {record['source_path']}",
        f"- Property: {record['property']}",
        f"- Known sequence: {record['known_sequence']}",
        f"- Compiler recorded by B1/preflight: {record['compiler']}", "",
        "## Static checks", "",
        f"- Source exists: {checks['source_exists']}",
        f"- Property present: {checks['property_present']}",
        f"- Original config exists: {checks['config_exists']}",
        f"- Harness config exists: {checks['harness_config_exists']}",
        f"- Existing preflight status: {checks['preflight']['status']}",
        f"- Existing preflight summary all true: {checks['preflight']['summary_all_true']}",
        f"- Known sequence present in existing full-sequences artifact: {checks['preflight']['known_sequence_present']}", "",
        "## Semantic scan", "",
        f"- Caller-sensitive tokens: {feature_scan['caller']}",
        f"- Address-keyed mapping: {feature_scan['address_keyed_mapping']}",
        f"- msg.value/payable: {feature_scan['value']}",
        f"- block.timestamp/block.number: {feature_scan['block_time']}",
        f"- external call/delegatecall/reentrancy token: {feature_scan['external_call']}",
        f"- require/revert/assert token: {feature_scan['revert_or_require']}", "",
        "## Interpretation", "", record["notes"], record["limitations"], record["execution_note"],
    ]
    if record["static_errors"]:
        lines.extend(["", "## Review blockers", ""])
        lines.extend(f"- {error}" for error in record["static_errors"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_command(path: Path, argv: Sequence[str]) -> None:
    path.write_text(" ".join(argv) + "\n", encoding="utf-8")


def write_environment(path: Path, record: Dict[str, Any]) -> None:
    tool_lines = [f"{tool}={shutil.which(tool) or 'not_found'}" for tool in ("solc", "echidna-test", "slither", "forge")]
    lines = [
        f"recorded_at={now_iso()}", f"platform={platform.platform()}",
        f"python={sys.version.replace(os.linesep, ' ')}", f"repo_root={REPO_ROOT}",
        f"commit_sha={record['commit_sha']}", "execution_mode=static_gate_only",
        "native_replay_command=not_invoked", "fuzzing=not_invoked", *tool_lines,
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_checksums(path: Path, entries: Iterable[Tuple[Path, str]]) -> None:
    lines: List[str] = []
    seen: Set[str] = set()
    for file_path, label in entries:
        if not file_path.exists() or label in seen:
            continue
        seen.add(label)
        lines.append(f"{sha256_file(file_path)}  {label}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_tsv(path: Path, headers: Sequence[str], rows: Iterable[Dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(headers), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in headers})


def resolve_benchmarks(benchmark: Optional[str], all_public_b1: bool) -> List[str]:
    if all_public_b1 and benchmark:
        raise SystemExit("Use either --benchmark or --all-public-b1, not both.")
    if not all_public_b1 and not benchmark:
        raise SystemExit("Select one benchmark with --benchmark or use --all-public-b1.")
    if all_public_b1:
        return list(BENCHMARKS.keys())
    assert benchmark is not None
    if benchmark in BENCHMARKS:
        return [benchmark]
    for name, definition in BENCHMARKS.items():
        if benchmark == definition["benchmark_id"]:
            return [name]
    raise SystemExit(f"Unknown B1 public benchmark: {benchmark}")


def validate_registry_inputs(names: Sequence[str]) -> Tuple[Dict[str, Dict[str, str]], Dict[str, Dict[str, str]]]:
    if not REGISTRY_PATH.exists():
        raise SystemExit(f"Missing registry: {relative_path(REGISTRY_PATH)}")
    if not PREREG_PATH.exists():
        raise SystemExit(f"Missing preregistration: {relative_path(PREREG_PATH)}")
    registry_rows = {row.get("benchmark_name", ""): row for row in read_tsv(REGISTRY_PATH)}
    prereg_rows = {row.get("benchmark_id", ""): row for row in read_tsv(PREREG_PATH)}
    selected_registry: Dict[str, Dict[str, str]] = {}
    selected_prereg: Dict[str, Dict[str, str]] = {}
    for name in names:
        definition = BENCHMARKS[name]
        registry_row = registry_rows.get(name)
        if not registry_row:
            raise SystemExit(f"Benchmark is not present in B1 registry: {name}")
        if registry_row.get("benchmark_id") != definition["benchmark_id"]:
            raise SystemExit(f"Registry id mismatch for {name}")
        prereg_row = prereg_rows.get(name)
        if not prereg_row:
            raise SystemExit(f"Benchmark is not present in Phase 05 preregistration: {name}")
        if prereg_row.get("semantic_classification") not in {"supported", "conditional"}:
            raise SystemExit(f"Unexpected preregistration classification for {name}")
        selected_registry[name] = registry_row
        selected_prereg[name] = prereg_row
    return selected_registry, selected_prereg


def dry_run(names: Sequence[str], registry: Dict[str, Dict[str, str]], prereg: Dict[str, Dict[str, str]], out_dir: Path) -> None:
    print("B2 native replay gate dry-run")
    print("execution_mode=static_gate_only")
    print("native_replay=not_invoked")
    print("fuzzing=not_invoked")
    print(f"out_dir={out_dir}")
    for name in names:
        definition = BENCHMARKS[name]
        preflight = choose_preflight(definition)
        print("\t".join([
            definition["benchmark_id"], name, registry[name].get("classification", ""),
            definition["source_path"], prereg[name].get("original_config", ""),
            relative_path(preflight) if preflight else "MISSING",
            "conditional_replay_required" if name == "exercise2-access-control" else "static_gate_pass",
        ]))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=("Audit the five preregistered B1 public benchmarks with a deterministic static semantic gate. "
                     "No Echidna, Slither, solc, randomness, or coverage is used.")
    )
    parser.add_argument("--benchmark", help="One B1 public benchmark name or PUB01..PUB05.")
    parser.add_argument("--all-public-b1", action="store_true", help="Process the five B1 public tasks only; PUB06..PUB08 remain excluded/deferred.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR, help="Output directory (default: work/v1-restart/b2-native-replay-gate).")
    parser.add_argument("--dry-run", action="store_true", help="Print the static-gate plan without writing files.")
    args = parser.parse_args(argv)

    names = resolve_benchmarks(args.benchmark, args.all_public_b1)
    registry, prereg = validate_registry_inputs(names)
    if args.dry_run:
        dry_run(names, registry, prereg, args.out_dir if args.out_dir.is_absolute() else REPO_ROOT / args.out_dir)
        return 0

    out_dir = args.out_dir if args.out_dir.is_absolute() else REPO_ROOT / args.out_dir
    if out_dir.exists() and any(out_dir.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty output directory: {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)
    start_time = now_iso()
    records: List[Dict[str, Any]] = []
    top_manifest_rows: List[Dict[str, Any]] = []

    for name in names:
        definition = BENCHMARKS[name]
        record, input_files = build_record(name, definition, registry[name], prereg[name], start_time)
        benchmark_dir = out_dir / name
        benchmark_dir.mkdir(parents=True, exist_ok=False)
        record["end_time"] = now_iso()
        record["output_directory"] = relative_path(benchmark_dir)
        write_json(benchmark_dir / "replay_manifest.json", record)
        write_json(benchmark_dir / "semantic_gate.json", record)
        write_notes(benchmark_dir / "notes.md", record)
        write_command(benchmark_dir / "command.txt", [sys.executable, *sys.argv])
        write_environment(benchmark_dir / "environment.txt", record)
        write_checksums(benchmark_dir / "checksums.sha256", list(input_files) + [
            (benchmark_dir / "replay_manifest.json", "replay_manifest.json"),
            (benchmark_dir / "semantic_gate.json", "semantic_gate.json"),
            (benchmark_dir / "notes.md", "notes.md"),
            (benchmark_dir / "command.txt", "command.txt"),
            (benchmark_dir / "environment.txt", "environment.txt"),
        ])
        records.append(record)
        top_manifest_rows.append({
            "run_id": record["run_id"], "commit_sha": record["commit_sha"],
            "method_version": record["method_version"], "benchmark_id": record["benchmark_id"],
            "benchmark": name, "contract_file": record["source_path"],
            "contract_sha256": record["source_sha256"], "contract_name": record["contract_name"],
            "property": record["property"], "config_file": record["config_path"],
            "compiler": record["compiler"], "execution_mode": record["execution_mode"],
            "seed": record["seed"], "test_limit": record["test_limit"],
            "timeout": record["timeout"], "workers": record["workers"],
            "stop_on_fail": record["stop_on_fail"], "gate_status": record["gate_status"],
            "main_table_gate": record["main_table_gate"], "b3_action": record["b3_action"],
            "start_time": record["start_time"], "end_time": record["end_time"],
        })

    top_manifest_headers = [
        "run_id", "commit_sha", "method_version", "benchmark_id", "benchmark", "contract_file",
        "contract_sha256", "contract_name", "property", "config_file", "compiler", "execution_mode",
        "seed", "test_limit", "timeout", "workers", "stop_on_fail", "gate_status", "main_table_gate",
        "b3_action", "start_time", "end_time",
    ]
    write_tsv(out_dir / "manifest.tsv", top_manifest_headers, top_manifest_rows)
    summary_headers = [
        "benchmark_id", "benchmark_name", "classification_before_b2", "gate_status", "execution_mode",
        "source_path", "config_path", "property", "known_sequence", "caller_model", "value_model",
        "block_time_model", "external_call_model", "rollback_model", "main_table_gate", "b3_action",
        "limitations", "notes",
    ]
    summary_rows = [{key: record.get(key, "") for key in summary_headers} for record in records]
    write_tsv(out_dir / "gate_summary.tsv", summary_headers, summary_rows)
    write_checksums(out_dir / "checksums.sha256", [
        (REGISTRY_PATH, "input:paper-ready/v1/public_benchmark_registry.tsv"),
        (PREREG_PATH, "input:docs/v1-restart/phase05-public-preregistration.tsv"),
        (out_dir / "manifest.tsv", "output:manifest.tsv"),
        (out_dir / "gate_summary.tsv", "output:gate_summary.tsv"),
    ])
    print(f"Wrote static B2 gate to {out_dir}")
    for record in records:
        print(f"{record['benchmark_id']}\t{record['benchmark_name']}\t{record['gate_status']}\t{record['execution_mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
