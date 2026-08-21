#!/usr/bin/env python3
"""Run the frozen matched-random V1 manifest against local benchmark files."""

from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


COMPLETION_MARKER = "MATCHED_RANDOM_RUN_COMPLETED=1"
PROPERTY_DECLARATION = re.compile(r"\bfunction\s+(echidna_[A-Za-z0-9_]+)\s*\(")
FAILED_RESULT = re.compile(
    r"(?:Test\s+)?(echidna_[A-Za-z0-9_]+)\s*(?::\s*|\s+)"
    r"(?:failed|falsified)!?",
    re.IGNORECASE,
)
PASSED_RESULT = re.compile(
    r"(echidna_[A-Za-z0-9_]+)\s*:\s*(?:passed|passing)!?",
    re.IGNORECASE,
)
STARTUP_ERROR_PATTERNS = (
    r"compilation failed",
    r"ParserError",
    r"File outside of allowed directories",
    r"Source .* not found",
    r"Config .* not found",
    r"Could not compile",
    r"crytic-compile .* (?:error|failed)",
    r"solc: not found",
)


@dataclass(frozen=True)
class RunCase:
    cohort: str
    benchmark: str
    method: str
    fuzz_seed: int
    schedule_seed: str
    selection_id: str
    selected_candidate_indices: str
    selection_sha256: str
    harness_file: Path
    harness_contract: str
    compiler: str
    config_file: Path
    semantic_classification: str


@dataclass(frozen=True)
class RunResult:
    case: RunCase
    status: str
    output_path: Path
    skipped: bool
    wall_seconds: float


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=repo_root / "results/matched-random-v1/execution-manifest.tsv",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=repo_root / "results/matched-random-v1/runs",
    )
    parser.add_argument("--repo-root", type=Path, default=repo_root)
    parser.add_argument(
        "--compiler-root",
        type=Path,
        required=True,
        help="Directory containing solc-VERSION/solc-VERSION artifacts.",
    )
    parser.add_argument(
        "--tool-bin",
        type=Path,
        default=Path(sys.executable).resolve().parent,
        help="Directory containing local analysis dependencies.",
    )
    parser.add_argument(
        "--echidna",
        type=Path,
        default=Path(shutil.which("echidna") or "echidna"),
        help="Path to the local Echidna executable.",
    )
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--only-benchmark", action="append", default=[])
    parser.add_argument("--only-seed", action="append", type=int, default=[])
    parser.add_argument("--test-limit-override", type=int)
    parser.add_argument("--run-mode", choices=("formal", "smoke"), default="formal")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def load_manifest(path: Path, repo_root: Path) -> list[RunCase]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {field.name for field in RunCase.__dataclass_fields__.values()}
        if not reader.fieldnames or set(reader.fieldnames) != required:
            raise ValueError(
                f"manifest columns differ from the frozen schema: {reader.fieldnames}"
            )

        cases = []
        seen = set()
        for row in reader:
            key = (row["benchmark"], int(row["fuzz_seed"]))
            if key in seen:
                raise ValueError(f"duplicate benchmark/seed row: {key}")
            seen.add(key)
            case = RunCase(
                cohort=row["cohort"],
                benchmark=row["benchmark"],
                method=row["method"],
                fuzz_seed=int(row["fuzz_seed"]),
                schedule_seed=row["schedule_seed"],
                selection_id=row["selection_id"],
                selected_candidate_indices=row["selected_candidate_indices"],
                selection_sha256=row["selection_sha256"],
                harness_file=repo_root / row["harness_file"],
                harness_contract=row["harness_contract"],
                compiler=row["compiler"],
                config_file=repo_root / row["config_file"],
                semantic_classification=row["semantic_classification"],
            )
            cases.append(case)

    if not cases:
        raise ValueError("execution manifest is empty")
    return cases


def expected_properties(harness_file: Path) -> set[str]:
    text = harness_file.read_text(encoding="utf-8")
    properties = set(PROPERTY_DECLARATION.findall(text))
    if not properties:
        raise ValueError(f"no echidna property found in {harness_file}")
    return properties


def classify_output(text: str, exit_code: int, expected: set[str]) -> str:
    if any(
        re.search(pattern, text, flags=re.IGNORECASE)
        for pattern in STARTUP_ERROR_PATTERNS
    ):
        return "startup_error"

    failed = set(FAILED_RESULT.findall(text))
    passed = set(PASSED_RESULT.findall(text))
    observed = failed | passed
    if not expected.issubset(observed):
        return "incomplete"
    if failed:
        return "falsified"
    # Echidna exits with status 1 when it finds a falsified property.
    # A non-zero exit code is only a startup error after the property
    # result has been checked; otherwise every valid counterexample is
    # misclassified as a failed launch.
    if exit_code != 0:
        return "startup_error"
    if re.search(r"Test limit reached\. Stopping\.", text, flags=re.IGNORECASE):
        return "budget_exhausted"
    if passed:
        return "passed"
    return "incomplete"


def compiler_path(compiler_root: Path, version: str) -> Path:
    return compiler_root / f"solc-{version}" / f"solc-{version}"


def output_path(output_root: Path, case: RunCase) -> Path:
    return output_root / case.benchmark / case.method / f"seed-{case.fuzz_seed}.log"


def is_complete(path: Path) -> bool:
    if not path.is_file():
        return False
    return COMPLETION_MARKER in path.read_text(encoding="utf-8", errors="ignore")


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def run_case(
    case: RunCase,
    *,
    repo_root: Path,
    output_root: Path,
    compiler_root: Path,
    tool_bin: Path,
    echidna_path: Path,
    run_mode: str,
    force: bool,
    test_limit_override: int | None,
) -> RunResult:
    destination = output_path(output_root, case)
    if not force and is_complete(destination):
        return RunResult(case, "completed", destination, True, 0.0)

    properties = expected_properties(case.harness_file)
    selected_compiler = compiler_path(compiler_root, case.compiler)
    if not selected_compiler.is_file():
        raise FileNotFoundError(f"compiler not found: {selected_compiler}")
    for required_path in (case.harness_file, case.config_file):
        if not required_path.is_file():
            raise FileNotFoundError(required_path)

    command = [
        str(echidna_path),
        str(case.harness_file.relative_to(repo_root)),
        "--contract",
        case.harness_contract,
        "--config",
        str(case.config_file.relative_to(repo_root)),
        "--seed",
        str(case.fuzz_seed),
        "--disable-onchain-sources",
        "--crytic-args",
        f"--solc={selected_compiler}",
    ]
    if test_limit_override is not None:
        command.extend(("--test-limit", str(test_limit_override)))

    environment = os.environ.copy()
    environment["PATH"] = str(tool_bin) + os.pathsep + environment.get("PATH", "")
    started_at = iso_now()
    start = time.monotonic()
    process = subprocess.run(
        command,
        cwd=repo_root,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    wall_seconds = time.monotonic() - start
    status = classify_output(process.stdout, process.returncode, properties)

    metadata = [
        "MATCHED_RANDOM_EXPERIMENT_VERSION=Full-v1.0-matched-random-control",
        f"RUN_MODE={run_mode}",
        f"COHORT={case.cohort}",
        f"BENCHMARK={case.benchmark}",
        f"METHOD={case.method}",
        f"SEED={case.fuzz_seed}",
        f"SCHEDULE_SEED={case.schedule_seed}",
        f"SELECTION_ID={case.selection_id}",
        f"SELECTED_CANDIDATE_INDICES={case.selected_candidate_indices}",
        f"SELECTION_SHA256={case.selection_sha256}",
        f"CONTRACT_FILE={case.harness_file.relative_to(repo_root)}",
        f"CONTRACT_NAME={case.harness_contract}",
        f"COMPILER_VERSION={case.compiler}",
        f"COMPILER_PATH={selected_compiler}",
        f"CONFIG_FILE={case.config_file.relative_to(repo_root)}",
        f"SEMANTIC_CLASSIFICATION={case.semantic_classification}",
        f"EXPECTED_PROPERTIES={','.join(sorted(properties))}",
        f"TEST_LIMIT_OVERRIDE={test_limit_override or ''}",
        f"START_TIME={started_at}",
        "",
    ]
    trailer = [
        "",
        f"EXIT_CODE={process.returncode}",
        f"END_TIME={iso_now()}",
        f"PROCESS_WALL_SECONDS={wall_seconds:.6f}",
        f"MATCHED_RANDOM_RUN_STATUS={status}",
    ]
    if status in {"falsified", "budget_exhausted", "passed"}:
        trailer.append(COMPLETION_MARKER)

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + f".tmp-{os.getpid()}")
    temporary.write_text(
        "\n".join(metadata) + process.stdout + "\n".join(trailer) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, destination)
    return RunResult(case, status, destination, False, wall_seconds)


def validate_environment(
    cases: list[RunCase], compiler_root: Path, tool_bin: Path, echidna_path: Path
) -> None:
    if not os.access(echidna_path, os.X_OK):
        raise FileNotFoundError(f"echidna is not executable: {echidna_path}")
    for tool in ("crytic-compile", "slither"):
        if not shutil.which(tool, path=str(tool_bin)):
            raise FileNotFoundError(f"{tool} not found under {tool_bin}")
    for version in sorted({case.compiler for case in cases}):
        path = compiler_path(compiler_root, version)
        if not os.access(path, os.X_OK):
            raise FileNotFoundError(f"compiler is not executable: {path}")


def main() -> int:
    args = parse_args()
    if args.jobs < 1:
        raise ValueError("--jobs must be positive")
    if args.test_limit_override is not None and args.run_mode != "smoke":
        raise ValueError("a test-limit override is allowed only in smoke mode")

    repo_root = args.repo_root.resolve()
    cases = load_manifest(args.manifest.resolve(), repo_root)
    if args.only_benchmark:
        allowed = set(args.only_benchmark)
        cases = [case for case in cases if case.benchmark in allowed]
    if args.only_seed:
        allowed_seeds = set(args.only_seed)
        cases = [case for case in cases if case.fuzz_seed in allowed_seeds]
    if args.limit is not None:
        cases = cases[: args.limit]
    if not cases:
        raise ValueError("filters selected zero manifest rows")

    validate_environment(
        cases,
        args.compiler_root.resolve(),
        args.tool_bin.resolve(),
        args.echidna.resolve(),
    )
    print(f"Selected {len(cases)} frozen runs; jobs={args.jobs}; mode={args.run_mode}")
    if args.dry_run:
        for case in cases:
            print(f"DRY-RUN {case.benchmark}/seed-{case.fuzz_seed}")
        return 0

    results = []
    kwargs = {
        "repo_root": repo_root,
        "output_root": args.output_root.resolve(),
        "compiler_root": args.compiler_root.resolve(),
        "tool_bin": args.tool_bin.resolve(),
        "echidna_path": args.echidna.resolve(),
        "run_mode": args.run_mode,
        "force": args.force,
        "test_limit_override": args.test_limit_override,
    }
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = {executor.submit(run_case, case, **kwargs): case for case in cases}
        for index, future in enumerate(as_completed(futures), start=1):
            result = future.result()
            results.append(result)
            disposition = "skip" if result.skipped else result.status
            print(
                f"[{index}/{len(cases)}] {result.case.benchmark}/"
                f"seed-{result.case.fuzz_seed}: {disposition} "
                f"({result.wall_seconds:.2f}s)",
                flush=True,
            )

    counts = {}
    for result in results:
        counts[result.status] = counts.get(result.status, 0) + 1
    print("Summary: " + ", ".join(f"{key}={counts[key]}" for key in sorted(counts)))
    return 1 if any(key in counts for key in ("startup_error", "incomplete")) else 0


if __name__ == "__main__":
    raise SystemExit(main())
