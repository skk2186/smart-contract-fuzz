#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RESULT_ROOT="results/public-benchmarks/c1"

benchmarks=(
    echidna-flags
    echidna-multi
    exercise2-access-control
    smartbugs-multifunc
    smartbugs-onefunc
)

cd "${ROOT}"

for benchmark in "${benchmarks[@]}"; do
    python3 analyzer/parse_experiment_logs.py \
        "${RESULT_ROOT}/runs/${benchmark}" \
        "${RESULT_ROOT}/parsed/${benchmark}.csv"

    python3 analyzer/summarize_experiment.py \
        "${RESULT_ROOT}/parsed/${benchmark}.csv" \
        "${RESULT_ROOT}/grouped/${benchmark}.csv"
done

python3 analyzer/build_public_c1_group_summary.py
python3 analyzer/check_public_c1_paths.py
