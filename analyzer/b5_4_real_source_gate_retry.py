#!/usr/bin/env python3
"""B5-4R gate-only retry with compiler-version-aware CLI handling.

This reuses the B5-4 static gate. It never starts Echidna formal fuzzing
and never writes formal result tables.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess

import b5_4_real_source_gate as base


def compile_candidate(candidate, run_dir):
    solc = shutil.which("solc")
    if not solc:
        return "ENVIRONMENT_GATE_BLOCKED", "solc_not_found"
    directory = base.PACKETS / candidate / "adapted"
    entries = [p.name for p in sorted(directory.glob("*.sol"))]
    if len(entries) != 1:
        return "COMPILE_ERROR", "expected_one_entry_file"
    if candidate.startswith("b5-rs-smartbugs-"):
        command = [solc, "--bin", entries[0]]
    else:
        command = [solc, "--base-path", str(directory),
                   "--include-path", str(directory), "--bin", entries[0]]
    result = subprocess.run(command, cwd=str(directory),
                            capture_output=True, text=True)
    (run_dir / "raw/compile.stdout").write_text(result.stdout, encoding="utf-8")
    (run_dir / "raw/compile.stderr").write_text(result.stderr, encoding="utf-8")
    return ("PASS" if result.returncode == 0 else "COMPILE_ERROR",
            " ".join(command) + "; returncode=" + str(result.returncode))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-preflight", action="store_true")
    parser.add_argument("--compile", action="store_true")
    parser.add_argument("--gate-name", default="preflight-solc-compat")
    parser.add_argument("--candidate", action="append", choices=base.SUPPORTED)
    args = parser.parse_args()

    if not args.execute_preflight:
        print("B5-4R DRY_RUN")
        print("No files created; no compiler or Echidna invoked.")
        return 0

    registry = base.registry()
    for candidate in args.candidate or base.SUPPORTED:
        run_dir = base.ROOT / "work/v1-restart" / (
            "b5-4-gate-" + candidate + "-" + args.gate_name
        )
        if run_dir.exists():
            raise SystemExit("REFUSED_COLLISION\t" + run_dir.name)
        run_dir.mkdir(parents=True)
        (run_dir / "raw").mkdir()
        seen, errors, prop, target = base.static_gate(candidate, registry[candidate])
        compiler, note = ("NOT_REQUESTED", "compile flag not supplied")
        if args.compile:
            compiler, note = compile_candidate(candidate, run_dir)
        base.write_artifacts(candidate, seen, errors, prop, target,
                             compiler, note, run_dir)
        print(candidate + "\t" + compiler)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

