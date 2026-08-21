#!/usr/bin/env bash

set -u
set -o pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
MANIFEST="results/public-benchmarks/c1/manifest.tsv"
OUTPUT_ROOT="results/public-benchmarks/c1/smoke"

cd "$ROOT" || exit 1

export PATH="$CONDA_PREFIX/bin:$PATH"

mkdir -p "$OUTPUT_ROOT"

while IFS=$'\t' read -r \
    benchmark \
    method \
    compiler \
    contract_file \
    contract_name \
    config_file
do
    benchmark="${benchmark%$'\r'}"
    method="${method%$'\r'}"
    compiler="${compiler%$'\r'}"
    contract_file="${contract_file%$'\r'}"
    contract_name="${contract_name%$'\r'}"
    config_file="${config_file%$'\r'}"

    if [[ "$benchmark" == "benchmark" ]]
    then
        continue
    fi

    output_directory="${OUTPUT_ROOT}/${benchmark}"
    mkdir -p "$output_directory"

    echo "Smoke: ${benchmark}/${method}"

    solc-select use "$compiler" || exit 1

    echidna "$contract_file" \
      --contract "$contract_name" \
      --config "$config_file" \
      --seed 1 \
      > "${output_directory}/${method}.log" \
      2>&1

done < <(sed 's/\r$//' "$MANIFEST")

solc-select use 0.8.20

echo "Public C-1 smoke tests completed."
