#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
RESULT_DIR="${PROJECT_ROOT}/results/semantic-applicability/v1"

cd "${PROJECT_ROOT}"

export PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/v1_semantics_pycache"

python3 -m py_compile \
  analyzer/audit_harness_semantics.py \
  analyzer/tests/test_audit_harness_semantics.py

python3 -m unittest \
  analyzer.tests.test_audit_harness_semantics -v

python3 analyzer/audit_harness_semantics.py \
  --manifest "${RESULT_DIR}/targets.tsv" \
  --output-csv "${RESULT_DIR}/applicability.csv" \
  --report "${RESULT_DIR}/static-audit-report.md" \
  --project-root "${PROJECT_ROOT}"

echo "Semantic applicability static audit rebuilt."
