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

mkdir -p results/formal-b2/preparation
mkdir -p contracts/harnesses/formal-b2

prepare_case() {
    local benchmark="$1"
    local source="$2"
    local contract="$3"

    local output_directory
    output_directory="results/formal-b2/preparation/${benchmark}"

    mkdir -p "$output_directory"

    echo "Preparing ${benchmark}"

    python analyzer/extract_rw.py \
      "$source" \
      > "${output_directory}/rw.json" \
      || return 1

    python analyzer/generate_repetition_aware_sequences.py \
      "${output_directory}/rw.json" \
      4 \
      500 \
      --contract "$contract" \
      --max-function-visits 2 \
      > "${output_directory}/repeat-property-sequences.json" \
      || return 1

    python analyzer/extract_value_constraints.py \
      "$source" \
      --contract "$contract" \
      > "${output_directory}/value-constraints.json" \
      || return 1

    python analyzer/generate_value_guided_sequences.py \
      "${output_directory}/repeat-property-sequences.json" \
      "${output_directory}/value-constraints.json" \
      --contract "$contract" \
      > "${output_directory}/full-sequences.json" \
      || return 1

    jq empty "${output_directory}/rw.json"
    jq empty "${output_directory}/repeat-property-sequences.json"
    jq empty "${output_directory}/value-constraints.json"
    jq empty "${output_directory}/full-sequences.json"
}

prepare_case \
  "alternative-path" \
  "contracts/benchmarks/AlternativePathExample.sol" \
  "AlternativePathExample" \
  || exit 1

prepare_case \
  "multi-property" \
  "contracts/benchmarks/MultiPropertyExample.sol" \
  "MultiPropertyExample" \
  || exit 1

python analyzer/generate_harness_from_paths.py \
  --source contracts/benchmarks/AlternativePathExample.sol \
  --sequences results/formal-b2/preparation/alternative-path/full-sequences.json \
  --target-contract AlternativePathExample \
  --harness-contract AlternativePathFullK1Harness \
  --output contracts/harnesses/formal-b2/AlternativePathFullK1Harness.sol \
  --prefix full \
  --top-k 1 \
  || exit 1

python analyzer/generate_harness_from_paths.py \
  --source contracts/benchmarks/AlternativePathExample.sol \
  --sequences results/formal-b2/preparation/alternative-path/full-sequences.json \
  --target-contract AlternativePathExample \
  --harness-contract AlternativePathFullK2Harness \
  --output contracts/harnesses/formal-b2/AlternativePathFullK2Harness.sol \
  --prefix full \
  --top-k 2 \
  || exit 1

python analyzer/generate_harness_from_paths.py \
  --source contracts/benchmarks/MultiPropertyExample.sol \
  --sequences results/formal-b2/preparation/multi-property/full-sequences.json \
  --target-contract MultiPropertyExample \
  --harness-contract MultiPropertyFullK1Harness \
  --output contracts/harnesses/formal-b2/MultiPropertyFullK1Harness.sol \
  --prefix full \
  --top-k 1 \
  || exit 1

for file in contracts/harnesses/formal-b2/*.sol
do
    echo "Compiling $file"
    solc --bin "$file" >/dev/null || exit 1
done

echo "Formal B-2 preparation completed."
