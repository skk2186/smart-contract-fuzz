#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULT_ROOT="${PROJECT_ROOT}/results/v2/regression"

cd "$PROJECT_ROOT"

if [[ -z "${CONDA_PREFIX:-}" ]]; then
    echo "Activate the contract-fuzz environment first." >&2
    exit 1
fi

for required_command in python slither solc echidna
do
    if ! command -v "$required_command" >/dev/null 2>&1
    then
        echo "Missing required command: $required_command" >&2
        exit 1
    fi
done

mkdir -p "$RESULT_ROOT"

prepare_case() {
    local case_name="$1"
    local compiler="$2"
    local source_file="$3"
    local contract_name="$4"
    local candidate_file="$5"
    local property_name="${6:-}"
    local predicate_file="${RESULT_ROOT}/${case_name}-predicate.json"
    local ranked_file="${RESULT_ROOT}/${case_name}-ranked.json"

    echo "Preparing V2 ranking regression: ${case_name}"

    SOLC_VERSION="$compiler" python \
      analyzer/v2/extract_property_predicate.py \
      "$source_file" \
      --contract "$contract_name" \
      --output "$predicate_file"

    if [[ -n "$property_name" ]]; then
        python analyzer/v2/rank_violation_paths.py \
          "$candidate_file" \
          "$predicate_file" \
          --contract "$contract_name" \
          --property "$property_name" \
          --output "$ranked_file"
    else
        python analyzer/v2/rank_violation_paths.py \
          "$candidate_file" \
          "$predicate_file" \
          --contract "$contract_name" \
          --output "$ranked_file"
    fi
}

prepare_case \
  noisy-four-step 0.8.20 \
  contracts/benchmarks/NoisyFourStepExample.sol \
  NoisyFourStepExample \
  results/formal/preparation/noisy-four-step/full-sequences.json

prepare_case \
  reset-example 0.8.20 \
  contracts/benchmarks/ResetExample.sol \
  ResetExample \
  results/formal/preparation/reset-example/full-sequences.json

prepare_case \
  branch-value 0.8.20 \
  contracts/benchmarks/BranchValueExample.sol \
  BranchValueExample \
  results/formal/preparation/branch-value/full-sequences.json

prepare_case \
  repeated-call 0.8.20 \
  contracts/benchmarks/RepeatedCallExample.sol \
  RepeatedCallExample \
  results/formal/preparation/repeated-call/full-sequences.json

prepare_case \
  alternative-path 0.8.20 \
  contracts/benchmarks/AlternativePathExample.sol \
  AlternativePathExample \
  results/formal-b2/preparation/alternative-path/full-sequences.json

prepare_case \
  multi-property-a 0.8.20 \
  contracts/benchmarks/MultiPropertyExample.sol \
  MultiPropertyExample \
  results/formal-b2/preparation/multi-property/full-sequences.json \
  "echidna_value_a_safe()"

prepare_case \
  multi-property-b 0.8.20 \
  contracts/benchmarks/MultiPropertyExample.sol \
  MultiPropertyExample \
  results/formal-b2/preparation/multi-property/full-sequences.json \
  "echidna_value_b_safe()"

prepare_case \
  echidna-multi 0.8.20 \
  contracts/public-benchmarks/raw/echidna/multi.sol \
  C \
  results/public-benchmarks/c1/preparation/echidna-multi/full.json

prepare_case \
  echidna-flags 0.8.20 \
  contracts/public-benchmarks/adapted/EchidnaFlagsTarget.sol \
  PublicEchidnaFlagsTarget \
  results/public-benchmarks/c1/preparation/echidna-flags/full.json

prepare_case \
  exercise2-access-control 0.8.20 \
  contracts/public-benchmarks/raw/exercise2/solution.sol \
  TestToken \
  results/public-benchmarks/c1/preparation/exercise2-access-control/full.json

prepare_case \
  smartbugs-multifunc 0.4.25 \
  contracts/public-benchmarks/adapted/SmartBugsMultiFuncEchidna.sol \
  SmartBugsMultiFuncEchidna \
  results/public-benchmarks/c1/preparation/smartbugs-multifunc/full.json

prepare_case \
  smartbugs-onefunc 0.4.25 \
  contracts/public-benchmarks/adapted/SmartBugsOneFuncEchidna.sol \
  SmartBugsOneFuncEchidna \
  results/public-benchmarks/c1/preparation/smartbugs-onefunc/full.json

python analyzer/check_v2_ranking_regression.py \
  --result-root "$RESULT_ROOT"

echo "V2 ranking regression preparation completed."
