#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
SOURCE="${PROJECT_ROOT}/contracts/semantic-fixtures/HarnessSemanticDifferential.sol"
CONFIG="${PROJECT_ROOT}/configs/semantic-differential-v1.yaml"
RESULT_DIR="${PROJECT_ROOT}/results/semantic-applicability/v1/differential"

if command -v crytic-compile >/dev/null 2>&1; then
  ECHIDNA_COMMAND=(echidna)
elif command -v conda >/dev/null 2>&1; then
  ECHIDNA_COMMAND=(
    conda run --no-capture-output -n contract-fuzz echidna
  )
else
  echo "crytic-compile is unavailable and conda cannot activate contract-fuzz." >&2
  exit 1
fi

mkdir -p "${RESULT_DIR}"
cd "${PROJECT_ROOT}"

solc --bin "${SOURCE}" \
  > "${RESULT_DIR}/compile.log" \
  2> "${RESULT_DIR}/compile.stderr.log"

"${ECHIDNA_COMMAND[@]}" "${SOURCE}" \
  --contract HarnessSemanticDifferential \
  --config "${CONFIG}" \
  --seed 1 \
  --disable-slither \
  --disable-onchain-sources \
  > "${RESULT_DIR}/echidna-seed-1.log" \
  2> "${RESULT_DIR}/echidna-seed-1.stderr.log"

python3 analyzer/validate_semantic_differential.py \
  --log "${RESULT_DIR}/echidna-seed-1.log" \
  --output "${RESULT_DIR}/validation.json" \
  --profile semantic-model

echo "Semantic differential regression completed."
