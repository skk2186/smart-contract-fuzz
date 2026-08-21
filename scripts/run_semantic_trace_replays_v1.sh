#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
RESULT_DIR="${PROJECT_ROOT}/results/semantic-applicability/v1/trace-replays"
SOLC_ARTIFACT_ROOT="${SOLC_ARTIFACT_ROOT:-${HOME}/.solc-select/artifacts}"

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

run_replay() {
  local profile="$1"
  local source="$2"
  local contract="$3"
  local compiler_version="$4"
  local compiler
  compiler="${SOLC_ARTIFACT_ROOT}/solc-${compiler_version}/solc-${compiler_version}"

  if [[ ! -x "${compiler}" ]]; then
    echo "Missing local compiler: ${compiler}" >&2
    return 1
  fi

  "${compiler}" \
    --allow-paths "${PROJECT_ROOT}/contracts" \
    --bin "${source}" \
    > "${RESULT_DIR}/${profile}-compile.log" \
    2> "${RESULT_DIR}/${profile}-compile.stderr.log"

  "${ECHIDNA_COMMAND[@]}" "${source}" \
    --contract "${contract}" \
    --config configs/semantic-trace-replay-v1.yaml \
    --seed 1 \
    --disable-slither \
    --disable-onchain-sources \
    --crytic-args "--solc=${compiler}" \
    > "${RESULT_DIR}/${profile}-echidna.log" \
    2> "${RESULT_DIR}/${profile}-echidna.stderr.log"

  python3 analyzer/validate_semantic_differential.py \
    --log "${RESULT_DIR}/${profile}-echidna.log" \
    --output "${RESULT_DIR}/${profile}-validation.json" \
    --profile "${profile}"
}

run_replay \
  formal-replay \
  contracts/semantic-fixtures/FormalTraceReplay.sol \
  FormalTraceReplay \
  0.8.20

run_replay \
  public-v8-replay \
  contracts/semantic-fixtures/PublicTraceReplayV8.sol \
  PublicTraceReplayV8 \
  0.8.20

run_replay \
  public-v4-replay \
  contracts/semantic-fixtures/PublicTraceReplayV4.sol \
  PublicTraceReplayV4 \
  0.4.25

python3 analyzer/summarize_semantic_replays.py \
  --input-dir "${RESULT_DIR}" \
  --output-csv "${RESULT_DIR}/trace-replay-summary.csv" \
  --report "${RESULT_DIR}/differential-report.md"

echo "All semantic trace replays completed."
