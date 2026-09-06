#!/usr/bin/env bash

set -euo pipefail

usage() {
    cat >&2 <<'USAGE'
Usage:
  bash scripts/run_v1_restart_case.sh --run-id <run_id> [--benchmark <benchmark>] --method original --seed <seed> [--dry-run]
  bash scripts/run_v1_restart_case.sh --run-id <run_id> [--benchmark <benchmark>] --method full-k1 --seed <seed> [--dry-run]
USAGE
}

fail() {
    printf 'Error: %s\n' "$1" >&2
    exit 2
}

RUN_ID=""
BENCHMARK="noisy-four-step"
METHOD=""
SEED=""
DRY_RUN=0

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --run-id)
            [[ "$#" -ge 2 ]] || fail "--run-id requires a value"
            RUN_ID="$2"
            shift 2
            ;;
        --benchmark)
            [[ "$#" -ge 2 ]] || fail "--benchmark requires a value"
            BENCHMARK="$2"
            shift 2
            ;;
        --method)
            [[ "$#" -ge 2 ]] || fail "--method requires a value"
            METHOD="$2"
            shift 2
            ;;
        --seed)
            [[ "$#" -ge 2 ]] || fail "--seed requires a value"
            SEED="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            fail "unknown option: $1"
            ;;
    esac
done

[[ -n "$RUN_ID" ]] || fail "--run-id is required"
[[ -n "$METHOD" ]] || fail "--method is required"
[[ -n "$SEED" ]] || fail "--seed is required"
[[ "$RUN_ID" =~ ^[A-Za-z0-9._-]+$ ]] || fail "run-id contains unsafe characters"

case "$METHOD" in
    original|full-k1)
        ;;
    *)
        fail "method must be original or full-k1"
        ;;
esac


case "$BENCHMARK" in
    noisy-four-step)
        CONTRACT_FILE="contracts/benchmarks/NoisyFourStepExample.sol"
        CONTRACT_NAME="NoisyFourStepExample"
        ;;
    reset-example)
        CONTRACT_FILE="contracts/benchmarks/ResetExample.sol"
        CONTRACT_NAME="ResetExample"
        ;;
    branch-value)
        CONTRACT_FILE="contracts/benchmarks/BranchValueExample.sol"
        CONTRACT_NAME="BranchValueExample"
        ;;
    repeated-call)
        CONTRACT_FILE="contracts/benchmarks/RepeatedCallExample.sol"
        CONTRACT_NAME="RepeatedCallExample"
        ;;
    *)
        fail "benchmark must be noisy-four-step, reset-example, branch-value, or repeated-call"
        ;;
esac

PROPERTY="echidna_value_safe"
ORIGINAL_CONFIG_FILE="configs/formal-original-seq4.yaml"
HARNESS_CONFIG_FILE="configs/formal-harness-seq1.yaml"
TEST_LIMIT=100000
TIMEOUT=30
WORKERS=1
STOP_ON_FAIL=true
METHOD_VERSION="Full-v1.0-restart-benchmark-v1"
if [[ "$METHOD" == "original" ]]; then
    CONFIG_FILE="$ORIGINAL_CONFIG_FILE"
else
    CONFIG_FILE="$HARNESS_CONFIG_FILE"
fi
HARNESS_NAME="${CONTRACT_NAME}FullK1RestartHarness"
if [[ "$BENCHMARK" == "noisy-four-step" ]]; then
    HARNESS_NAME="NoisyFourStepFullK1RestartHarness"
fi

[[ "$SEED" =~ ^[1-9][0-9]*$ ]] || fail "seed must be a positive integer"

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(bash "$SCRIPT_DIR/resolve_repo_root.sh")"
REPO_ROOT="$(readlink -f -- "$REPO_ROOT")"
cd "$REPO_ROOT"

EXPECTED_REPO_ROOT="$(git -C "$REPO_ROOT" rev-parse --show-toplevel 2>/dev/null)" || {
    fail "repository root could not be verified"
}
EXPECTED_REPO_ROOT="$(readlink -f -- "$EXPECTED_REPO_ROOT")"
[[ "$EXPECTED_REPO_ROOT" == "$REPO_ROOT" ]] || fail "repository root verification failed"

WORK_ROOT="$REPO_ROOT/work"
if [[ -L "$WORK_ROOT" ]]; then
    fail "work must not be a symlink"
fi
if [[ -e "$WORK_ROOT" && ! -d "$WORK_ROOT" ]]; then
    fail "work is not a directory"
fi
mkdir -p "$WORK_ROOT"

RESTART_ROOT="$WORK_ROOT/v1-restart"
if [[ -L "$RESTART_ROOT" ]]; then
    fail "work/v1-restart must not be a symlink"
fi
if [[ -e "$RESTART_ROOT" && ! -d "$RESTART_ROOT" ]]; then
    fail "work/v1-restart is not a directory"
fi
mkdir -p "$RESTART_ROOT"
RESOLVED_RESTART_ROOT="$(readlink -f -- "$RESTART_ROOT")"
[[ "$RESOLVED_RESTART_ROOT" == "$REPO_ROOT/work/v1-restart" ]] || {
    fail "work/v1-restart resolved outside the repository"
}

OUTPUT_ROOT="$RESTART_ROOT/$RUN_ID"
RESOLVED_OUTPUT_ROOT="$(readlink -f -- "$OUTPUT_ROOT")"
if [[ "$RESOLVED_OUTPUT_ROOT" == "$RESOLVED_RESTART_ROOT" ||
      "$RESOLVED_OUTPUT_ROOT" != "$RESOLVED_RESTART_ROOT/"* ]]; then
    fail "output root is outside work/v1-restart"
fi
if [[ -e "$OUTPUT_ROOT" || -L "$OUTPUT_ROOT" ]]; then
    fail "run-id already exists; refusing to overwrite: $OUTPUT_ROOT"
fi
if ! mkdir "$OUTPUT_ROOT"; then
    fail "run-id was created concurrently; refusing to overwrite: $OUTPUT_ROOT"
fi
mkdir -p \
    "$OUTPUT_ROOT/generated" \
    "$OUTPUT_ROOT/raw" \
    "$OUTPUT_ROOT/parsed" \
    "$OUTPUT_ROOT/summary" \
    "$OUTPUT_ROOT/status"

STATUS_FILE="$OUTPUT_ROOT/status/status.env"
START_TIME="$(date --iso-8601=seconds)"

startup_fail() {
    printf 'Error: %s\n' "$1" >&2
    {
        printf 'DRY_RUN=%s\n' "$DRY_RUN"
        printf 'STATUS=startup_error\n'
        printf 'RUN_COMPLETED=0\n'
        printf 'EXIT_CODE=1\n'
        printf 'START_TIME=%s\n' "$START_TIME"
        printf 'END_TIME=%s\n' "$(date --iso-8601=seconds)"
        printf 'ERROR=%s\n' "$1"
    } > "$STATUS_FILE"
    exit 1
}

CONDA_PREFIX_VALUE="$(printenv CONDA_PREFIX || true)"
CONDA_DEFAULT_ENV_VALUE="$(printenv CONDA_DEFAULT_ENV || true)"
[[ -n "$CONDA_PREFIX_VALUE" ]] || startup_fail "CONDA_PREFIX is not set; activate contract-fuzz first"
[[ "$CONDA_DEFAULT_ENV_VALUE" == "contract-fuzz" ]] || {
    startup_fail "active Conda environment must be contract-fuzz"
}
[[ -d "$CONDA_PREFIX_VALUE" ]] || startup_fail "CONDA_PREFIX is not a directory"

export PATH="$CONDA_PREFIX_VALUE/bin:$PATH"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPYCACHEPREFIX="$OUTPUT_ROOT/generated/pycache"

for command_name in python slither solc echidna git
do
    command -v "$command_name" >/dev/null 2>&1 || {
        startup_fail "required command not found: $command_name"
    }
done

[[ -f "$CONTRACT_FILE" ]] || startup_fail "contract not found: $CONTRACT_FILE"
[[ -f "$CONFIG_FILE" ]] || startup_fail "config not found: $CONFIG_FILE"

HARNESS_FILE="$OUTPUT_ROOT/generated/$HARNESS_NAME.sol"
RW_JSON="$OUTPUT_ROOT/generated/rw.json"
REPEAT_JSON="$OUTPUT_ROOT/generated/repeat-property-sequences.json"
VALUE_JSON="$OUTPUT_ROOT/generated/value-constraints.json"
FULL_JSON="$OUTPUT_ROOT/generated/full-sequences.json"
RAW_LOG="$OUTPUT_ROOT/raw/seed-$SEED.log"
COMMAND_FILE="$OUTPUT_ROOT/command.txt"
ENVIRONMENT_FILE="$OUTPUT_ROOT/environment.txt"

COMMIT_SHA="$(git rev-parse HEAD 2>/dev/null)" || startup_fail "unable to read Git commit"
GIT_BRANCH="$(git branch --show-current 2>/dev/null)" || startup_fail "unable to read Git branch"

if [[ "$DRY_RUN" -eq 1 ]]; then
    PYTHON_VERSION="not_run_dry_run"
    SLITHER_VERSION="not_run_dry_run"
    SOLC_VERSION="not_run_dry_run"
    ECHIDNA_VERSION="not_run_dry_run"
    SOLC_SELECT_VERSIONS="not_run_dry_run"
    VERSION_CHECK_NOTE="dry-run skips version command execution"
else
    PYTHON_VERSION="$(python --version 2>&1 | tr '\n' ' ')" || startup_fail "python version check failed"
    SLITHER_VERSION="$(slither --version 2>&1 | tr '\n' ' ')" || startup_fail "slither version check failed"
    SOLC_VERSION="$(solc --version 2>&1 | tr '\n' ' ')" || startup_fail "solc version check failed"
    ECHIDNA_VERSION="$(echidna --version 2>&1 | tr '\n' ' ')" || startup_fail "echidna version check failed"
    SOLC_SELECT_VERSIONS="$(solc-select versions 2>&1 | tr '\n' '; ' || true)"
    VERSION_CHECK_NOTE="version commands executed"
fi

{
    printf 'REPO_ROOT=%s\n' "$REPO_ROOT"
    printf 'RUN_ID=%s\n' "$RUN_ID"
    printf 'BENCHMARK=%s\n' "$BENCHMARK"
    printf 'METHOD_VERSION=%s\n' "$METHOD_VERSION"
    printf 'METHOD=%s\n' "$METHOD"
    printf 'SEED=%s\n' "$SEED"
    printf 'DRY_RUN=%s\n' "$DRY_RUN"
    printf 'GIT_BRANCH=%s\n' "$GIT_BRANCH"
    printf 'COMMIT_SHA=%s\n' "$COMMIT_SHA"
    printf 'CONDA_DEFAULT_ENV=%s\n' "$CONDA_DEFAULT_ENV_VALUE"
    printf 'CONDA_PREFIX=%s\n' "$CONDA_PREFIX_VALUE"
    printf 'CONTRACT_FILE=%s\n' "$CONTRACT_FILE"
    printf 'CONTRACT_NAME=%s\n' "$CONTRACT_NAME"
    printf 'PROPERTY=%s\n' "$PROPERTY"
    printf 'CONFIG_FILE=%s\n' "$CONFIG_FILE"
    printf 'TEST_LIMIT=%s\n' "$TEST_LIMIT"
    printf 'TIMEOUT=%s\n' "$TIMEOUT"
    printf 'WORKERS=%s\n' "$WORKERS"
    printf 'STOP_ON_FAIL=%s\n' "$STOP_ON_FAIL"
    printf 'PYTHON=%s\n' "$(command -v python)"
    printf 'SLITHER=%s\n' "$(command -v slither)"
    printf 'SOLC=%s\n' "$(command -v solc)"
    printf 'ECHIDNA=%s\n' "$(command -v echidna)"
    printf 'GIT=%s\n' "$(command -v git)"
    printf 'PYTHON_VERSION=%s\n' "$PYTHON_VERSION"
    printf 'SLITHER_VERSION=%s\n' "$SLITHER_VERSION"
    printf 'SOLC_VERSION=%s\n' "$SOLC_VERSION"
    printf 'ECHIDNA_VERSION=%s\n' "$ECHIDNA_VERSION"
    printf 'SOLC_SELECT_VERSIONS=%s\n' "$SOLC_SELECT_VERSIONS"
    printf 'VERSION_CHECK_NOTE=%s\n' "$VERSION_CHECK_NOTE"
} > "$ENVIRONMENT_FILE"

{
    printf 'cd -- %q\n' "$REPO_ROOT"
    if [[ "$METHOD" == "original" ]]; then
        printf 'echidna %q --contract %q --config %q --seed %q\n' \
            "$CONTRACT_FILE" "$CONTRACT_NAME" "$CONFIG_FILE" "$SEED"
    else
        printf 'python analyzer/extract_rw.py %q > %q\n' \
            "$CONTRACT_FILE" "$RW_JSON"
        printf 'python analyzer/generate_repetition_aware_sequences.py %q 4 500 --contract %q --max-function-visits 2 > %q\n' \
            "$RW_JSON" "$CONTRACT_NAME" "$REPEAT_JSON"
        printf 'python analyzer/extract_value_constraints.py %q --contract %q > %q\n' \
            "$CONTRACT_FILE" "$CONTRACT_NAME" "$VALUE_JSON"
        printf 'python analyzer/generate_value_guided_sequences.py %q %q --contract %q > %q\n' \
            "$REPEAT_JSON" "$VALUE_JSON" "$CONTRACT_NAME" "$FULL_JSON"
        printf 'python analyzer/generate_harness_from_paths.py --source %q --sequences %q --target-contract %q --harness-contract %q --output %q --prefix full --top-k 1\n' \
            "$CONTRACT_FILE" "$FULL_JSON" "$CONTRACT_NAME" "$HARNESS_NAME" "$HARNESS_FILE"
        printf 'solc --bin %q\n' "$HARNESS_FILE"
        printf 'echidna %q --contract %q --config %q --seed %q\n' \
            "$HARNESS_FILE" "$HARNESS_NAME" "$CONFIG_FILE" "$SEED"
    fi
} > "$COMMAND_FILE"

if grep -Eq 'results/formal|results/formal-b2|results/public-benchmarks|results/paper-data|contracts/harnesses/formal' "$COMMAND_FILE"; then
    startup_fail "planned command leaks into a frozen output path"
fi

{
    printf 'run_id\tcommit_sha\tmethod_version\tbenchmark\tmethod\tcontract_file\tcontract_name\tproperty\tconfig_file\tseed\ttest_limit\ttimeout\tworkers\tstop_on_fail\tpython_version\tslither_version\tsolc_version\techidna_version\toutput_root\tstart_time\n'
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$RUN_ID" "$COMMIT_SHA" "$METHOD_VERSION" "$BENCHMARK" "$METHOD" \
        "$CONTRACT_FILE" "$CONTRACT_NAME" "$PROPERTY" "$CONFIG_FILE" "$SEED" \
        "$TEST_LIMIT" "$TIMEOUT" "$WORKERS" "$STOP_ON_FAIL" \
        "$PYTHON_VERSION" "$SLITHER_VERSION" "$SOLC_VERSION" "$ECHIDNA_VERSION" \
        "$OUTPUT_ROOT" "$START_TIME"
} > "$OUTPUT_ROOT/manifest.tsv"

write_checksums() {
    sha256sum -- "$CONTRACT_FILE" "$CONFIG_FILE"
    if [[ "$METHOD" == "full-k1" ]]; then
        for path in "$RW_JSON" "$REPEAT_JSON" "$VALUE_JSON" "$FULL_JSON" "$HARNESS_FILE"
        do
            if [[ -f "$path" ]]; then
                sha256sum -- "$path"
            else
                printf 'MISSING  %s\n' "$path"
            fi
        done
    fi
    sha256sum -- "$RAW_LOG"
}

write_status() {
    local status_value="$1"
    local exit_code="$2"
    local run_completed="$3"
    local end_time="$4"
    local failed_stage_value="none"
    if [[ -n "$FAILED_STAGE" ]]; then
        failed_stage_value="$FAILED_STAGE"
    fi
    {
        printf 'DRY_RUN=%s\n' "$DRY_RUN"
        printf 'STATUS=%s\n' "$status_value"
        printf 'RUN_COMPLETED=%s\n' "$run_completed"
        printf 'EXIT_CODE=%s\n' "$exit_code"
        printf 'START_TIME=%s\n' "$START_TIME"
        printf 'END_TIME=%s\n' "$end_time"
        printf 'FAILED_STAGE=%s\n' "$failed_stage_value"
    } > "$STATUS_FILE"
}

if [[ "$DRY_RUN" -eq 1 ]]; then
    END_TIME="$(date --iso-8601=seconds)"
    FAILED_STAGE="none"
    write_status "dry_run" 0 0 "$END_TIME"
    printf 'Dry-run prepared: %s\n' "$OUTPUT_ROOT"
    exit 0
fi

run_pipeline() {
    if [[ "$METHOD" == "original" ]]; then
        FAILED_STAGE="echidna"
        echidna "$CONTRACT_FILE" \
            --contract "$CONTRACT_NAME" \
            --config "$CONFIG_FILE" \
            --seed "$SEED"
        return
    fi

    FAILED_STAGE="extract_rw"
    python analyzer/extract_rw.py "$CONTRACT_FILE" > "$RW_JSON" || return 1
    FAILED_STAGE="repeat_generation"
    python analyzer/generate_repetition_aware_sequences.py \
        "$RW_JSON" 4 500 --contract "$CONTRACT_NAME" --max-function-visits 2 \
        > "$REPEAT_JSON" || return 1
    FAILED_STAGE="value_extraction"
    python analyzer/extract_value_constraints.py \
        "$CONTRACT_FILE" --contract "$CONTRACT_NAME" > "$VALUE_JSON" || return 1
    FAILED_STAGE="value_guided_generation"
    python analyzer/generate_value_guided_sequences.py \
        "$REPEAT_JSON" "$VALUE_JSON" --contract "$CONTRACT_NAME" \
        > "$FULL_JSON" || return 1
    FAILED_STAGE="harness_generation"
    python analyzer/generate_harness_from_paths.py \
        --source "$CONTRACT_FILE" \
        --sequences "$FULL_JSON" \
        --target-contract "$CONTRACT_NAME" \
        --harness-contract "$HARNESS_NAME" \
        --output "$HARNESS_FILE" \
        --prefix full \
        --top-k 1 || return 1
    FAILED_STAGE="solc"
    solc --bin "$HARNESS_FILE" || return 1
    FAILED_STAGE="echidna"
    echidna "$HARNESS_FILE" \
        --contract "$HARNESS_NAME" \
        --config "$CONFIG_FILE" \
        --seed "$SEED"
}

: > "$RAW_LOG"
{
    printf 'RUN_ID=%s\n' "$RUN_ID"
    printf 'BENCHMARK=%s\n' "$BENCHMARK"
    printf 'METHOD=%s\n' "$METHOD"
    printf 'SEED=%s\n' "$SEED"
    printf 'START_TIME=%s\n' "$START_TIME"
} >> "$RAW_LOG"

set +e
run_pipeline >> "$RAW_LOG" 2>&1
EXIT_CODE="$?"
set -e

END_TIME="$(date --iso-8601=seconds)"
{
    printf 'EXIT_CODE=%s\n' "$EXIT_CODE"
    printf 'END_TIME=%s\n' "$END_TIME"
} >> "$RAW_LOG"

STATUS_VALUE="unknown_error"
if [[ "$FAILED_STAGE" == "echidna" ]]; then
    if grep -Eiq 'falsified|property[[:space:][:punct:]]*failed|assertion[[:space:][:punct:]]*failed|failed!' "$RAW_LOG"; then
        STATUS_VALUE="completed"
    elif [[ "$EXIT_CODE" -eq 0 ]]; then
        STATUS_VALUE="completed"
    elif grep -Eiq 'test limit|testLimit|budget.exhaust|time limit|timed out' "$RAW_LOG"; then
        STATUS_VALUE="budget_exhausted"
    fi
fi

RUN_COMPLETED=0
if [[ "$STATUS_VALUE" == "completed" ||
      "$STATUS_VALUE" == "budget_exhausted" ]]; then
    RUN_COMPLETED=1
fi

write_status "$STATUS_VALUE" "$EXIT_CODE" "$RUN_COMPLETED" "$END_TIME"
(
    cd "$REPO_ROOT"
    write_checksums
) > "$OUTPUT_ROOT/status/checksums.sha256"

printf 'Run finished: %s (%s)\n' "$OUTPUT_ROOT" "$STATUS_VALUE"
[[ "$STATUS_VALUE" != "unknown_error" ]]
