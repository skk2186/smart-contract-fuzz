#!/usr/bin/env bash

set -u
set -o pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
cd "$ROOT" || exit 1

export PATH="$CONDA_PREFIX/bin:$PATH"

mkdir -p results/formal/preparation
mkdir -p contracts/harnesses/formal

prepare_full() {
    local benchmark="$1"
    local source_file="$2"
    local contract_name="$3"
    local rw_file="$4"
    local harness_name="$5"

    local output_dir
    output_dir="results/formal/preparation/${benchmark}"

    mkdir -p "$output_dir"

    echo "=========================================="
    echo "Preparing Full-v1.0: ${benchmark}"
    echo "=========================================="

    python analyzer/extract_value_constraints.py \
      "$source_file" \
      --contract "$contract_name" \
      > "${output_dir}/value-constraints.json" \
      || return 1

    python analyzer/generate_repetition_aware_sequences.py \
      "$rw_file" \
      4 \
      500 \
      --contract "$contract_name" \
      --max-function-visits 2 \
      > "${output_dir}/repeat-property-sequences.json" \
      || return 1

    python analyzer/generate_value_guided_sequences.py \
      "${output_dir}/repeat-property-sequences.json" \
      "${output_dir}/value-constraints.json" \
      --contract "$contract_name" \
      > "${output_dir}/full-sequences.json" \
      || return 1

    python analyzer/generate_harness_from_paths.py \
      --source "$source_file" \
      --sequences "${output_dir}/full-sequences.json" \
      --target-contract "$contract_name" \
      --harness-contract "$harness_name" \
      --output "contracts/harnesses/formal/${harness_name}.sol" \
      --prefix full \
      --top-k 1 \
      || return 1

    solc --bin \
      "contracts/harnesses/formal/${harness_name}.sol" \
      >/dev/null \
      || return 1

    echo "Prepared: ${harness_name}"
}

prepare_full \
  "noisy-four-step" \
  "contracts/benchmarks/NoisyFourStepExample.sol" \
  "NoisyFourStepExample" \
  "results/noisy-four-step/NoisyFourStepExample-rw.json" \
  "NoisyFourStepFullK1Harness" \
  || exit 1

prepare_full \
  "reset-example" \
  "contracts/benchmarks/ResetExample.sol" \
  "ResetExample" \
  "results/reset-example/ResetExample-rw.json" \
  "ResetFullK1Harness" \
  || exit 1

prepare_full \
  "branch-value" \
  "contracts/benchmarks/BranchValueExample.sol" \
  "BranchValueExample" \
  "results/branch-value/BranchValueExample-rw.json" \
  "BranchValueFullK1Harness" \
  || exit 1

prepare_full \
  "repeated-call" \
  "contracts/benchmarks/RepeatedCallExample.sol" \
  "RepeatedCallExample" \
  "results/repeated-call/RepeatedCallExample-rw.json" \
  "RepeatedCallFullK1Harness" \
  || exit 1

echo "All Full-v1.0 Harnesses were generated and compiled."
