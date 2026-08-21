#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
run_root="$repo_root/results/public-benchmarks/c2-screening/smartian-formal-20260806"
compiler="/home/skk/.solc-select/artifacts/solc-0.4.25/solc-0.4.25"
dotnet_root="$repo_root/.tools/dotnet"
smartian_dll="$repo_root/baselines/smartian/src/bin/Release/net8.0/Smartian.dll"
source_dir="$repo_root/contracts/public-benchmarks/adapted"

if [[ ! -x "$compiler" ]]; then
  echo "missing Solidity 0.4.25 compiler: $compiler" >&2
  exit 2
fi
if [[ ! -f "$smartian_dll" ]]; then
  echo "missing SMARTIAN assembly: $smartian_dll" >&2
  exit 2
fi
if [[ -e "$run_root" ]]; then
  echo "run root already exists; remove it only after preserving results: $run_root" >&2
  exit 2
fi

mkdir -p "$run_root/inputs/multi" "$run_root/inputs/one" \
  "$run_root/runs/multi" "$run_root/runs/one"

export DOTNET_ROOT="$dotnet_root"
export PATH="$DOTNET_ROOT:$PATH"
export DOTNET_CLI_HOME=/tmp/smartian-dotnet-home
export NUGET_PACKAGES=/tmp/smartian-nuget
mkdir -p "$DOTNET_CLI_HOME" "$NUGET_PACKAGES"

"$compiler" --bin --abi -o "$run_root/inputs/multi" \
  "$source_dir/SmartBugsMultiFuncEchidna.sol"
"$compiler" --bin --abi -o "$run_root/inputs/one" \
  "$source_dir/SmartBugsOneFuncEchidna.sol"

status_file="$run_root/run-status.tsv"
printf 'target\trun_id\texit_code\tduration_sec\tcompleted\ttestcase_files\tbug_files\tlog\toutput_dir\n' > "$status_file"

cat > "$run_root/manifest.txt" <<EOF
date=2026-08-06
smartian_commit=$(git -C "$repo_root/baselines/smartian" rev-parse HEAD)
dotnet_sdk=$("$dotnet_root/dotnet" --version)
solidity_compiler=$compiler
solidity_version=$("$compiler" --version | sed -n 's/^Version: //p')
smartian_dll=$smartian_dll
timelimit_sec=30
repeats_per_target=30
seed_control=SMARTIAN CLI exposes no seed option; run_id is recorded instead
success_definition=bug directory contains an IntegerBug (IB) artifact
EOF

for target in multi one; do
  if [[ "$target" == "multi" ]]; then
    stem="SmartBugsMultiFuncEchidna"
  else
    stem="SmartBugsOneFuncEchidna"
  fi
  bytecode="$run_root/inputs/$target/$stem.bin"
  abi="$run_root/inputs/$target/$stem.abi"
  for run_id in $(seq 1 30); do
    output_dir="$run_root/runs/$target/run-$run_id"
    log_file="$run_root/runs/$target/run-$run_id.log"
    mkdir -p "$output_dir"
    start=$(date +%s)
    set +e
    "$dotnet_root/dotnet" "$smartian_dll" fuzz \
      -p "$bytecode" -a "$abi" -t 30 -o "$output_dir" -v 0 \
      > "$log_file" 2>&1
    exit_code=$?
    set -e
    end=$(date +%s)
    completed=0
    if rg -q 'Done, clean up and exit' "$log_file"; then
      completed=1
    fi
    testcase_files=$(find "$output_dir/testcase" -type f 2>/dev/null | wc -l)
    bug_files=$(find "$output_dir/bug" -type f 2>/dev/null | wc -l)
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$target" "$run_id" "$exit_code" "$((end-start))" "$completed" \
      "$testcase_files" "$bug_files" "$log_file" "$output_dir" >> "$status_file"
    printf 'target=%s run_id=%s exit=%s duration_sec=%s completed=%s testcase_files=%s bug_files=%s\n' \
      "$target" "$run_id" "$exit_code" "$((end-start))" "$completed" \
      "$testcase_files" "$bug_files"
  done
done

python3 "$repo_root/analyzer/parse_smartian_formal_results.py" \
  --run-status "$status_file" \
  --output-csv "$run_root/summary.csv" \
  --output-json "$run_root/summary.json"
