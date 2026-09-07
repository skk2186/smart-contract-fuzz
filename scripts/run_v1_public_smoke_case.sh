#!/usr/bin/env bash

set -euo pipefail

usage() {
    cat >&2 <<'USAGE'
Usage:
  bash scripts/run_v1_public_smoke_case.sh --mode main10-preflight --run-id <run_id> --benchmark <benchmark_id> --method <Original|Full-K1|Full-K5> --seed <1..10>
  bash scripts/run_v1_public_smoke_case.sh --mode main10-dry-run --run-id <run_id> --benchmark <benchmark_id> --method <Original|Full-K1|Full-K5> --seed <1..10>
  # --mode main10 is reserved for the B4 execution phase; B3 never invokes it.
  bash scripts/run_v1_public_smoke_case.sh --mode preflight --benchmark <benchmark_id> [--run-id <run_id>]
  bash scripts/run_v1_public_smoke_case.sh --mode smoke --run-id <run_id> --benchmark <benchmark_id> --method <original|full-k1|full-k5> --seed 1
  bash scripts/run_v1_public_smoke_case.sh --mode pilot-preflight --benchmark <benchmark_id> [--run-id <run_id>]
  bash scripts/run_v1_public_smoke_case.sh --mode pilot --run-id <run_id> --benchmark <benchmark_id> --method <original|full-k1|full-k5> --seed <1|2|3>
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

[[ "$MODE" == "preflight" || "$MODE" == "smoke" || "$MODE" == "pilot-preflight" || "$MODE" == "pilot" || "$MODE" == "main10-preflight" || "$MODE" == "main10-dry-run" || "$MODE" == "main10" ]] || fail "--mode must be preflight, smoke, pilot-preflight, pilot, main10-preflight, main10-dry-run, or main10"
[[ -n "$BENCHMARK" ]] || fail "--benchmark is required"
MAIN10_MODE=0
SAFE_MAIN10_MODE=0
if [[ "$MODE" == "main10-preflight" || "$MODE" == "main10-dry-run" || "$MODE" == "main10" ]]; then
    MAIN10_MODE=1
    [[ "$MODE" == "main10-preflight" || "$MODE" == "main10-dry-run" ]] && SAFE_MAIN10_MODE=1
fi
if (( MAIN10_MODE == 1 )); then
    [[ -n "$RUN_ID" ]] || fail "--run-id is required for main10"
    [[ "$RUN_ID" =~ ^[A-Za-z0-9._-]+$ ]] || fail "run-id contains unsafe characters"
    case "$METHOD" in
        original|Original) METHOD="original" ;;
        full-k1|Full-K1) METHOD="full-k1" ;;
        full-k5|Full-K5) METHOD="full-k5" ;;
        *) fail "main10 method must be Original, Full-K1, or Full-K5" ;;
    esac
    case "$SEED" in
        1|2|3|4|5|6|7|8|9|10) ;;
        11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30) fail "main10 explicitly rejects seed $SEED" ;;
        *) fail "main10 only permits seeds 1 through 10" ;;
    esac
elif [[ "$MODE" == "preflight" || "$MODE" == "pilot-preflight" ]]; then
    [[ -z "$METHOD" && -z "$SEED" ]] || fail "preflight does not accept method or seed"
    [[ -z "$RUN_ID" || "$RUN_ID" =~ ^[A-Za-z0-9._-]+$ ]] || fail "run-id contains unsafe characters"
else
    [[ -n "$RUN_ID" ]] || fail "--run-id is required for smoke/pilot"
    [[ "$RUN_ID" =~ ^[A-Za-z0-9._-]+$ ]] || fail "run-id contains unsafe characters"
    [[ "$METHOD" == "original" || "$METHOD" == "full-k1" || "$METHOD" == "full-k5" ]] || fail "smoke method must be original, full-k1, or full-k5"
    if [[ "$MODE" == "smoke" ]]; then
        [[ "$SEED" =~ ^1$ ]] || fail "Phase 05 smoke only permits seed 1"
    else
        [[ "$SEED" =~ ^[123]$ ]] || fail "Phase 06A pilot only permits seeds 1, 2, or 3"
    fi
fi

if (( MAIN10_MODE == 1 )); then
    case "$BENCHMARK" in
        PUB06|PUB07|PUB08|alternative-path-internal|multi-property-internal|three-step-internal)
            fail "main10 rejects excluded benchmark: $BENCHMARK"
            ;;
        matched-random-v1)
            fail "main10 rejects matched-random-v1"
            ;;
    esac
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
case "$BENCHMARK" in
    echidna-flags) BENCHMARK_ID="PUB01" ;;
    echidna-multi) BENCHMARK_ID="PUB02" ;;
    smartbugs-multifunc) BENCHMARK_ID="PUB03" ;;
    smartbugs-onefunc) BENCHMARK_ID="PUB04" ;;
    exercise2-access-control) BENCHMARK_ID="PUB05" ;;
esac
if (( MAIN10_MODE == 1 )); then
    case "$BENCHMARK" in
        echidna-flags|echidna-multi|smartbugs-multifunc|smartbugs-onefunc)
            ;;
        exercise2-access-control)
            fail "main10 rejects conditional benchmark: $BENCHMARK"
            ;;
        PUB06|PUB07|PUB08|alternative-path-internal|multi-property-internal|three-step-internal)
            fail "main10 rejects excluded benchmark: $BENCHMARK"
            ;;
        matched-random-v1)
            fail "main10 rejects matched-random-v1"
            ;;
        *)
            fail "main10 benchmark is not preregistered and is not supported: $BENCHMARK"
            ;;
    esac
fi
if [[ "$MODE" == "pilot-preflight" || "$MODE" == "pilot" ]]; then
    case "$BENCHMARK" in
        echidna-flags|echidna-multi|smartbugs-multifunc|smartbugs-onefunc)
            ;;
        exercise2-access-control)
            fail "Phase 06A pilot does not permit conditional benchmark: $BENCHMARK"
            ;;
        *)
            fail "Phase 06A pilot benchmark is not supported: $BENCHMARK"
            ;;
    esac
fi
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
PHASE06A_ROOT="$RESTART_ROOT/phase06a-public-supported-3seed"
B4_MAIN_ROOT="$RESTART_ROOT/b4-public-supported-10seed-main"
B4_OUTPUT_REL_ROOT="work/v1-restart/b4-public-supported-10seed-main/"
for path in "$WORK_ROOT" "$RESTART_ROOT"; do
    [[ ! -L "$path" ]] || fail "temporary output path must not be a symlink: $path"
    [[ ! -e "$path" || -d "$path" ]] || fail "temporary output path is not a directory: $path"
done
if (( MAIN10_MODE == 1 )); then
    [[ ! -L "$B4_MAIN_ROOT" ]] || fail "temporary output path must not be a symlink: $B4_MAIN_ROOT"
    [[ ! -e "$B4_MAIN_ROOT" || -d "$B4_MAIN_ROOT" ]] || fail "temporary output path is not a directory: $B4_MAIN_ROOT"
    mkdir -p "$B4_MAIN_ROOT"
else
    [[ ! -L "$PUBLIC_SMOKE_ROOT" ]] || fail "temporary output path must not be a symlink: $PUBLIC_SMOKE_ROOT"
    [[ ! -e "$PUBLIC_SMOKE_ROOT" || -d "$PUBLIC_SMOKE_ROOT" ]] || fail "temporary output path is not a directory: $PUBLIC_SMOKE_ROOT"
    mkdir -p "$PUBLIC_SMOKE_ROOT"
    if [[ "$MODE" == "pilot-preflight" || "$MODE" == "pilot" ]]; then
        [[ ! -L "$PHASE06A_ROOT" ]] || fail "temporary output path must not be a symlink: $PHASE06A_ROOT"
        [[ ! -e "$PHASE06A_ROOT" || -d "$PHASE06A_ROOT" ]] || fail "temporary output path is not a directory: $PHASE06A_ROOT"
        mkdir -p "$PHASE06A_ROOT"
    fi
fi
if (( MAIN10_MODE == 1 )); then
    OUTPUT_ROOT="$B4_MAIN_ROOT/$RUN_ID"
elif [[ "$MODE" == "preflight" ]]; then
    if [[ -n "$RUN_ID" ]]; then
        OUTPUT_ROOT="$PUBLIC_SMOKE_ROOT/$BENCHMARK-preflight-$RUN_ID"
    else
        OUTPUT_ROOT="$PUBLIC_SMOKE_ROOT/$BENCHMARK-preflight"
    fi
elif [[ "$MODE" == "pilot-preflight" ]]; then
    if [[ -n "$RUN_ID" ]]; then
        OUTPUT_ROOT="$PHASE06A_ROOT/$BENCHMARK-preflight-$RUN_ID"
    else
        OUTPUT_ROOT="$PHASE06A_ROOT/$BENCHMARK-preflight"
    fi
elif [[ "$MODE" == "pilot" ]]; then
    OUTPUT_ROOT="$PHASE06A_ROOT/$RUN_ID"
else
    OUTPUT_ROOT="$PUBLIC_SMOKE_ROOT/$RUN_ID"
fi
[[ "$OUTPUT_ROOT" == "$B4_MAIN_ROOT"/* || "$MODE" != "main10-preflight" && "$MODE" != "main10-dry-run" && "$MODE" != "main10" ]] || fail "main10 output root is not fixed to B4 root"
[[ "$OUTPUT_ROOT" != *"/results/"* && "$OUTPUT_ROOT" != *"/paper-ready/"* && "$OUTPUT_ROOT" != *"/matched-random-v1/"* ]] || fail "main10 output path enters a forbidden evidence directory"
[[ ! -e "$OUTPUT_ROOT" && ! -L "$OUTPUT_ROOT" ]] || fail "refusing to overwrite existing output: $OUTPUT_ROOT"
mkdir "$OUTPUT_ROOT"
mkdir -p "$OUTPUT_ROOT/generated" "$OUTPUT_ROOT/raw" "$OUTPUT_ROOT/parsed" "$OUTPUT_ROOT/summary" "$OUTPUT_ROOT/status"

SOURCE_ABS="$REPO_ROOT/$SOURCE"
ORIGINAL_CONFIG="$REPO_ROOT/configs/public-c1-original.yaml"
HARNESS_CONFIG="$REPO_ROOT/configs/public-c1-harness.yaml"
MAIN10_PREREGISTRATION="$REPO_ROOT/paper-ready/v1/main10_preregistration.tsv"
MAIN10_EXPECTED_RUNS="$REPO_ROOT/paper-ready/v1/main10_expected_runs.tsv"
if (( MAIN10_MODE == 1 )); then
    PREREGISTRATION="$MAIN10_PREREGISTRATION"
else
    PREREGISTRATION="$REPO_ROOT/docs/v1-restart/phase05-public-preregistration.tsv"
fi
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
if (( MAIN10_MODE == 1 )); then
    EXPECTED_CONFIG_REL="configs/public-c1-harness.yaml"
    [[ "$METHOD" == "original" ]] && EXPECTED_CONFIG_REL="configs/public-c1-original.yaml"
    if (( SAFE_MAIN10_MODE == 1 )); then
        [[ "$RUN_ID" =~ ^b3-main10-(preflight|dry-run)-[A-Za-z0-9._-]+$ ]] || fail "safe main10 run-id must start with b3-main10-preflight- or b3-main10-dry-run-"
    else
        [[ -f "$MAIN10_EXPECTED_RUNS" ]] || fail "B4 expected-runs registry not found"
        if ! awk -F '\t' -v run_id="$RUN_ID" -v benchmark_id="$BENCHMARK_ID" -v benchmark="$BENCHMARK" -v method="$METHOD" -v seed="$SEED" -v source="$SOURCE" -v config="$EXPECTED_CONFIG_REL" -v output_dir="${B4_OUTPUT_REL_ROOT}${RUN_ID}/" 'NR == 1 { next } $1 == run_id && $2 == benchmark_id && $3 == benchmark && $4 == method && $5 == seed && $6 == source && $7 == config && $8 == output_dir && $10 == "preregistered" { found += 1 } END { exit found == 1 ? 0 : 1 }' "$MAIN10_EXPECTED_RUNS"; then
            fail "run-id, benchmark, method, seed, config, output directory, or status is not exactly preregistered"
        fi
    fi
elif (( SAFE_MAIN10_MODE == 0 )); then
    [[ "$CONDA_DEFAULT_ENV" == "contract-fuzz" ]] || fail "active Conda environment must be contract-fuzz"
    [[ -n "$CONDA_PREFIX" && -d "$CONDA_PREFIX" ]] || fail "CONDA_PREFIX must point to the active contract-fuzz environment"
fi

if (( MAIN10_MODE == 1 )); then
    if [[ "$METHOD" == "original" ]]; then
        INPUT_CONTRACT="$CONTRACT_NAME"
        CONFIG="$ORIGINAL_CONFIG"
        INPUT_SOURCE="$SOURCE_ABS"
    else
        CONFIG="$HARNESS_CONFIG"
        INPUT_CONTRACT="$HARNESS_K1"
        [[ "$METHOD" == "full-k5" ]] && INPUT_CONTRACT="$HARNESS_K5"
        INPUT_SOURCE="$PHASE06A_ROOT/$BENCHMARK-preflight/generated/harness-${METHOD#full-}.sol"
    fi
fi
if [[ -n "${CONDA_PREFIX:-}" ]]; then export PATH="$CONDA_PREFIX/bin:$PATH"; fi
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPYCACHEPREFIX="$OUTPUT_ROOT/generated/pycache"

if (( SAFE_MAIN10_MODE == 0 )); then
    for command_name in python slither solc solc-select echidna git sha256sum jq awk; do
        command -v "$command_name" >/dev/null 2>&1 || fail "required command not found: $command_name"
    done
fi

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
        if (( SAFE_MAIN10_MODE == 1 )); then
            printf 'SAFE_MODE=main10-preflight-or-dry-run\nECHIDNA_INVOCATION=skipped\nSLITHER_INVOCATION=skipped\nSOLC_INVOCATION=skipped\n'
        else
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
        fi
        printf 'START_TIME=%s\n' "$START_TIME"
    } > "$OUTPUT_ROOT/environment.txt"
}

write_command_record() {
    {
        printf 'cd -- %q\n' "$REPO_ROOT"
        if (( SAFE_MAIN10_MODE == 1 )); then
            printf '# main10 safe mode: no Echidna, Slither, solc, or solc-select invocation\n'
            printf 'python analyzer/build_main10_preregistration.py --check\n'
            printf 'planned_echidna_template=echidna %q --contract %q --config %q --seed %q\n' "$INPUT_SOURCE" "$INPUT_CONTRACT" "$CONFIG" "$SEED"
        else
            printf 'solc-select use %q\n' "$COMPILER"
        if [[ "$MODE" == "preflight" || "$MODE" == "pilot-preflight" ]]; then
            printf 'solc --allow-paths %q --bin %q\n' "$REPO_ROOT/contracts" "$SOURCE_ABS"
            printf 'python analyzer/extract_rw.py %q > %q\n' "$SOURCE_ABS" "$OUTPUT_ROOT/generated/rw.json"
            printf 'python analyzer/generate_repetition_aware_sequences.py %q 4 500 --contract %q --max-function-visits 2 > %q\n' "$OUTPUT_ROOT/generated/rw.json" "$CONTRACT_NAME" "$OUTPUT_ROOT/generated/repeat-property-sequences.json"
            printf 'python analyzer/extract_value_constraints.py %q --contract %q > %q\n' \
  "$SOURCE_ABS" "$CONTRACT_NAME" "$OUTPUT_ROOT/generated/value-constraints.json"
            printf 'python analyzer/generate_value_guided_sequences.py %q %q --contract %q > %q\n' "$OUTPUT_ROOT/generated/repeat-property-sequences.json" "$OUTPUT_ROOT/generated/value-constraints.json" "$CONTRACT_NAME" "$OUTPUT_ROOT/generated/full-sequences.json"
            printf 'python analyzer/generate_harness_from_paths.py --source %q --sequences %q --target-contract %q --harness-contract %q --output %q --prefix full --top-k 1 --solidity-pragma %q\n' "$SOURCE_ABS" "$OUTPUT_ROOT/generated/full-sequences.json" "$CONTRACT_NAME" "$HARNESS_K1" "$OUTPUT_ROOT/generated/harness-k1.sol" "$COMPILER"
            printf 'python analyzer/generate_harness_from_paths.py --source %q --sequences %q --target-contract %q --harness-contract %q --output %q --prefix full --top-k 5 --solidity-pragma %q\n' "$SOURCE_ABS" "$OUTPUT_ROOT/generated/full-sequences.json" "$CONTRACT_NAME" "$HARNESS_K5" "$OUTPUT_ROOT/generated/harness-k5.sol" "$COMPILER"
            printf 'solc --allow-paths %q --bin %q\n' "$REPO_ROOT/contracts" "$OUTPUT_ROOT/generated/harness-k1.sol"
            printf 'solc --allow-paths %q --bin %q\n' "$REPO_ROOT/contracts" "$OUTPUT_ROOT/generated/harness-k5.sol"
        else
            printf 'echidna %q --contract %q --config %q --seed %q\n' "$INPUT_SOURCE" "$INPUT_CONTRACT" "$CONFIG" "$SEED"
        fi
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
        for checksum_path in "$SOURCE_ABS" "$ORIGINAL_CONFIG" "$HARNESS_CONFIG" "$PREREGISTRATION" "$MAIN10_EXPECTED_RUNS" "$EXISTING_PATH_PREFLIGHT" "$PREVIOUS_APPLICABILITY" "$OUTPUT_ROOT/manifest.tsv" "$OUTPUT_ROOT/command.txt" "$OUTPUT_ROOT/environment.txt" "$OUTPUT_ROOT/status/status.env"; do
            if [[ -f "$checksum_path" ]]; then
                sha256sum -- "$checksum_path"
            fi
        done
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

if (( SAFE_MAIN10_MODE == 1 )); then
    write_environment
    write_command_record
    write_manifest
    if grep -Eq 'results/formal|results/formal-b2|results/public-benchmarks/c1/|results/paper-data|results/matched-random-v1|contracts/harnesses/formal' "$OUTPUT_ROOT/command.txt"; then
        FAILED_STAGE="path_safety"
        EXIT_CODE=1
        write_status "startup_error" 0 "$(date --iso-8601=seconds)"
        write_checksums
        fail "main10 safe-mode command leaks into a forbidden evidence path"
    fi
    printf 'main10 safe mode: Echidna fuzzing was not invoked.\n' > "$OUTPUT_ROOT/raw/dry-run.txt"
    printf 'status\tnotes\n%s\tno_fuzzing_invoked\n' "$([[ "$MODE" == "main10-preflight" ]] && printf 'preflight_pass' || printf 'dry_run_pass')" > "$OUTPUT_ROOT/parsed/main10.tsv"
    printf 'benchmark\tmethod\tseed\tstatus\texpected\n%s\t%s\t%s\t%s\tpreregistered\n' "$BENCHMARK" "$METHOD" "$SEED" "$([[ "$MODE" == "main10-preflight" ]] && printf 'preflight_pass' || printf 'dry_run_pass')" > "$OUTPUT_ROOT/summary/main10.tsv"
    SAFE_STATUS="dry_run_pass"
    [[ "$MODE" == "main10-preflight" ]] && SAFE_STATUS="preflight_pass"
    write_status "$SAFE_STATUS" 1 "$(date --iso-8601=seconds)"
    write_checksums
    printf 'Main10 safe check finished: %s (%s)\n' "$OUTPUT_ROOT" "$SAFE_STATUS"
    exit 0
fi

if ! solc-select use "$COMPILER" > "$OUTPUT_ROOT/raw/solc-select.log" 2>&1; then
    FAILED_STAGE="solc_select"
    EXIT_CODE=1
    write_status "startup_error" 0 "$(date --iso-8601=seconds)"
    write_checksums
    exit 1
fi

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

if [[ "$MODE" == "preflight" || "$MODE" == "pilot-preflight" ]]; then
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

if [[ "$MODE" == "pilot" || "$MODE" == "main10" ]]; then
    PREFLIGHT_ROOT="$PHASE06A_ROOT/$BENCHMARK-preflight"
    if [[ ! -f "$PREFLIGHT_ROOT/generated/harness-k1.sol" || ! -f "$PREFLIGHT_ROOT/generated/harness-k5.sol" ]]; then
        for candidate in "$PHASE06A_ROOT"/"$BENCHMARK-preflight-"*; do
            if [[ -f "$candidate/generated/harness-k1.sol" && -f "$candidate/generated/harness-k5.sol" && -f "$candidate/status/status.env" ]] && grep -q '^STATUS=preflight_pass$' "$candidate/status/status.env"; then
                PREFLIGHT_ROOT="$candidate"
            fi
        done
    fi
else
    PREFLIGHT_ROOT="$PUBLIC_SMOKE_ROOT/$BENCHMARK-preflight"
fi
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
