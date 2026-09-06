#!/usr/bin/env bash

set -euo pipefail

usage() {
    cat >&2 <<'USAGE'
Usage:
  bash scripts/run_v1_public_smoke_case.sh --mode preflight --benchmark <benchmark_id>
  bash scripts/run_v1_public_smoke_case.sh --mode smoke --run-id <run_id> --benchmark <benchmark_id> --method <original|full-k1|full-k5> --seed 1
USAGE
}

fail() {
    printf 'Error: %s\n' "$1" >&2
    exit 2
}

MODE=""
RUN_ID=""
BENCHMARK=""
METHOD=""
SEED=""

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --mode)
            [[ "$#" -ge 2 ]] || fail "--mode requires a value"
            MODE="$2"
            shift 2
            ;;
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
        --help|-h)
            usage
            exit 0
            ;;
        *)
            fail "unknown option: $1"
            ;;
    esac
done

[[ "$MODE" == "preflight" || "$MODE" == "smoke" ]] || fail "--mode must be preflight or smoke"
[[ -n "$BENCHMARK" ]] || fail "--benchmark is required"
if [[ "$MODE" == "preflight" ]]; then
    [[ -z "$RUN_ID" && -z "$METHOD" && -z "$SEED" ]] || fail "preflight does not accept run-id, method, or seed"
else
    [[ -n "$RUN_ID" ]] || fail "--run-id is required for smoke"
    [[ "$RUN_ID" =~ ^[A-Za-z0-9._-]+$ ]] || fail "run-id contains unsafe characters"
    [[ "$METHOD" == "original" || "$METHOD" == "full-k1" || "$METHOD" == "full-k5" ]] || fail "smoke method must be original, full-k1, or full-k5"
    [[ "$SEED" =~ ^1$ ]] || fail "Phase 05 smoke only permits seed 1"
fi

case "$BENCHMARK" in
    echidna-flags)
        COMPILER="0.8.20"
        SOURCE="contracts/public-benchmarks/adapted/EchidnaFlagsTarget.sol"
        CONTRACT_NAME="PublicEchidnaFlagsTarget"
        PROPERTY="echidna_sometimesfalse"
        HARNESS_PREFIX="PublicEchidnaFlagsFull"
        ;;
    echidna-multi)
        COMPILER="0.8.20"
        SOURCE="contracts/public-benchmarks/raw/echidna/multi.sol"
        CONTRACT_NAME="C"
        PROPERTY="echidna_state3"
        HARNESS_PREFIX="PublicEchidnaMultiFull"
        ;;
    exercise2-access-control)
        COMPILER="0.8.20"
        SOURCE="contracts/public-benchmarks/raw/exercise2/solution.sol"
        CONTRACT_NAME="TestToken"
        PROPERTY="echidna_no_transfer"
        HARNESS_PREFIX="PublicExercise2Full"
        ;;
    smartbugs-multifunc)
        COMPILER="0.4.25"
        SOURCE="contracts/public-benchmarks/adapted/SmartBugsMultiFuncEchidna.sol"
        CONTRACT_NAME="SmartBugsMultiFuncEchidna"
        PROPERTY="echidna_count_does_not_underflow"
        HARNESS_PREFIX="PublicSmartBugsMultiFuncFull"
        ;;
    smartbugs-onefunc)
        COMPILER="0.4.25"
        SOURCE="contracts/public-benchmarks/adapted/SmartBugsOneFuncEchidna.sol"
        CONTRACT_NAME="SmartBugsOneFuncEchidna"
        PROPERTY="echidna_count_does_not_underflow"
        HARNESS_PREFIX="PublicSmartBugsOneFuncFull"
        ;;
    *)
        fail "unknown public C-1 benchmark: $BENCHMARK"
        ;;
esac

HARNESS_K1="$HARNESS_PREFIX""K1Harness"
HARNESS_K5="$HARNESS_PREFIX""K5Harness"
SCRIPT_DIR="$(cd -- "$(dirname -- "$BASH_SOURCE")" && pwd)"
REPO_ROOT="$(bash "$SCRIPT_DIR/resolve_repo_root.sh")"
REPO_ROOT="$(readlink -f -- "$REPO_ROOT")"
cd "$REPO_ROOT"

EXPECTED_REPO_ROOT="$(git -C "$REPO_ROOT" rev-parse --show-toplevel 2>/dev/null)" || fail "repository root could not be verified"
EXPECTED_REPO_ROOT="$(readlink -f -- "$EXPECTED_REPO_ROOT")"
[[ "$EXPECTED_REPO_ROOT" == "$REPO_ROOT" ]] || fail "repository root verification failed"

WORK_ROOT="$REPO_ROOT/work"
RESTART_ROOT="$WORK_ROOT/v1-restart"
PUBLIC_SMOKE_ROOT="$RESTART_ROOT/phase05-public-smoke"
for path in "$WORK_ROOT" "$RESTART_ROOT" "$PUBLIC_SMOKE_ROOT"; do
    [[ ! -L "$path" ]] || fail "temporary output path must not be a symlink: $path"
    [[ ! -e "$path" || -d "$path" ]] || fail "temporary output path is not a directory: $path"
done
mkdir -p "$PUBLIC_SMOKE_ROOT"

if [[ "$MODE" == "preflight" ]]; then
    OUTPUT_ROOT="$PUBLIC_SMOKE_ROOT/$BENCHMARK-preflight"
else
    OUTPUT_ROOT="$PUBLIC_SMOKE_ROOT/$RUN_ID"
fi
[[ ! -e "$OUTPUT_ROOT" && ! -L "$OUTPUT_ROOT" ]] || fail "refusing to overwrite existing output: $OUTPUT_ROOT"
mkdir "$OUTPUT_ROOT"
mkdir -p "$OUTPUT_ROOT/generated" "$OUTPUT_ROOT/raw" "$OUTPUT_ROOT/parsed" "$OUTPUT_ROOT/summary" "$OUTPUT_ROOT/status"

SOURCE_ABS="$REPO_ROOT/$SOURCE"
ORIGINAL_CONFIG="$REPO_ROOT/configs/public-c1-original.yaml"
HARNESS_CONFIG="$REPO_ROOT/configs/public-c1-harness.yaml"
PREREGISTRATION="$REPO_ROOT/docs/v1-restart/phase05-public-preregistration.tsv"
EXISTING_PATH_PREFLIGHT="$REPO_ROOT/results/public-benchmarks/c1/c1-path-preflight.csv"
PREVIOUS_APPLICABILITY="$REPO_ROOT/results/semantic-applicability/v1/applicability.csv"
START_TIME="$(date --iso-8601=seconds)"
FAILED_STAGE="none"
EXIT_CODE=0
INPUT_CONTRACT="$CONTRACT_NAME"
CONFIG="$ORIGINAL_CONFIG"
INPUT_SOURCE="$SOURCE_ABS"

[[ -f "$SOURCE_ABS" ]] || fail "contract not found: $SOURCE"
[[ -f "$ORIGINAL_CONFIG" && -f "$HARNESS_CONFIG" ]] || fail "public C-1 config not found"
[[ -f "$PREREGISTRATION" ]] || fail "Phase 05 preregistration manifest not found"
[[ "$CONDA_DEFAULT_ENV" == "contract-fuzz" ]] || fail "active Conda environment must be contract-fuzz"
[[ -n "$CONDA_PREFIX" && -d "$CONDA_PREFIX" ]] || fail "CONDA_PREFIX must point to the active contract-fuzz environment"

export PATH="$CONDA_PREFIX/bin:$PATH"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPYCACHEPREFIX="$OUTPUT_ROOT/generated/pycache"

for command_name in python slither solc solc-select echidna git sha256sum jq awk; do
    command -v "$command_name" >/dev/null 2>&1 || fail "required command not found: $command_name"
done

write_environment() {
    {
        printf 'REPO_ROOT=%s\n' "$REPO_ROOT"
        printf 'RUN_ID=%s\n' "$RUN_ID"
        printf 'MODE=%s\n' "$MODE"
        printf 'BENCHMARK=%s\n' "$BENCHMARK"
        printf 'METHOD=%s\n' "$METHOD"
        printf 'SEED=%s\n' "$SEED"
        printf 'METHOD_VERSION=Full-v1.0.1-compat\n'
        printf 'GIT_BRANCH=%s\n' "$(git branch --show-current)"
        printf 'COMMIT_SHA=%s\n' "$(git rev-parse HEAD)"
        printf 'COMPILER=%s\n' "$COMPILER"
        printf 'CONTRACT_FILE=%s\n' "$SOURCE"
        printf 'CONTRACT_NAME=%s\n' "$CONTRACT_NAME"
        printf 'PROPERTY=%s\n' "$PROPERTY"
        printf 'ORIGINAL_CONFIG=configs/public-c1-original.yaml\n'
        printf 'HARNESS_CONFIG=configs/public-c1-harness.yaml\n'
        printf 'TEST_LIMIT=100000\nTIMEOUT=30s\nWORKERS=1\nSTOP_ON_FAIL=true\n'
        printf 'PYTHON=%s\n' "$(command -v python)"
        printf 'SLITHER=%s\n' "$(command -v slither)"
        printf 'SOLC=%s\n' "$(command -v solc)"
        printf 'SOLC_SELECT=%s\n' "$(command -v solc-select)"
        printf 'ECHIDNA=%s\n' "$(command -v echidna)"
        printf 'PYTHON_VERSION=%s\n' "$(python --version 2>&1 | tr '\n' ' ')"
        printf 'SLITHER_VERSION=%s\n' "$(slither --version 2>&1 | tr '\n' ' ')"
        printf 'SOLC_VERSION=%s\n' "$(solc --version 2>&1 | tr '\n' ' ')"
        printf 'ECHIDNA_VERSION=%s\n' "$(echidna --version 2>&1 | tr '\n' ' ')"
        printf 'SOLC_SELECT_VERSIONS=%s\n' "$(solc-select versions 2>&1 | tr '\n' '; ')"
        printf 'START_TIME=%s\n' "$START_TIME"
    } > "$OUTPUT_ROOT/environment.txt"
}

write_command_record() {
    {
        printf 'cd -- %q\n' "$REPO_ROOT"
        printf 'solc-select use %q\n' "$COMPILER"
        if [[ "$MODE" == "preflight" ]]; then
            printf 'solc --allow-paths %q --bin %q\n' "$REPO_ROOT/contracts" "$SOURCE_ABS"
            printf 'python analyzer/extract_rw.py %q > %q\n' "$SOURCE_ABS" "$OUTPUT_ROOT/generated/rw.json"
            printf 'python analyzer/generate_repetition_aware_sequences.py %q 4 500 --contract %q --max-function-visits 2 > %q\n' "$OUTPUT_ROOT/generated/rw.json" "$CONTRACT_NAME" "$OUTPUT_ROOT/generated/repeat-property-sequences.json"
            printf 'python analyzer/extract_value_constraints.py %q --contract %q > %q\n' "$SOURCE_ABS" "$CONTRACT_NAME"
            printf 'python analyzer/generate_value_guided_sequences.py %q %q --contract %q > %q\n' "$OUTPUT_ROOT/generated/repeat-property-sequences.json" "$OUTPUT_ROOT/generated/value-constraints.json" "$CONTRACT_NAME" "$OUTPUT_ROOT/generated/full-sequences.json"
            printf 'python analyzer/generate_harness_from_paths.py --source %q --sequences %q --target-contract %q --harness-contract %q --output %q --prefix full --top-k 1 --solidity-pragma %q\n' "$SOURCE_ABS" "$OUTPUT_ROOT/generated/full-sequences.json" "$CONTRACT_NAME" "$HARNESS_K1" "$OUTPUT_ROOT/generated/harness-k1.sol" "$COMPILER"
            printf 'python analyzer/generate_harness_from_paths.py --source %q --sequences %q --target-contract %q --harness-contract %q --output %q --prefix full --top-k 5 --solidity-pragma %q\n' "$SOURCE_ABS" "$OUTPUT_ROOT/generated/full-sequences.json" "$CONTRACT_NAME" "$HARNESS_K5" "$OUTPUT_ROOT/generated/harness-k5.sol" "$COMPILER"
            printf 'solc --allow-paths %q --bin %q\n' "$REPO_ROOT/contracts" "$OUTPUT_ROOT/generated/harness-k1.sol"
            printf 'solc --allow-paths %q --bin %q\n' "$REPO_ROOT/contracts" "$OUTPUT_ROOT/generated/harness-k5.sol"
        else
            printf 'echidna %q --contract %q --config %q --seed %q\n' "$INPUT_SOURCE" "$INPUT_CONTRACT" "$CONFIG" "$SEED"
        fi
    } > "$OUTPUT_ROOT/command.txt"
}

write_manifest() {
    {
        printf 'run_id\tcommit_sha\tmethod_version\tmode\tbenchmark\tmethod\tcompiler\tcontract_file\tcontract_name\tproperty\tconfig_file\tseed\ttest_limit\ttimeout\tworkers\tstop_on_fail\toutput_root\tstart_time\n'
        printf '%s\t%s\tFull-v1.0.1-compat\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t100000\t30s\t1\ttrue\t%s\t%s\n' "$RUN_ID" "$(git rev-parse HEAD)" "$MODE" "$BENCHMARK" "$METHOD" "$COMPILER" "$SOURCE" "$INPUT_CONTRACT" "$PROPERTY" "$(realpath --relative-to="$REPO_ROOT" "$CONFIG")" "$SEED" "$OUTPUT_ROOT" "$START_TIME"
    } > "$OUTPUT_ROOT/manifest.tsv"
}

write_checksums() {
    {
        sha256sum -- "$SOURCE_ABS" "$ORIGINAL_CONFIG" "$HARNESS_CONFIG" "$PREREGISTRATION" "$EXISTING_PATH_PREFLIGHT" "$PREVIOUS_APPLICABILITY" "$OUTPUT_ROOT/manifest.tsv" "$OUTPUT_ROOT/command.txt" "$OUTPUT_ROOT/environment.txt" "$OUTPUT_ROOT/status/status.env"
        if [[ -f "$REPO_ROOT/contracts/public-benchmarks/raw/exercise2/token.sol" ]]; then
            sha256sum -- "$REPO_ROOT/contracts/public-benchmarks/raw/exercise2/token.sol"
        fi
        find "$OUTPUT_ROOT/generated" "$OUTPUT_ROOT/raw" "$OUTPUT_ROOT/parsed" "$OUTPUT_ROOT/summary" -type f ! -name '*.tmp' -print0 |
            sort -z | xargs -0 -r sha256sum
    } > "$OUTPUT_ROOT/status/checksums.sha256"
}

write_status() {
    {
        printf 'MODE=%s\n' "$MODE"
        printf 'STATUS=%s\n' "$1"
        printf 'RUN_COMPLETED=%s\n' "$2"
        printf 'EXIT_CODE=%s\n' "$EXIT_CODE"
        printf 'FAILED_STAGE=%s\n' "$FAILED_STAGE"
        printf 'START_TIME=%s\n' "$START_TIME"
        printf 'END_TIME=%s\n' "$3"
    } > "$OUTPUT_ROOT/status/status.env"
}

write_environment
write_command_record
write_manifest
if grep -Eq 'results/formal|results/formal-b2|results/public-benchmarks/c1/|results/paper-data|contracts/harnesses/formal' "$OUTPUT_ROOT/command.txt"; then
    FAILED_STAGE="path_safety"
    EXIT_CODE=1
    write_status "startup_error" 0 "$(date --iso-8601=seconds)"
    write_checksums
    fail "planned command leaks into a frozen output path"
fi

if ! solc-select use "$COMPILER" > "$OUTPUT_ROOT/raw/solc-select.log" 2>&1; then
    FAILED_STAGE="solc_select"
    EXIT_CODE=1
    write_status "startup_error" 0 "$(date --iso-8601=seconds)"
    write_checksums
    exit 1
fi

if [[ "$MODE" == "preflight" ]]; then
    SOLC_ORIGINAL_DIR="$OUTPUT_ROOT/generated/solc-original"
    SOLC_K1_DIR="$OUTPUT_ROOT/generated/solc-k1"
    SOLC_K5_DIR="$OUTPUT_ROOT/generated/solc-k5"
    mkdir -p "$SOLC_ORIGINAL_DIR" "$SOLC_K1_DIR" "$SOLC_K5_DIR"
    if ! grep -RqsE "contract[[:space:]]+$CONTRACT_NAME([[:space:]]|\\{|is)" "$SOURCE_ABS" "$(dirname "$SOURCE_ABS")"; then
        FAILED_STAGE="contract_name_check"
        EXIT_CODE=1
        write_status "startup_error" 0 "$(date --iso-8601=seconds)"
        write_checksums
        exit 1
    fi
    if ! grep -RqsE "function[[:space:]]+$PROPERTY([[:space:]]|\\()" "$SOURCE_ABS" "$(dirname "$SOURCE_ABS")"; then
        FAILED_STAGE="property_check"
        EXIT_CODE=1
        write_status "startup_error" 0 "$(date --iso-8601=seconds)"
        write_checksums
        exit 1
    fi
    if ! (cd "$SOLC_ORIGINAL_DIR" && solc --allow-paths "$REPO_ROOT/contracts" --bin "$SOURCE_ABS" > "$OUTPUT_ROOT/raw/original-solc.stdout" 2> "$OUTPUT_ROOT/raw/original-solc.stderr"); then
        FAILED_STAGE="original_solc"
        EXIT_CODE=1
        write_status "startup_error" 0 "$(date --iso-8601=seconds)"
        write_checksums
        exit 1
    fi
    if ! python analyzer/extract_rw.py "$SOURCE_ABS" > "$OUTPUT_ROOT/generated/rw.json" 2> "$OUTPUT_ROOT/raw/extract-rw.stderr"; then
        FAILED_STAGE="slither_extract_rw"
        EXIT_CODE=1
        write_status "startup_error" 0 "$(date --iso-8601=seconds)"
        write_checksums
        exit 1
    fi
    if ! python analyzer/generate_repetition_aware_sequences.py "$OUTPUT_ROOT/generated/rw.json" 4 500 --contract "$CONTRACT_NAME" --max-function-visits 2 > "$OUTPUT_ROOT/generated/repeat-property-sequences.json" 2> "$OUTPUT_ROOT/raw/repeat-generation.stderr"; then
        FAILED_STAGE="repeat_generation"
        EXIT_CODE=1
        write_status "startup_error" 0 "$(date --iso-8601=seconds)"
        write_checksums
        exit 1
    fi
    if ! python analyzer/extract_value_constraints.py "$SOURCE_ABS" --contract "$CONTRACT_NAME" > "$OUTPUT_ROOT/generated/value-constraints.json" 2> "$OUTPUT_ROOT/raw/value-extraction.stderr"; then
        FAILED_STAGE="value_extraction"
        EXIT_CODE=1
        write_status "startup_error" 0 "$(date --iso-8601=seconds)"
        write_checksums
        exit 1
    fi
    if ! python analyzer/generate_value_guided_sequences.py "$OUTPUT_ROOT/generated/repeat-property-sequences.json" "$OUTPUT_ROOT/generated/value-constraints.json" --contract "$CONTRACT_NAME" > "$OUTPUT_ROOT/generated/full-sequences.json" 2> "$OUTPUT_ROOT/raw/value-guided-generation.stderr"; then
        FAILED_STAGE="value_guided_generation"
        EXIT_CODE=1
        write_status "startup_error" 0 "$(date --iso-8601=seconds)"
        write_checksums
        exit 1
    fi
    if ! python analyzer/generate_harness_from_paths.py --source "$SOURCE_ABS" --sequences "$OUTPUT_ROOT/generated/full-sequences.json" --target-contract "$CONTRACT_NAME" --harness-contract "$HARNESS_K1" --output "$OUTPUT_ROOT/generated/harness-k1.sol" --prefix full --top-k 1 --solidity-pragma "$COMPILER" > "$OUTPUT_ROOT/raw/harness-k1-generation.stdout" 2> "$OUTPUT_ROOT/raw/harness-k1-generation.stderr"; then
        FAILED_STAGE="harness_k1_generation"
        EXIT_CODE=1
        write_status "startup_error" 0 "$(date --iso-8601=seconds)"
        write_checksums
        exit 1
    fi
    if ! python analyzer/generate_harness_from_paths.py --source "$SOURCE_ABS" --sequences "$OUTPUT_ROOT/generated/full-sequences.json" --target-contract "$CONTRACT_NAME" --harness-contract "$HARNESS_K5" --output "$OUTPUT_ROOT/generated/harness-k5.sol" --prefix full --top-k 5 --solidity-pragma "$COMPILER" > "$OUTPUT_ROOT/raw/harness-k5-generation.stdout" 2> "$OUTPUT_ROOT/raw/harness-k5-generation.stderr"; then
        FAILED_STAGE="harness_k5_generation"
        EXIT_CODE=1
        write_status "startup_error" 0 "$(date --iso-8601=seconds)"
        write_checksums
        exit 1
    fi
    if ! grep -qs "contract $HARNESS_K1" "$OUTPUT_ROOT/generated/harness-k1.sol" || ! grep -qs "contract $HARNESS_K5" "$OUTPUT_ROOT/generated/harness-k5.sol"; then
        FAILED_STAGE="harness_contract_check"
        EXIT_CODE=1
        write_status "startup_error" 0 "$(date --iso-8601=seconds)"
        write_checksums
        exit 1
    fi
    if ! (cd "$SOLC_K1_DIR" && solc --allow-paths "$REPO_ROOT/contracts,$OUTPUT_ROOT/generated" --bin "$OUTPUT_ROOT/generated/harness-k1.sol" > "$OUTPUT_ROOT/raw/harness-k1-solc.stdout" 2> "$OUTPUT_ROOT/raw/harness-k1-solc.stderr"); then
        FAILED_STAGE="harness_k1_solc"
        EXIT_CODE=1
        write_status "startup_error" 0 "$(date --iso-8601=seconds)"
        write_checksums
        exit 1
    fi
    if ! (cd "$SOLC_K5_DIR" && solc --allow-paths "$REPO_ROOT/contracts,$OUTPUT_ROOT/generated" --bin "$OUTPUT_ROOT/generated/harness-k5.sol" > "$OUTPUT_ROOT/raw/harness-k5-solc.stdout" 2> "$OUTPUT_ROOT/raw/harness-k5-solc.stderr"); then
        FAILED_STAGE="harness_k5_solc"
        EXIT_CODE=1
        write_status "startup_error" 0 "$(date --iso-8601=seconds)"
        write_checksums
        exit 1
    fi
    jq empty "$OUTPUT_ROOT/generated/rw.json" "$OUTPUT_ROOT/generated/repeat-property-sequences.json" "$OUTPUT_ROOT/generated/value-constraints.json" "$OUTPUT_ROOT/generated/full-sequences.json"
    {
        printf 'benchmark\tcontract_name\tproperty\toriginal_exists\toriginal_compiles\trw_extracted\tfull_sequences\tharness_k1_generated\tharness_k1_compiles\tharness_k5_generated\tharness_k5_compiles\n'
        printf '%s\t%s\t%s\ttrue\ttrue\ttrue\ttrue\ttrue\ttrue\ttrue\ttrue\n' "$BENCHMARK" "$CONTRACT_NAME" "$PROPERTY"
    } > "$OUTPUT_ROOT/summary/preflight.tsv"
    write_status "preflight_pass" 1 "$(date --iso-8601=seconds)"
    write_checksums
    printf 'Preflight finished: %s\n' "$OUTPUT_ROOT"
    exit 0
fi

PREFLIGHT_ROOT="$PUBLIC_SMOKE_ROOT/$BENCHMARK-preflight"
[[ -f "$PREFLIGHT_ROOT/generated/harness-k1.sol" && -f "$PREFLIGHT_ROOT/generated/harness-k5.sol" ]] || {
    FAILED_STAGE="missing_preflight"
    EXIT_CODE=1
    write_status "startup_error" 0 "$(date --iso-8601=seconds)"
    write_checksums
    exit 1
}

if [[ "$METHOD" == "original" ]]; then
    INPUT_CONTRACT="$CONTRACT_NAME"
    CONFIG="$ORIGINAL_CONFIG"
    INPUT_SOURCE="$SOURCE_ABS"
else
    CONFIG="$HARNESS_CONFIG"
    if [[ "$METHOD" == "full-k1" ]]; then
        INPUT_CONTRACT="$HARNESS_K1"
        cp -- "$PREFLIGHT_ROOT/generated/harness-k1.sol" "$OUTPUT_ROOT/generated/input.sol"
    else
        INPUT_CONTRACT="$HARNESS_K5"
        cp -- "$PREFLIGHT_ROOT/generated/harness-k5.sol" "$OUTPUT_ROOT/generated/input.sol"
    fi
    INPUT_SOURCE="$OUTPUT_ROOT/generated/input.sol"
fi
write_command_record
write_manifest

RAW_TMP="$OUTPUT_ROOT/raw/seed-$SEED.log.tmp"
RAW_LOG="$OUTPUT_ROOT/raw/seed-$SEED.log"
{
    printf 'RUN_ID=%s\nBENCHMARK=%s\nMETHOD=%s\nSEED=%s\nMETHOD_VERSION=Full-v1.0.1-compat\nCOMPILER=%s\nCONTRACT_FILE=%s\nCONTRACT_NAME=%s\nCONFIG_FILE=%s\nSTART_TIME=%s\n\n' "$RUN_ID" "$BENCHMARK" "$METHOD" "$SEED" "$COMPILER" "$SOURCE" "$INPUT_CONTRACT" "$(realpath --relative-to="$REPO_ROOT" "$CONFIG")" "$START_TIME"
    printf '===== SOLC VERSION =====\n'
    solc --version
    printf '\n===== ECHIDNA COMMAND =====\n'
    printf 'echidna %q --contract %q --config %q --seed %q\n\n' "$INPUT_SOURCE" "$INPUT_CONTRACT" "$CONFIG" "$SEED"
} > "$RAW_TMP"

set +e
echidna "$INPUT_SOURCE" --contract "$INPUT_CONTRACT" --config "$CONFIG" --seed "$SEED" >> "$RAW_TMP" 2>&1
ECHIDNA_EXIT_CODE="$?"
set -e
END_TIME="$(date --iso-8601=seconds)"
printf '\nEXIT_CODE=%s\nEND_TIME=%s\n' "$ECHIDNA_EXIT_CODE" "$END_TIME" >> "$RAW_TMP"
mv -- "$RAW_TMP" "$RAW_LOG"

EXIT_CODE="$ECHIDNA_EXIT_CODE"
if grep -Eiq 'falsified|property[[:space:][:punct:]]*failed|assertion[[:space:][:punct:]]*failed|failed!' "$RAW_LOG"; then
    STATUS_VALUE="falsified"
elif grep -Eiq 'Echidna doesn.t support versions of solc before|compilation failed|ParserError|File outside of allowed directories|Source .* not found|Config .* not found|Could not compile' "$RAW_LOG"; then
    STATUS_VALUE="startup_error"
elif grep -Eiq 'Test limit reached[.] Stopping[.]|testLimit|budget.exhaust|time limit|timed out' "$RAW_LOG"; then
    STATUS_VALUE="budget_exhausted"
elif grep -Eiq 'echidna_[A-Za-z0-9_]+[[:space:]]*:[[:space:]]*(passed|passing)' "$RAW_LOG"; then
    STATUS_VALUE="passed"
elif [[ "$ECHIDNA_EXIT_CODE" -ne 0 ]]; then
    STATUS_VALUE="unknown_error"
else
    STATUS_VALUE="incomplete"
fi

if ! python analyzer/parse_experiment_logs.py "$OUTPUT_ROOT/raw" "$OUTPUT_ROOT/parsed/smoke.csv" > "$OUTPUT_ROOT/raw/parser.stdout" 2> "$OUTPUT_ROOT/raw/parser.stderr"; then
    FAILED_STAGE="parser"
    STATUS_VALUE="unknown_error"
fi
if ! python analyzer/summarize_experiment.py "$OUTPUT_ROOT/parsed/smoke.csv" "$OUTPUT_ROOT/summary/smoke.csv" > "$OUTPUT_ROOT/raw/summarizer.stdout" 2> "$OUTPUT_ROOT/raw/summarizer.stderr"; then
    FAILED_STAGE="summarizer"
    STATUS_VALUE="unknown_error"
fi

if [[ -s "$OUTPUT_ROOT/parsed/smoke.csv" ]]; then
    PARSED_STATUS="$(awk -F, 'NR == 2 {print $3}' "$OUTPUT_ROOT/parsed/smoke.csv")"
    if [[ -n "$PARSED_STATUS" ]]; then
        STATUS_VALUE="$PARSED_STATUS"
    fi
fi

if [[ "$STATUS_VALUE" == "falsified" || "$STATUS_VALUE" == "budget_exhausted" || "$STATUS_VALUE" == "passed" ]]; then
    RUN_COMPLETED=1
else
    RUN_COMPLETED=0
fi
write_status "$STATUS_VALUE" "$RUN_COMPLETED" "$END_TIME"
write_checksums
printf 'Smoke finished: %s (%s)\n' "$OUTPUT_ROOT" "$STATUS_VALUE"
[[ "$STATUS_VALUE" != "unknown_error" ]]
