#!/usr/bin/env bash
set -uo pipefail

ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd)"
REGISTRY="$ROOT/paper-ready/v1/b5/b5_expected_runs.tsv"
RUN_ROOT="$ROOT/work/v1-restart"

if [[ "${B5_MAIN_AUTHORIZED:-}" != "1" ]]; then
  echo "ERROR: B5_MAIN_AUTHORIZED=1 is required" >&2
  exit 2
fi
if [[ ! -f "$REGISTRY" ]]; then
  echo "ERROR: expected registry not found: $REGISTRY" >&2
  exit 2
fi

registry_rows="$(awk -F '\t' 'NR > 1 { count += 1; if (NF != 6) bad = 1; if ($1 in seen) dup = 1; seen[$1] = 1; if ($4 < 1 || $4 > 10) seed_bad = 1 } END { if (count != 120 || bad || dup || seed_bad) exit 1; print count }' "$REGISTRY")" || {
  echo "ERROR: registry must contain 120 unique rows with seeds 1..10" >&2
  exit 2
}
echo "registry_rows=$registry_rows"

collision="$(awk -F '\t' -v root="$RUN_ROOT" 'NR > 1 { path = root "/" $1; if ((system("[ -e \"" path "\" ] || [ -L \"" path "\" ]") == 0)) print $1 }' "$REGISTRY")"
if [[ -n "$collision" ]]; then
  echo "ERROR: pre-existing run-id collision(s):" >&2
  printf '%s\n' "$collision" >&2
  exit 3
fi

executed=0
failed=0
while IFS=$'\t' read -r run_id scenario method seed budget expected; do
  budget="${budget%$'\r'}"
  expected="${expected%$'\r'}"
  [[ -z "$run_id" ]] && continue
  if [[ "$expected" != "preregistered" ]]; then
    echo "ERROR: unexpected registry marker for $run_id: $expected" >&2
    exit 2
  fi
  if [[ "$budget" != "testLimit=100000;timeout=30s" ]]; then
    echo "ERROR: unexpected budget for $run_id: $budget" >&2
    exit 2
  fi
  budget_value="${budget#testLimit=}"
  budget_value="${budget_value%%;*}"
  echo "START $run_id scenario=$scenario method=$method seed=$seed"
  "$ROOT/scripts/run_b5_controlled.sh" \
    --scenario "$scenario" \
    --method "$method" \
    --seed "$seed" \
    --budget "$budget_value" \
    --run-id "$run_id" \
    --experiment-class formal
  rc=$?
  executed=$((executed + 1))
  if [[ "$rc" -ne 0 ]]; then
    failed=$((failed + 1))
    echo "RUN_EXIT $run_id rc=$rc"
  else
    echo "RUN_EXIT $run_id rc=0"
  fi
done < <(tail -n +2 "$REGISTRY")

echo "formal_runs_executed=$executed"
echo "runner_nonzero_exits=$failed"
[[ "$executed" -eq 120 ]]
