#!/usr/bin/env bash

set -u
set -o pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
RESULT_ROOT="results/public-benchmarks/c1/preparation"
HARNESS_ROOT="contracts/harnesses/public-c1"

cd "$ROOT" || exit 1

if [[ -z "${CONDA_PREFIX:-}" ]]; then
    echo "Activate contract-fuzz first."
    exit 1
fi

export PATH="$CONDA_PREFIX/bin:$PATH"

mkdir -p "$RESULT_ROOT"
mkdir -p "$HARNESS_ROOT"

prepare_case() {
    local benchmark="$1"
    local compiler="$2"
    local source="$3"
    local contract="$4"
    local harness_prefix="$5"

    local output_directory
    output_directory="${RESULT_ROOT}/${benchmark}"

    mkdir -p "$output_directory"

    echo
    echo "================================================"
    echo "Preparing: ${benchmark}"
    echo "Compiler : ${compiler}"
    echo "Contract : ${contract}"
    echo "================================================"

    solc-select use "$compiler" || return 1

    solc --bin "$source" \
      > "${output_directory}/source-bin.log" \
      2> "${output_directory}/source-compile.stderr.log" \
      || return 1

    python analyzer/extract_rw.py \
      "$source" \
      > "${output_directory}/rw.json" \
      2> "${output_directory}/extract-rw.stderr.log" \
      || return 1

    python analyzer/generate_repetition_aware_sequences.py \
      "${output_directory}/rw.json" \
      4 \
      500 \
      --contract "$contract" \
      --max-function-visits 2 \
      > "${output_directory}/repeat-property.json" \
      2> "${output_directory}/repeat-property.stderr.log" \
      || return 1

    python analyzer/extract_value_constraints.py \
      "$source" \
      --contract "$contract" \
      > "${output_directory}/value-constraints.json" \
      2> "${output_directory}/value-constraints.stderr.log" \
      || return 1

    python analyzer/generate_value_guided_sequences.py \
      "${output_directory}/repeat-property.json" \
      "${output_directory}/value-constraints.json" \
      --contract "$contract" \
      > "${output_directory}/full.json" \
      2> "${output_directory}/full.stderr.log" \
      || return 1

    python analyzer/generate_harness_from_paths.py \
      --source "$source" \
      --sequences "${output_directory}/full.json" \
      --target-contract "$contract" \
      --harness-contract "${harness_prefix}K1Harness" \
      --output "${HARNESS_ROOT}/${harness_prefix}K1Harness.sol" \
      --prefix full \
      --top-k 1 \
      --solidity-pragma "$compiler" \
      2> "${output_directory}/harness-k1.stderr.log" \
      || return 1

    python analyzer/generate_harness_from_paths.py \
      --source "$source" \
      --sequences "${output_directory}/full.json" \
      --target-contract "$contract" \
      --harness-contract "${harness_prefix}K5Harness" \
      --output "${HARNESS_ROOT}/${harness_prefix}K5Harness.sol" \
      --prefix full \
      --top-k 5 \
      --solidity-pragma "$compiler" \
      2> "${output_directory}/harness-k5.stderr.log" \
      || return 1

    solc \
      --allow-paths "$ROOT/contracts" \
      --bin \
      "${HARNESS_ROOT}/${harness_prefix}K1Harness.sol" \
      > "${output_directory}/harness-k1-bin.log" \
      2> "${output_directory}/harness-k1-compile.stderr.log" \
      || return 1

    solc \
      --allow-paths "$ROOT/contracts" \
      --bin \
      "${HARNESS_ROOT}/${harness_prefix}K5Harness.sol" \
      > "${output_directory}/harness-k5-bin.log" \
      2> "${output_directory}/harness-k5-compile.stderr.log" \
      || return 1

    jq empty "${output_directory}/rw.json"
    jq empty "${output_directory}/repeat-property.json"
    jq empty "${output_directory}/value-constraints.json"
    jq empty "${output_directory}/full.json"

    echo "Prepared ${benchmark}"
}

prepare_case \
  "echidna-multi" \
  "0.8.20" \
  "contracts/public-benchmarks/raw/echidna/multi.sol" \
  "C" \
  "PublicEchidnaMultiFull" \
  || exit 1

prepare_case \
  "echidna-flags" \
  "0.8.20" \
  "contracts/public-benchmarks/adapted/EchidnaFlagsTarget.sol" \
  "PublicEchidnaFlagsTarget" \
  "PublicEchidnaFlagsFull" \
  || exit 1

prepare_case \
  "exercise2-access-control" \
  "0.8.20" \
  "contracts/public-benchmarks/raw/exercise2/solution.sol" \
  "TestToken" \
  "PublicExercise2Full" \
  || exit 1

prepare_case \
  "smartbugs-multifunc" \
  "0.4.25" \
  "contracts/public-benchmarks/adapted/SmartBugsMultiFuncEchidna.sol" \
  "SmartBugsMultiFuncEchidna" \
  "PublicSmartBugsMultiFuncFull" \
  || exit 1

prepare_case \
  "smartbugs-onefunc" \
  "0.4.25" \
  "contracts/public-benchmarks/adapted/SmartBugsOneFuncEchidna.sol" \
  "SmartBugsOneFuncEchidna" \
  "PublicSmartBugsOneFuncFull" \
  || exit 1

solc-select use 0.8.20

echo
echo "Public C-1 preparation completed."
