#!/usr/bin/env bash

set -u
set -o pipefail

ROOT="$HOME/smart-contract-fuzzing"
MANIFEST="results/public-benchmarks/c1/manifest.tsv"
RUN_ROOT="results/public-benchmarks/c1/runs"

cd "$ROOT" || exit 1

if [[ -z "${CONDA_PREFIX:-}" ]]; then
    echo "Activate contract-fuzz first."
    exit 1
fi

export PATH="$CONDA_PREFIX/bin:$PATH"

mkdir -p "$RUN_ROOT"

total_groups=$(
    tail -n +2 "$MANIFEST" |
    sed 's/\r$//' |
    sed '/^[[:space:]]*$/d' |
    wc -l
)

current_group=0

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

    if [[ -z "$benchmark" ]]
    then
        continue
    fi

    if [[ ! -f "$contract_file" ]]
    then
        printf 'Contract not found: %q\n' "$contract_file"
        exit 1
    fi

    if [[ ! -f "$config_file" ]]
    then
        printf 'Config not found: %q\n' "$config_file"
        exit 1
    fi

    current_group=$((current_group + 1))

    output_directory="${RUN_ROOT}/${benchmark}/${method}"
    mkdir -p "$output_directory"

    echo
    echo "================================================"
    echo "Group     : ${current_group}/${total_groups}"
    echo "Benchmark : ${benchmark}"
    echo "Method    : ${method}"
    echo "Compiler  : ${compiler}"
    echo "================================================"

    solc-select use "$compiler" || exit 1

    for seed in $(seq 1 30)
    do
        log_file="${output_directory}/seed-${seed}.log"

        if [[ -f "$log_file" && "${FORCE:-0}" != "1" ]]
        then
            if grep -q \
              "PUBLIC_C1_RUN_COMPLETED=1" \
              "$log_file"
            then
                echo "Skip completed: ${benchmark}/${method}/${seed}"
                continue
            fi
        fi

        echo "Running ${benchmark}/${method}/seed-${seed}"

        temp_log="${log_file}.tmp"

        {
            echo "METHOD_VERSION=Full-v1.0.1-compat"
            echo "FORMAL_BATCH=C-1"
            echo "BENCHMARK=${benchmark}"
            echo "METHOD=${method}"
            echo "COMPILER=${compiler}"
            echo "SEED=${seed}"
            echo "CONTRACT_FILE=${contract_file}"
            echo "CONTRACT_NAME=${contract_name}"
            echo "CONFIG_FILE=${config_file}"
            echo "START_TIME=$(date --iso-8601=seconds)"
            echo

            echo "===== SOLC VERSION ====="
            solc --version
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

        } > "$temp_log" 2>&1

        if grep -qiE \
          "doesn't support versions of solc before|\
compilation failed|\
ParserError|\
File outside of allowed directories|\
Config .* not found|\
Source .* not found|\
Could not compile" \
          "$temp_log"
        then
            run_status="startup_error"

        elif grep -qiE \
          "Test echidna_[A-Za-z0-9_]+ falsified|\
echidna_[A-Za-z0-9_]+:[[:space:]]*\
(failed|falsified|passed|passing)" \
          "$temp_log"
        then
            run_status="valid"

        else
            run_status="unknown_error"
        fi

        {
            cat "$temp_log"
            echo
            echo "PUBLIC_C1_RUN_STATUS=${run_status}"

            if [[ "$run_status" == "valid" ]]
            then
                echo "PUBLIC_C1_RUN_COMPLETED=1"
            fi
        } > "$log_file"

        rm -f "$temp_log"
    done

done < <(sed 's/\r$//' "$MANIFEST")

solc-select use 0.8.20

echo
echo "Public C-1 experiments completed."
