#!/usr/bin/env bash

set -u
set -o pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
cd "$ROOT" || exit 1

if [[ -z "${CONDA_PREFIX:-}" ]]; then
    echo "Error: Conda environment is not activated."
    echo "Run: conda activate contract-fuzz"
    exit 1
fi

export PATH="$CONDA_PREFIX/bin:$PATH"

for required_command in echidna slither solc
do
    if ! command -v "$required_command" >/dev/null 2>&1
    then
        echo "Error: $required_command not found"
        exit 1
    fi
done

RESULT_ROOT="results/noisy-four-step/permuted"
mkdir -p "$RESULT_ROOT"

for harness_id in $(seq -w 1 24)
do
    harness_file="contracts/harnesses/permuted/NoisyFourStepPermutationHarness-${harness_id}.sol"
    harness_result="${RESULT_ROOT}/harness-${harness_id}"

    mkdir -p "$harness_result"
    rm -f "${harness_result}"/seed-*.log

    for seed in 1 2 3 4 5
    do
        log_file="${harness_result}/seed-${seed}.log"

        echo \
          "Running harness=${harness_id}, seed=${seed}"

        {
            /usr/bin/time \
              -f "PROCESS_WALL_SECONDS=%e" \
              echidna "$harness_file" \
                --contract NoisyFourStepPermutationHarness \
                --config configs/echidna-noisy-harness.yaml \
                --seed "$seed"

            echo "EXIT_CODE=$?"
        } > "$log_file" 2>&1
    done
done

echo "All permutation experiments completed."
