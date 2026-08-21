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

for command_name in echidna slither solc
do
    if ! command -v "$command_name" >/dev/null 2>&1
    then
        echo "Error: $command_name not found"
        exit 1
    fi
done

run_group() {
    local method="$1"
    local contract_file="$2"
    local contract_name="$3"
    local config_file="$4"

    local result_directory
    result_directory="results/branch-value/${method}"

    mkdir -p "$result_directory"
    rm -f "${result_directory}"/seed-*.log

    for seed in $(seq 1 30)
    do
        local log_file
        log_file="${result_directory}/seed-${seed}.log"

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
    done
}

run_group \
  "original" \
  "contracts/benchmarks/BranchValueExample.sol" \
  "BranchValueExample" \
  "configs/echidna-branch-value-original.yaml"

for k in 1 3 4 5 10
do
    run_group \
      "property-k${k}" \
      "contracts/harnesses/branch-value/BranchValuePropertyK${k}Harness.sol" \
      "BranchValuePropertyK${k}Harness" \
      "configs/echidna-branch-value-harness.yaml"
done

echo "BranchValueExample experiments completed."
