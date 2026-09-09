#!/usr/bin/env python3
"""B5 controlled-scenario runner.

This runner owns one isolated run directory. It deliberately does not
produce paper summaries or write any frozen result directory.
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

METHODS: dict[str, dict[str, dict[str, Any]]] = {
    "c1": {
        "original": {"selected": "dependency", "k": 0, "value": 0, "repeat": 0},
        "dependency-only": {"selected": "dependency", "k": 0, "value": 0, "repeat": 0},
        "full-k1": {"selected": "value", "k": 1, "value": 1, "repeat": 1},
        "full-k5": {"selected": "value", "k": 5, "value": 1, "repeat": 1},
    },
    "c2": {
        "original": {"selected": "dependency", "k": 0, "value": 0, "repeat": 0},
        "no-repeat": {"selected": "property", "k": 0, "value": 0, "repeat": 0},
        "full-k1": {"selected": "value", "k": 1, "value": 1, "repeat": 1},
        "full-k5": {"selected": "value", "k": 5, "value": 1, "repeat": 1},
    },
    "c3": {
        "original": {"selected": "dependency", "k": 0, "value": 0, "repeat": 0},
        "no-value": {"selected": "repeat", "k": 0, "value": 0, "repeat": 1},
        "full-k1": {"selected": "value", "k": 1, "value": 1, "repeat": 1},
        "full-k5": {"selected": "value", "k": 5, "value": 1, "repeat": 1},
    },
}

STATUSES = {
    "falsified",
    "budget_exhausted",
    "compile_error",
    "startup_error",
    "parser_error",
    "unknown_error",
    "incomplete",
}

def discover_repo_root() -> Path:
    explicit = os.environ.get("B5_REPO_ROOT")
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend([Path(__file__).resolve().parent.parent, Path.cwd()])
    for candidate in candidates:
        root = candidate.resolve()
        if (root / "configs" / "b5-controlled-scenarios.json").is_file():
            return root
    raise SystemExit("ERROR: repository root not found")

ROOT = discover_repo_root()
REGISTRY_PATH = ROOT / "configs" / "b5-controlled-scenarios.json"
ANALYZER_DIR = ROOT / "analyzer"
CONTRACT_FUZZ_BIN = Path("/home/skk/miniconda3/envs/contract-fuzz/bin")

def fail(message: str) -> None:
    raise SystemExit("ERROR: " + message)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="B5 controlled scenario runner")
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--method", required=True)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--budget", required=True, type=int)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--experiment-class", required=True, choices=("smoke", "formal"))
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()

def load_registry() -> dict[str, Any]:
    try:
        value = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"cannot load scenario registry: {error}")
    if not isinstance(value, dict):
        fail("scenario registry must be a JSON object")
    return value

def validate(args: argparse.Namespace, registry: dict[str, Any]) -> dict[str, Any]:
    if args.scenario not in METHODS or args.scenario not in registry:
        fail(f"unknown scenario {args.scenario}")
    if args.method not in METHODS[args.scenario]:
        fail("method not declared for scenario")
    if args.seed < 1 or args.budget < 1:
        fail("seed and budget must be positive")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", args.run_id):
        fail("unsafe run-id")
    spec = registry[args.scenario]
    for key in ("source_file", "contract_name", "property", "target_state_getter"):
        if not spec.get(key):
            fail(f"scenario registry missing {key}")
    if args.experiment_class == "formal" and not 1 <= args.seed <= 10:
        fail("formal seeds must be 1..10")
    return spec

def as_command(parts: list[Any]) -> list[str]:
    return [str(part) for part in parts]

def shell_command(parts: list[Any]) -> str:
    return shlex.join(as_command(parts))

def make_environment(args: argparse.Namespace, commit: str) -> dict[str, str]:
    environment = os.environ.copy()
    if CONTRACT_FUZZ_BIN.is_dir():
        environment["PATH"] = str(CONTRACT_FUZZ_BIN) + os.pathsep + environment.get("PATH", "")
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["B5_RUN_ID"] = args.run_id
    environment["B5_EXPERIMENT_CLASS"] = args.experiment_class
    environment["B5_GIT_SHA"] = commit
    return environment

def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.STDOUT
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"

def tool_version(command: list[str]) -> str:
    try:
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
        text = (result.stdout + result.stderr).strip().replace("\n", " | ")
        return text[:1000] if text else f"returncode={result.returncode}"
    except OSError as error:
        return f"unavailable: {error}"

def write_environment(path: Path, args: argparse.Namespace, commit: str) -> None:
    lines = [
        f"run_id={args.run_id}",
        f"experiment_class={args.experiment_class.upper()}",
        "paper_usable=false",
        f"scenario={args.scenario}",
        f"method={args.method}",
        f"seed={args.seed}",
        f"budget={args.budget}",
        f"git_commit={commit}",
        f"captured_at={datetime.now(timezone.utc).isoformat()}",
        f"python={tool_version([sys.executable, '--version'])}",
        f"solc={tool_version(['solc', '--version'])}",
        f"slither={tool_version(['slither', '--version'])}",
        f"echidna={tool_version(['echidna', '--version'])}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def write_manifest(path: Path, args: argparse.Namespace, status: str, complete: bool, checksum: str) -> None:
    fields = [
        "run_id", "experiment_class", "paper_usable", "scenario", "method",
        "seed", "budget", "status", "artifact_complete", "checksum_pass",
    ]
    row = [
        args.run_id,
        "SMOKE_ONLY" if args.experiment_class == "smoke" else "FORMAL",
        "false",
        args.scenario,
        args.method,
        str(args.seed),
        str(args.budget),
        status,
        str(complete).lower(),
        checksum,
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(fields)
        writer.writerow(row)

def write_status(path: Path, status: str, stage: str, args: argparse.Namespace, complete: bool, checksum: str) -> None:
    path.write_text(
        "\n".join(
            [
                f"STATUS={status}",
                f"FAILED_STAGE={stage}",
                f"EXPERIMENT_CLASS={'SMOKE_ONLY' if args.experiment_class == 'smoke' else 'FORMAL'}",
                "PAPER_USABLE=false",
                f"RUN_COMPLETED={int(complete)}",
                f"CHECKSUM_PASS={checksum}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

def write_command_log(path: Path, commands: list[list[str]]) -> None:
    path.write_text(
        "\n".join(shell_command(command) for command in commands) + "\n",
        encoding="utf-8",
    )

def run_logged(
    command: list[Any],
    commands: list[list[str]],
    stdout_path: Path,
    stderr_path: Path,
    environment: dict[str, str],
) -> None:
    normalized = as_command(command)
    commands.append(normalized)
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open(
        "w", encoding="utf-8"
    ) as stderr:
        subprocess.run(
            normalized, cwd=ROOT, env=environment, stdout=stdout, stderr=stderr, check=True
        )

def run_quiet(command: list[Any], commands: list[list[str]], environment: dict[str, str]) -> None:
    normalized = as_command(command)
    commands.append(normalized)
    subprocess.run(normalized, cwd=ROOT, env=environment, check=True)

def normalize_original_import(input_sol: Path, source: Path) -> None:
    relative = os.path.relpath(source.resolve(), input_sol.parent.resolve()).replace(os.sep, "/")
    text = input_sol.read_text(encoding="utf-8")
    updated, count = re.subn(r'(?m)^import\s+"[^"]+";', f'import "{relative}";', text, count=1)
    if count != 1:
        raise ValueError("original observer import was not found")
    input_sol.write_text(updated, encoding="utf-8")

def patch_metric_row(path: Path, args: argparse.Namespace, preprocess: float, compile_seconds: float) -> None:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 1:
        raise ValueError(f"metric collector returned {len(rows)} rows")
    row = rows[0]
    row["budget"] = str(args.budget)
    row["preprocess_seconds"] = f"{preprocess:.6f}"
    row["harness_compile_seconds"] = f"{compile_seconds:.6f}"
    row["artifact_complete"] = "false"
    row["checksum_pass"] = "pending"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row), delimiter="\t")
        writer.writeheader()
        writer.writerow(row)

def finalize_metric(path: Path, summary: Path, artifact_complete: bool, checksum: str) -> None:
    if not path.is_file():
        return
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 1:
        raise ValueError(f"metric collector returned {len(rows)} rows during finalization")
    row = rows[0]
    row["artifact_complete"] = str(artifact_complete).lower()
    row["checksum_pass"] = checksum
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row), delimiter="\t")
        writer.writeheader()
        writer.writerow(row)
    shutil.copyfile(path, summary)

def build_checksums(run_dir: Path) -> tuple[bool, str]:
    checksum_path = run_dir / "status" / "checksums.sha256"
    files = []
    for directory in ("generated", "raw", "parsed", "summary", "status"):
        for candidate in (run_dir / directory).rglob("*"):
            if candidate.is_file() and candidate.name not in {
                "checksums.sha256", "checksum-verification.txt"
            }:
                files.append(candidate)
    lines = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(ROOT).as_posix()}"
        for path in sorted(files)
    ]
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = subprocess.run(
        ["sha256sum", "-c", str(checksum_path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    (run_dir / "status" / "checksum-verification.txt").write_text(
        result.stdout + result.stderr, encoding="utf-8"
    )
    return result.returncode == 0, "pass" if result.returncode == 0 else "fail"

def main() -> int:
    args = parse_args()
    registry = load_registry()
    spec = validate(args, registry)
    output = ROOT / "work" / "v1-restart" / args.run_id
    if output.exists() or output.is_symlink():
        fail("run-id already exists: " + str(output))
    source = (ROOT / spec["source_file"]).resolve()
    if not source.is_file():
        fail("scenario source not found: " + str(source))
    if args.dry_run:
        print(f"scenario resolved: {args.scenario} {spec.get('scenario_name', '')}".rstrip())
        print(f"method resolved: {args.method}")
        print(f"seed/budget: {args.seed} {args.budget}")
        print(f"output: {output}")
        print("expected artifacts: manifest.tsv command.txt environment.txt generated/ raw/ parsed/ summary/ status/")
        print("planned commands: state-read, dependency, property, repeat, value, selection, instrumentation, solc, Echidna, metrics")
        print("dry-run: no execution performed")
        return 0
    if args.experiment_class == "formal" and os.environ.get("B5_MAIN_AUTHORIZED") != "1":
        fail("formal execution locked until B5-2")

    output.mkdir(parents=True)
    for directory in ("generated", "raw", "parsed", "summary", "status"):
        (output / directory).mkdir()
    generated = output / "generated"
    raw = output / "raw"
    parsed = output / "parsed"
    commands: list[list[str]] = []
    commit = git_sha()
    environment = make_environment(args, commit)
    write_environment(output / "environment.txt", args, commit)
    stage = "startup"
    status = "incomplete"
    preprocess_seconds = 0.0
    compile_seconds = 0.0

    try:
        run_quiet(["solc-select", "use", "0.8.20"], commands, environment)
        preprocess_start = time.monotonic()
        rw = generated / "rw.json"
        dependency = generated / "dependency.json"
        property_sequences = generated / "property.json"
        repeat = generated / "repeat.json"
        value = generated / "value.json"
        selected = generated / "selected.json"
        run_logged(
            [sys.executable, ANALYZER_DIR / "extract_rw.py", source],
            commands, rw, raw / "extract_rw.stderr", environment
        )
        run_logged(
            [sys.executable, ANALYZER_DIR / "generate_sequences.py", rw, spec["max_path_length"], spec["candidate_cap"]],
            commands, dependency, raw / "generate_sequences.stderr", environment
        )
        run_logged(
            [sys.executable, ANALYZER_DIR / "generate_property_sequences.py", rw, spec["max_path_length"], spec["candidate_cap"]],
            commands, property_sequences, raw / "generate_property_sequences.stderr", environment
        )
        run_logged(
            [
                sys.executable, ANALYZER_DIR / "generate_repetition_aware_sequences.py",
                rw, spec["max_path_length"], spec["candidate_cap"],
                "--contract", spec["contract_name"],
                "--max-function-visits", spec["max_function_visits"],
            ],
            commands, repeat, raw / "generate_repetition.stderr", environment
        )
        run_logged(
            [
                sys.executable, ANALYZER_DIR / "extract_value_constraints.py", source,
                "--contract", spec["contract_name"],
            ],
            commands, value, raw / "extract_value.stderr", environment
        )
        preprocess_seconds = time.monotonic() - preprocess_start
        method = METHODS[args.scenario][args.method]
        selected_sources = {
            "dependency": dependency,
            "property": property_sequences,
            "repeat": repeat,
        }
        if args.method in {"full-k1", "full-k5"}:
            stage = "value_guided_selection"
            run_logged(
                [
                    sys.executable, ANALYZER_DIR / "generate_value_guided_sequences.py",
                    repeat, value, "--contract", spec["contract_name"],
                    "--top-k", str(method["k"]),
                ],
                commands, selected, raw / "generate_value_guided.stderr", environment
            )
        else:
            stage = "selection"
            copy_source = selected_sources[method["selected"]]
            shutil.copyfile(copy_source, selected)
        target_contract = spec["contract_name"] + (
            "B5OriginalObserver" if args.method == "original"
            else "B5" + "".join(part.title() for part in args.method.split("-")) + "Harness"
        )
        input_sol = generated / "input.sol"
        instrument_start = time.monotonic()
        stage = "instrumentation"
        if args.method == "original":
            run_quiet(
                [
                    sys.executable, ANALYZER_DIR / "b5_controlled.py", "instrument",
                    "--kind", "original", "--source", source, "--output", input_sol,
                    "--contract", spec["contract_name"], "--getter", spec["target_state_getter"],
                ],
                commands, environment
            )
            normalize_original_import(input_sol, source)
        else:
            base_harness = generated / "base_harness.sol"
            run_quiet(
                [
                    sys.executable, ANALYZER_DIR / "generate_harness_from_paths.py",
                    "--source", source, "--sequences", selected,
                    "--target-contract", spec["contract_name"],
                    "--harness-contract", target_contract,
                    "--output", base_harness, "--prefix", "b5",
                    "--top-k", str(method["k"] if method["k"] else 5),
                ],
                commands, environment
            )
            run_quiet(
                [
                    sys.executable, ANALYZER_DIR / "b5_controlled.py", "instrument",
                    "--kind", "harness", "--source", base_harness, "--output", input_sol,
                    "--contract", spec["contract_name"], "--getter", spec["target_state_getter"],
                ],
                commands, environment
            )
        instrumentation_seconds = time.monotonic() - instrument_start
        config_source = ROOT / "configs" / (
            "b5-controlled-original.yaml" if args.method == "original"
            else "b5-controlled-harness.yaml"
        )
        config_text = config_source.read_text(encoding="utf-8")
        config_text, replacements = re.subn(
            r"(?m)^testLimit:\s*\d+\s*$", f"testLimit: {args.budget}", config_text
        )
        if replacements != 1:
            fail(f"expected one testLimit in {config_source}")
        config = generated / "echidna.yaml"
        config.write_text(config_text, encoding="utf-8")
        stage = "compile"
        compile_start = time.monotonic()
        compile_command = [
            "solc", "--base-path", str(ROOT), "--allow-paths", str(ROOT), str(input_sol)
        ]
        run_logged(compile_command, commands, raw / "solc.log", raw / "solc.stderr", environment)
        compile_seconds = time.monotonic() - compile_start
        stage = "echidna"
        echidna_command = [
            "/usr/bin/time", "-f", "PROCESS_WALL_SECONDS=%e", "echidna", str(input_sol),
            "--contract", target_contract, "--config", str(config), "--seed", str(args.seed),
        ]
        commands.append(as_command(echidna_command))
        with (raw / f"echidna-seed-{args.seed}.log").open("w", encoding="utf-8") as log:
            result = subprocess.run(
                as_command(echidna_command), cwd=ROOT, env=environment,
                stdout=log, stderr=subprocess.STDOUT, check=False
            )
        stage = "metrics"
        metric_output = parsed / "b5_run.tsv"
        collector = [
            sys.executable, ANALYZER_DIR / "b5_controlled.py", "collect",
            "--registry", REGISTRY_PATH, "--scenario", args.scenario,
            "--run-id", args.run_id, "--method", args.method, "--seed", str(args.seed),
            "--dependency", dependency, "--property-sequences", property_sequences,
            "--selected-sequences", selected, "--raw-log", raw / f"echidna-seed-{args.seed}.log",
            "--exit-code", str(result.returncode), "--k", str(method["k"]),
            "--value-enabled", str(method["value"]), "--repeat-enabled", str(method["repeat"]),
            "--checksum-pass", "pending", "--output", metric_output,
        ]
        run_quiet(collector, commands, environment)
        patch_metric_row(metric_output, args, preprocess_seconds + instrumentation_seconds, compile_seconds)
        shutil.copyfile(metric_output, output / "summary" / "b5_summary.tsv")
        with metric_output.open("r", encoding="utf-8", newline="") as handle:
            metric_row = next(csv.DictReader(handle, delimiter="\t"))
        status = metric_row.get("status", "unknown_error")
        if status not in STATUSES:
            status = "parser_error"
        stage = "completed"
    except subprocess.CalledProcessError as error:
        if stage == "compile":
            status = "compile_error"
        elif stage == "metrics":
            status = "parser_error"
        else:
            status = "startup_error"
        (raw / "runner-error.txt").write_text(
            f"stage={stage}\nreturncode={error.returncode}\n", encoding="utf-8"
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        status = "unknown_error"
        (raw / "runner-error.txt").write_text(
            f"stage={stage}\nerror={error}\n", encoding="utf-8"
        )

    complete = status in {"falsified", "budget_exhausted"}
    write_command_log(output / "command.txt", commands)
    checksum_value = "pending"
    write_manifest(output / "manifest.tsv", args, status, complete, checksum_value)
    write_status(output / "status" / "status.env", status, stage, args, complete, checksum_value)
    checksum_ok, checksum_value = build_checksums(output)
    if checksum_ok:
        try:
            finalize_metric(
                output / "parsed" / "b5_run.tsv",
                output / "summary" / "b5_summary.tsv",
                True,
                checksum_value,
            )
            checksum_ok, checksum_value = build_checksums(output)
        except (OSError, ValueError, csv.Error) as error:
            checksum_ok = False
            checksum_value = "fail"
            (output / "raw" / "runner-error.txt").write_text(
                f"stage=metric_finalization\nerror={error}\n", encoding="utf-8"
            )
    if checksum_ok:
        write_manifest(output / "manifest.tsv", args, status, complete, checksum_value)
        write_status(output / "status" / "status.env", status, stage, args, complete, checksum_value)
    else:
        status = "unknown_error"
        complete = False
        write_manifest(output / "manifest.tsv", args, status, complete, checksum_value)
        write_status(output / "status" / "status.env", status, stage, args, complete, checksum_value)
    print(f"run finished: {output} {status}")
    return 0 if status in {"falsified", "budget_exhausted"} else 1

if __name__ == "__main__":
    raise SystemExit(main())
