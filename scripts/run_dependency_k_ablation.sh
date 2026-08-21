#!/usr/bin/env bash

set -u
set -o pipefail

ROOT="$HOME/smart-contract-fuzzing"
cd "$ROOT" || exit 1

if [[ -z "${CONDA_PREFIX:-}" ]]; then
    echo "Please run: conda activate contract-fuzz"
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

for k in 1 3 5 10
do
    result_directory="results/ablation-k/dependency-k${k}"
    mkdir -p "$result_directory"
    rm -f "${result_directory}"/seed-*.log

    for seed in $(seq 1 30)
    do
        contract_file="contracts/harnesses/dependency-k/NoisyFourStepDependencyK${k}Harness.sol"
        contract_name="NoisyFourStepDependencyK${k}Harness"
        log_file="${result_directory}/seed-${seed}.log"

        echo "Running Dependency-K${k}, seed=${seed}"

        {
            /usr/bin/time \
              -f "PROCESS_WALL_SECONDS=%e" \
              echidna "$contract_file" \
                --contract "$contract_name" \
                --config configs/echidna-noisy-harness.yaml \
                --seed "$seed"

            echo "EXIT_CODE=$?"
        } > "$log_file" 2>&1
    done
done

echo "Dependency K ablation completed."
