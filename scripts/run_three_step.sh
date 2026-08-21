#!/usr/bin/env bash

set -u
set -o pipefail

ROOT="$HOME/smart-contract-fuzzing"
cd "$ROOT" || exit 1

if [[ -z "${CONDA_PREFIX:-}" ]]; then
    echo "Error: Conda environment is not activated."
    echo "Run: conda activate contract-fuzz"
    exit 1
fi

export PATH="$CONDA_PREFIX/bin:$PATH"

for command_name in echidna slither solc; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
        echo "Error: $command_name not found in PATH"
        exit 1
    fi
done

mkdir -p results/three-step/original
mkdir -p results/three-step/guided
mkdir -p results/three-step/wrong-order

run_group() {
    local method="$1"
    local contract_file="$2"
    local contract_name="$3"
    local config_file="$4"

    for seed in 1 2 3 4 5 6 7 8 9 10
    do
        local log_file
        log_file="results/three-step/${method}/seed-${seed}.log"

        echo "Running method=${method}, seed=${seed}"

        echidna "$contract_file" \
          --contract "$contract_name" \
          --config "$config_file" \
          --seed "$seed" \
          > "$log_file" 2>&1

        local exit_code=$?
        echo "EXIT_CODE=${exit_code}" >> "$log_file"

        echo "Finished method=${method}, seed=${seed}, exit=${exit_code}"
    done
}

run_group \
  "original" \
  "contracts/benchmarks/ThreeStepExample.sol" \
  "ThreeStepExample" \
  "configs/echidna-three-step-original.yaml"

run_group \
  "guided" \
  "contracts/harnesses/guided/ThreeStepGuidedHarness.sol" \
  "ThreeStepGuidedHarness" \
  "configs/echidna-three-step-harness.yaml"

run_group \
  "wrong-order" \
  "contracts/harnesses/wrong-order/ThreeStepWrongOrderHarness.sol" \
  "ThreeStepWrongOrderHarness" \
  "configs/echidna-three-step-harness.yaml"

echo "All experiments completed."
