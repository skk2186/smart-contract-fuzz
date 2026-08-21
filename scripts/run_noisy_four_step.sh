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

mkdir -p results/noisy-four-step/original
mkdir -p results/noisy-four-step/guided
mkdir -p results/noisy-four-step/random

rm -f results/noisy-four-step/original/seed-*.log
rm -f results/noisy-four-step/guided/seed-*.log
rm -f results/noisy-four-step/random/seed-*.log

run_echidna() {
    local contract_file="$1"
    local contract_name="$2"
    local config_file="$3"
    local seed="$4"
    local log_file="$5"

    echo "Running: $log_file"

    {
        /usr/bin/time \
          -f "PROCESS_WALL_SECONDS=%e" \
          echidna "$contract_file" \
            --contract "$contract_name" \
            --config "$config_file" \
            --seed "$seed"

        echo "EXIT_CODE=$?"
    } > "$log_file" 2>&1
}

# 原始 Echidna 组
for seed in 1 2 3 4 5 6 7 8 9 10
do
    run_echidna \
      "contracts/benchmarks/NoisyFourStepExample.sol" \
      "NoisyFourStepExample" \
      "configs/echidna-noisy-original.yaml" \
      "$seed" \
      "results/noisy-four-step/original/seed-${seed}.log"
done

# 属性相关状态依赖引导组
for seed in 1 2 3 4 5 6 7 8 9 10
do
    run_echidna \
      "contracts/harnesses/guided/NoisyFourStepGuidedHarness.sol" \
      "NoisyFourStepGuidedHarness" \
      "configs/echidna-noisy-harness.yaml" \
      "$seed" \
      "results/noisy-four-step/guided/seed-${seed}.log"
done

# 随机 Harness 组：
# 第 i 次实验使用第 i 个随机 Harness 和第 i 个 Echidna seed。
for experiment_id in 1 2 3 4 5 6 7 8 9 10
do
    run_echidna \
      "contracts/harnesses/random/NoisyFourStepRandomHarness-${experiment_id}.sol" \
      "NoisyFourStepRandomHarness" \
      "configs/echidna-noisy-harness.yaml" \
      "$experiment_id" \
      "results/noisy-four-step/random/seed-${experiment_id}.log"
done

echo "All noisy four-step experiments completed."
