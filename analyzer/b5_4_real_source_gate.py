#!/usr/bin/env python3
"""B5-4 deterministic source/preflight gate; no formal fuzzing."""
from __future__ import annotations
import argparse, csv, hashlib, re, shutil, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "paper-ready/v1/b5/b5_real_source_provenance_registry.tsv"
PACKETS = ROOT / "contracts/benchmarks/b5-real-source-adapted"
SUPPORTED = ["b5-rs-echidna-flags","b5-rs-echidna-multi",
             "b5-rs-smartbugs-multifunc","b5-rs-smartbugs-onefunc"]
PROP = {"b5-rs-echidna-flags":"echidna_sometimesfalse","b5-rs-echidna-multi":"echidna_state3",
        "b5-rs-smartbugs-multifunc":"echidna_count_does_not_underflow",
        "b5-rs-smartbugs-onefunc":"echidna_count_does_not_underflow",
        "b5-rs-exercise2-access-control":"echidna_no_transfer"}
TARGET = {"b5-rs-echidna-flags":"PublicEchidnaFlagsTarget","b5-rs-echidna-multi":"C",
          "b5-rs-smartbugs-multifunc":"SmartBugsMultiFuncEchidna",
          "b5-rs-smartbugs-onefunc":"SmartBugsOneFuncEchidna",
          "b5-rs-exercise2-access-control":"TestToken"}
COMPILER = {"b5-rs-echidna-flags":"solc 0.8.20; pragma ^0.8.0",
            "b5-rs-echidna-multi":"solc 0.8.20 execution pin; no source pragma",
            "b5-rs-smartbugs-multifunc":"solc 0.4.25; pragma ^0.4.23",
            "b5-rs-smartbugs-onefunc":"solc 0.4.25; pragma ^0.4.23",
            "b5-rs-exercise2-access-control":"solc 0.8.20; pragma ^0.8.0"}

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1048576), b""): h.update(b)
    return h.hexdigest()

def registry():
    with REG.open(encoding="utf-8", newline="") as f:
        return {r["candidate_id"]: r for r in csv.DictReader(f, delimiter="\t")}

def pairs(value):
    result = {}
    for item in value.split(";"):
        if "=" in item:
            name, digest = item.strip().rsplit("=", 1)
            result[name] = digest
    return result

def static_gate(candidate, row):
    packet = PACKETS / candidate
    seen, errors = [], []
    expected = pairs(row["original_sha256"])
    expected.update(pairs(row["adapted_sha256"]))
    for rel, wanted in expected.items():
        path = packet / rel
        if not path.is_file():
            errors.append("missing:" + rel)
        else:
            actual = sha(path)
            seen.append(rel + "=" + actual)
            if actual != wanted: errors.append("hash_mismatch:" + rel)
    if not (packet / "original/LICENSE").is_file():
        errors.append("missing:original/LICENSE")
    files = sorted((packet / "adapted").glob("*.sol"))
    text = "\n".join(p.read_text(encoding="utf-8") for p in files)
    prop = re.search(r"\b" + re.escape(PROP[candidate]) + r"\s*\(", text) is not None
    target = re.search(r"\bcontract\s+" + re.escape(TARGET[candidate]) + r"\b", text) is not None
    for p in files:
        for line in p.read_text(encoding="utf-8").splitlines():
            m = re.match(r'\s*import\s+"([^"]+)"\s*;', line)
            if m and not (p.parent / m.group(1)).resolve().is_file():
                errors.append("missing_import:" + m.group(1))
    return seen, errors, prop, target

def compile_gate(candidate, run_dir):
    solc = shutil.which("solc")
    if not solc: return "ENVIRONMENT_GATE_BLOCKED", "solc_not_found"
    directory = PACKETS / candidate / "adapted"
    entries = ["solution.sol"] if candidate == "b5-rs-exercise2-access-control" else [p.name for p in sorted(directory.glob("*.sol"))]
    if len(entries) != 1: return "COMPILE_ERROR", "expected_one_entry_file"
    cmd = [solc, "--base-path", str(directory), "--include-path", str(directory), "--bin", entries[0]]
    result = subprocess.run(cmd, cwd=str(directory), capture_output=True, text=True)
    (run_dir / "raw/compile.stdout").write_text(result.stdout, encoding="utf-8")
    (run_dir / "raw/compile.stderr").write_text(result.stderr, encoding="utf-8")
    return ("PASS" if result.returncode == 0 else "COMPILE_ERROR", "returncode=" + str(result.returncode))

def write_artifacts(candidate, seen, errors, prop, target, compiler, note, run_dir):
    for name in ("generated","parsed","summary","status"): (run_dir / name).mkdir()
    preflight = "BLOCKED" if errors or not prop or not target else compiler
    manifest = [("phase","B5-4"),("run_id",run_dir.name),("experiment_class","gate_only"),
                ("paper_usable","false"),("formal_execution","false"),("candidate_id",candidate),
                ("method","preflight"),("seed","none"),("compiler_record",COMPILER[candidate]),
                ("source_packet_hashes",";".join(seen))]
    (run_dir / "manifest.tsv").write_text("field\tvalue\n" +
        "\n".join(k+"\t"+v for k,v in manifest) + "\n", encoding="utf-8")
    status = [("source_hash_status","PASS" if not errors else "FAIL"),
              ("property_status","PASS" if prop else "BLOCKED_PROPERTY_MISSING"),
              ("target_status","PASS" if target else "BLOCKED_TARGET_MISSING"),
              ("dependency_status","PASS" if not any(e.startswith("missing_import") for e in errors) else "BLOCKED_MISSING_IMPORT"),
              ("compiler_status",compiler),("compiler_note",note),
              ("deterministic_replay_status","PREPARED_NOT_EXECUTED"),
              ("preflight_status",preflight),("paper_usable","false"),
              ("formal_fuzzing","NOT_RUN"),("errors",";".join(errors) if errors else "none")]
    (run_dir / "status/gate_status.tsv").write_text("field\tvalue\n" +
        "\n".join(k+"\t"+v for k,v in status) + "\n", encoding="utf-8")
    (run_dir / "summary/gate_summary.md").write_text(
        "# B5-4 gate-only artifact\n\nPreflight/replay preparation only; not a formal result.\n"
        "deterministic_replay: PREPARED_NOT_EXECUTED\nEchidna_formal_fuzzing: NOT_RUN\n"
        "paper_usable: false\n", encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute-preflight", action="store_true")
    ap.add_argument("--compile", action="store_true")
    ap.add_argument("--candidate", action="append", choices=SUPPORTED + ["b5-rs-exercise2-access-control"])
    args = ap.parse_args()
    chosen = args.candidate or SUPPORTED
    if not args.execute_preflight:
        print("B5-4 DRY_RUN\nNo files created; no compiler or Echidna invoked.")
        for c in chosen: print("planned\t" + c + "\t" + COMPILER[c])
        return 0
    reg = registry()
    for c in chosen:
        run_dir = ROOT / "work/v1-restart" / ("b5-4-gate-" + c + "-preflight")
        if run_dir.exists(): raise SystemExit("REFUSED_COLLISION\t" + run_dir.name)
        run_dir.mkdir(parents=True); (run_dir / "raw").mkdir()
        seen, errors, prop, target = static_gate(c, reg[c])
        compiler, note = ("NOT_REQUESTED","compile flag not supplied")
        if args.compile: compiler, note = compile_gate(c, run_dir)
        write_artifacts(c, seen, errors, prop, target, compiler, note, run_dir)
        print(c + "\t" + compiler)
if __name__ == "__main__": main()

