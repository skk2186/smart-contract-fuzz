#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
RESULT_DIR="${PROJECT_ROOT}/results/public-benchmarks/c2-screening"

cd "${PROJECT_ROOT}"
export PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/c2_readiness_pycache"

python3 -m py_compile \
  analyzer/audit_baseline_feasibility.py \
  analyzer/validate_c2_candidate_registry.py \
  analyzer/tests/test_c2_readiness.py

python3 -m unittest analyzer.tests.test_c2_readiness -v

python3 analyzer/validate_c2_candidate_registry.py \
  --registry "${RESULT_DIR}/candidate-registry.tsv" \
  --project-root "${PROJECT_ROOT}"

python3 analyzer/audit_baseline_feasibility.py \
  --project-root "${PROJECT_ROOT}" \
  --output-csv "${RESULT_DIR}/baseline-feasibility.csv" \
  --report "${RESULT_DIR}/baseline-feasibility-report.md" \
  --environment "${RESULT_DIR}/environment.json"

echo "C2 local readiness audit rebuilt."
