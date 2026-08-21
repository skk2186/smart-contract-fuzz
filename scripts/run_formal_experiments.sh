#!/usr/bin/env bash

set -u
set -o pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
MANIFEST="results/formal/manifest.tsv"
RUN_ROOT="results/formal/runs"

cd "$ROOT" || exit 1

if [[ -z "${CONDA_PREFIX:-}" ]]; then
    echo "Error: activate the environment first:"
    echo "conda activate contract-fuzz"
    exit 1
fi

export PATH="$CONDA_PREFIX/bin:$PATH"

for command_name in echidna solc python
do
    if ! command -v "$command_name" >/dev/null 2>&1
    then
        echo "Error: ${command_name} not found"
        exit 1
    fi
done

if [[ ! -f "$MANIFEST" ]]
then
    echo "Error: manifest not found: $MANIFEST"
    exit 1
fi

mkdir -p "$RUN_ROOT"

total_groups=$(
    tail -n +2 "$MANIFEST" |
    sed '/^[[:space:]]*$/d' |
    wc -l
)

current_group=0

while IFS=$'\t' read -r \
    benchmark \
    method \
    contract_file \
    contract_name \
    config_file
do
    if [[ "$benchmark" == "benchmark" ]]
    then
        continue
    fi

    if [[ -z "$benchmark" ]]
    then
        continue
    fi

    current_group=$((current_group + 1))

    result_directory="${RUN_ROOT}/${benchmark}/${method}"
    mkdir -p "$result_directory"

    echo
    echo "=================================================="
    echo "Group ${current_group}/${total_groups}"
    echo "Benchmark : ${benchmark}"
    echo "Method    : ${method}"
    echo "Contract  : ${contract_name}"
    echo "=================================================="

    for seed in $(seq 1 30)
    do
        log_file="${result_directory}/seed-${seed}.log"

        if [[ -f "$log_file" && "${FORCE:-0}" != "1" ]]
        then
            if grep -q "FORMAL_RUN_COMPLETED=1" "$log_file"
            then
                echo "Skip completed: ${benchmark}/${method}/seed-${seed}"
                continue
            fi
        fi

        echo "Running: ${benchmark}/${method}/seed-${seed}"

        {
            echo "FORMAL_EXPERIMENT_VERSION=Full-v1.0"
            echo "BENCHMARK=${benchmark}"
            echo "METHOD=${method}"
            echo "SEED=${seed}"
            echo "CONTRACT_FILE=${contract_file}"
            echo "CONTRACT_NAME=${contract_name}"
            echo "CONFIG_FILE=${config_file}"
            echo "START_TIME=$(date --iso-8601=seconds)"
            echo

            /usr/bin/time \
              -f "PROCESS_WALL_SECONDS=%e" \
              echidna "$contract_file" \
                --contract "$contract_name" \
                --config "$config_file" \
                --seed "$seed"

            exit_code=$?

            echo
            echo "EXIT_CODE=${exit_code}"
            echo "END_TIME=$(date --iso-8601=seconds)"
            echo "FORMAL_RUN_COMPLETED=1"

        } > "$log_file" 2>&1
    done

done < "$MANIFEST"

echo
echo "All formal experiment groups completed."
