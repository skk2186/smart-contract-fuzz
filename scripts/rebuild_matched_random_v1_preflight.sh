#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
RESULT_DIR="${PROJECT_ROOT}/results/matched-random-v1"

cd "${PROJECT_ROOT}"
export PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/matched_random_v1_pycache"

python3 -m py_compile \
  analyzer/build_matched_random_schedule.py \
  analyzer/generate_matched_random_harnesses.py \
  analyzer/preflight_matched_random_harnesses.py \
  analyzer/tests/test_matched_random_schedule.py \
  analyzer/tests/test_generate_matched_random_harnesses.py

python3 -m unittest \
  analyzer.tests.test_matched_random_schedule \
  analyzer.tests.test_generate_matched_random_harnesses -v

python3 analyzer/build_matched_random_schedule.py \
  --manifest "${RESULT_DIR}/cases.tsv" \
  --project-root "${PROJECT_ROOT}" \
  --runs 30 \
  --top-k 1 \
  --schedule-seed 20260805 \
  --output-schedule "${RESULT_DIR}/matched-random-schedule.csv" \
  --output-cases "${RESULT_DIR}/case-summary.csv" \
  --report "${RESULT_DIR}/preregistration-report.md"

python3 analyzer/generate_matched_random_harnesses.py \
  --project-root "${PROJECT_ROOT}" \
  --cases "${RESULT_DIR}/cases.tsv" \
  --schedule "${RESULT_DIR}/matched-random-schedule.csv" \
  --output-root "${PROJECT_ROOT}/contracts/harnesses/matched-random-v1" \
  --harness-manifest "${RESULT_DIR}/harness-manifest.csv" \
  --execution-manifest "${RESULT_DIR}/execution-manifest.tsv"

python3 analyzer/preflight_matched_random_harnesses.py \
  --project-root "${PROJECT_ROOT}" \
  --manifest "${RESULT_DIR}/harness-manifest.csv" \
  --log-root "${RESULT_DIR}/preflight/logs" \
  --output-csv "${RESULT_DIR}/preflight/compile-preflight.csv" \
  --report "${RESULT_DIR}/preflight/report.md"

echo "Matched-random V1 schedule and compile preflight rebuilt."
