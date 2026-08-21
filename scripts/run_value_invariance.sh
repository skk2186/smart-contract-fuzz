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

run_group() {
    local method="$1"
    local contract_file="$2"
    local contract_name="$3"

    local output_directory
    output_directory="results/value-invariance/${method}"

    mkdir -p "$output_directory"
    rm -f "${output_directory}"/seed-*.log

    for seed in $(seq 1 30)
    do
        echo "Running ${method}, seed=${seed}"

        {
            /usr/bin/time \
              -f "PROCESS_WALL_SECONDS=%e" \
              echidna "$contract_file" \
                --contract "$contract_name" \
                --config configs/echidna-branch-value-harness.yaml \
                --seed "$seed"

            echo "EXIT_CODE=$?"
        } > "${output_directory}/seed-${seed}.log" 2>&1
    done
}

run_group \
  "value-original-k1" \
  "contracts/harnesses/value-invariance/BranchValueValueK1Harness.sol" \
  "BranchValueValueK1Harness"

run_group \
  "value-reordered-k1" \
  "contracts/harnesses/value-invariance/BranchValueReorderedValueK1Harness.sol" \
  "BranchValueReorderedValueK1Harness"

run_group \
  "value-renamed-k1" \
  "contracts/harnesses/value-invariance/BranchValueRenamedValueK1Harness.sol" \
  "BranchValueRenamedValueK1Harness"

echo "Value-guided invariance experiments completed."
