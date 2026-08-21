#!/usr/bin/env bash

set -u
set -o pipefail

ROOT="$HOME/smart-contract-fuzzing"
cd "$ROOT" || exit 1

if [[ -z "${CONDA_PREFIX:-}" ]]; then
    echo "Run first: conda activate contract-fuzz"
    exit 1
fi

export PATH="$CONDA_PREFIX/bin:$PATH"

prepare_case() {
    local benchmark="$1"
    local source="$2"
    local contract="$3"

    local output_directory
    output_directory="results/formal/candidates/${benchmark}"

    mkdir -p "$output_directory"

    echo "Preparing candidate statistics: ${benchmark}"

    python analyzer/extract_rw.py \
      "$source" \
      > "${output_directory}/rw.json"

    python analyzer/generate_sequences.py \
      "${output_directory}/rw.json" \
      4 \
      500 \
      > "${output_directory}/dependency.json"

    python analyzer/generate_property_sequences.py \
      "${output_directory}/rw.json" \
      4 \
      500 \
      > "${output_directory}/property.json"

    python analyzer/generate_repetition_aware_sequences.py \
      "${output_directory}/rw.json" \
      4 \
      500 \
      --contract "$contract" \
      --max-function-visits 2 \
      > "${output_directory}/repeat-property.json"

    python analyzer/extract_value_constraints.py \
      "$source" \
      --contract "$contract" \
      > "${output_directory}/value-constraints.json"

    python analyzer/generate_value_guided_sequences.py \
      "${output_directory}/repeat-property.json" \
      "${output_directory}/value-constraints.json" \
      --contract "$contract" \
      > "${output_directory}/full.json"

    jq empty "${output_directory}/dependency.json"
    jq empty "${output_directory}/property.json"
    jq empty "${output_directory}/repeat-property.json"
    jq empty "${output_directory}/full.json"
}

prepare_case \
  "noisy-four-step" \
  "contracts/benchmarks/NoisyFourStepExample.sol" \
  "NoisyFourStepExample"

prepare_case \
  "reset-example" \
  "contracts/benchmarks/ResetExample.sol" \
  "ResetExample"

prepare_case \
  "branch-value" \
  "contracts/benchmarks/BranchValueExample.sol" \
  "BranchValueExample"

prepare_case \
  "repeated-call" \
  "contracts/benchmarks/RepeatedCallExample.sol" \
  "RepeatedCallExample"

echo "Formal candidate files generated."
