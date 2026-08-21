#!/usr/bin/env bash

set -u
set -o pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
cd "$ROOT" || exit 1

if [[ -z "${CONDA_PREFIX:-}" ]]; then
    echo "Run first: conda activate contract-fuzz"
    exit 1
fi

export PATH="$CONDA_PREFIX/bin:$PATH"

run_group() {
    local method="$1"
    local contract_file="$2"
    local contract_name="$3"

    local result_directory
    result_directory="results/repeated-call/repeat-ablation/${method}"

    mkdir -p "$result_directory"
    rm -f "${result_directory}"/seed-*.log

    for seed in $(seq 1 30)
    do
        echo "Running ${method}, seed=${seed}"

        {
            /usr/bin/time \
              -f "PROCESS_WALL_SECONDS=%e" \
              echidna "$contract_file" \
                --contract "$contract_name" \
                --config configs/echidna-repeated-harness.yaml \
                --seed "$seed"

            echo "EXIT_CODE=$?"
        } > "${result_directory}/seed-${seed}.log" 2>&1
    done
}

run_group \
  "visits-1-k1" \
  "contracts/harnesses/repeated-call/generated/RepeatedCallVisits1K1Harness.sol" \
  "RepeatedCallVisits1K1Harness"

run_group \
  "visits-2-k1" \
  "contracts/harnesses/repeated-call/generated/RepeatedCallVisits2K1Harness.sol" \
  "RepeatedCallVisits2K1Harness"

echo "Repeated-call ablation completed."
