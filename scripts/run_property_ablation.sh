#!/usr/bin/env bash

set -u
set -o pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
cd "$ROOT" || exit 1

if [[ -z "${CONDA_PREFIX:-}" ]]; then
    echo "Error: activate the Conda environment first:"
    echo "conda activate contract-fuzz"
    exit 1
fi

export PATH="$CONDA_PREFIX/bin:$PATH"

for command_name in echidna slither solc
do
    if ! command -v "$command_name" >/dev/null 2>&1
    then
        echo "Error: $command_name not found"
        exit 1
    fi
done

mkdir -p results/ablation/original
mkdir -p results/ablation/dependency
mkdir -p results/ablation/property

rm -f results/ablation/original/seed-*.log
rm -f results/ablation/dependency/seed-*.log
rm -f results/ablation/property/seed-*.log

run_group() {
    local method="$1"
    local contract_file="$2"
    local contract_name="$3"
    local config_file="$4"

    for seed in 1 2 3 4 5 6 7 8 9 10
    do
        local log_file
        log_file="results/ablation/${method}/seed-${seed}.log"

        echo "Running method=${method}, seed=${seed}"

        {
            /usr/bin/time \
              -f "PROCESS_WALL_SECONDS=%e" \
              echidna "$contract_file" \
                --contract "$contract_name" \
                --config "$config_file" \
                --seed "$seed"

            echo "EXIT_CODE=$?"
        } > "$log_file" 2>&1

        echo "Finished method=${method}, seed=${seed}"
    done
}

run_group \
  "original" \
  "contracts/benchmarks/NoisyFourStepExample.sol" \
  "NoisyFourStepExample" \
  "configs/echidna-noisy-original.yaml"

run_group \
  "dependency" \
  "contracts/harnesses/dependency-generated/NoisyFourStepDependencyHarness.sol" \
  "NoisyFourStepDependencyHarness" \
  "configs/echidna-noisy-harness.yaml"

run_group \
  "property" \
  "contracts/harnesses/property-generated/NoisyFourStepPropertyHarness.sol" \
  "NoisyFourStepPropertyHarness" \
  "configs/echidna-noisy-harness.yaml"

echo "Property relevance ablation completed."
