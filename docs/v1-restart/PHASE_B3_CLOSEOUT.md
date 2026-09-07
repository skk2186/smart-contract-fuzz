# Phase B3 Closeout: Main10 Preregistration and Runner Lock

## Repository state

- Current branch: develop
- Current HEAD: 28e610f2bacfb2d2304e2ce459771a9a02c0d806
- HEAD message: docs: gate V1 public benchmarks for native replay
- Initial Windows-side status showed mode-only changes on analyzer/run_native_replay_gate.py and scripts/run_v1_public_smoke_case.sh.
- Content diffs were empty; WSL Git reported the repository clean after restoring the executable bits. No reset, checkout, clean, branch switch, commit, or push was used.
- Runner index mode: 100755
- Runner filesystem mode in Ubuntu: 755

## B3 scope audit

- Runner modified: yes. Changes are limited to main10 allowlist, preregistered run-ID checks, fixed B4 output root, safe preflight/dry-run modes, manifest/provenance records, and guards.
- Preregistration generator added: yes, analyzer/build_main10_preregistration.py.
- Echidna fuzzing run: no.
- 10-seed run: no.
- 30-seed run: no.
- B4 main10 execution: no.
- Slither or solc run for B3: no.
- results/ or frozen evidence modified: no.
- results/matched-random-v1/ modified or used: no.
- exercise2-access-control included in supported pooled scope: no; it remains conditional.
- PUB06/PUB07/PUB08 included: no; they remain excluded.
- New safe checks created only two fresh run directories below work/v1-restart/b4-public-supported-10seed-main/. They did not overwrite Phase 06A or B2 artifacts.

## B3 outputs

New:

- docs/v1-restart/PHASE_B3_MAIN10_PREREGISTRATION.md
- analyzer/build_main10_preregistration.py
- paper-ready/v1/main10_preregistration.tsv
- paper-ready/v1/main10_expected_runs.tsv
- docs/v1-restart/PHASE_B3_CLOSEOUT.md

Updated:

- paper-ready/v1/public_benchmark_registry.tsv
- paper-ready/v1/evidence_index.tsv

The preregistration generator read public_benchmark_registry.tsv, native_replay_gate.tsv,
configs/public-c1-original.yaml, and configs/public-c1-harness.yaml. Its --check mode
does not write files; its --write mode writes only the two main10 preregistration TSVs.

## Locked B4 scope

- Supported benchmark count: 4
- Benchmarks: echidna-flags, echidna-multi, smartbugs-multifunc, smartbugs-onefunc
- Methods: Original, Full-K1, Full-K5
- Seeds: 1 through 10
- main10_preregistration.tsv: 12 data rows
- main10_expected_runs.tsv: 120 data rows
- Expected total runs: 120
- Output root: work/v1-restart/b4-public-supported-10seed-main/<run_id>/
used b3-main10-* safe-check IDs and
- Config inheritance: public-c1-original.yaml for Original; public-c1-harness.yaml for Full-K1/Full-K5; testLimit 100000, timeout 30s, workers 1, stopOnFail true, Original seqLen 4, Harness seqLen 1, no corpusDir.
- main-table candidate: after_successful_b4_summary only

The 120 rows contain only PUB01-PUB04. There is no exercise2-access-control,
PUB06, PUB07, PUB08, or matched-random-v1 row.

## Safe-mode verification

The following checks passed:

- python3 analyzer/build_main10_preregistration.py --help
- python3 analyzer/build_main10_preregistration.py --check
- python3 analyzer/build_main10_preregistration.py --write
- bash -n scripts/run_v1_public_smoke_case.sh
- git diff --check
- main10-dry-run for b3-main10-dry-run-smartbugs-onefunc-full-k1-s1
- main10-preflight for b3-main10-preflight-smartbugs-multifunc-original-s1

Both safe checks recorded manifest.tsv, command.txt, environment.txt, raw/,
parsed/, summary/, status/, and status/checksums.sha256. Their environment records
state that Echidna, Slither, and solc were skipped. The reserved main10 mode was
not invoked.

## B4 entry decision

B3 is complete and permits proceeding to B4 only after researcher review of this
document, the preregistration tables, the B2 gate, and the two safe-check run
directories. This is not a B4 result and is not an automatic authorization to
start all 120 runs.

Before B4, run:

~~~text
python3 analyzer/build_main10_preregistration.py --check
bash -n scripts/run_v1_public_smoke_case.sh
git diff --check
git status --short
~~~

After the researcher approves the checks, a future B4 run may use the exact
preregistered command shape:

~~~text
bash scripts/run_v1_public_smoke_case.sh --mode main10 --run-id b4-echidna-flags-original-s1 --benchmark echidna-flags --method Original --seed 1
~~~

That command was not run in B3. B4 must preserve all falsified/budget/status
rules, retain startup_error/unknown_error/incomplete/parser mismatch states,
and generate its summary from the 120 isolated run directories.

## Blockers and limitations

- No B3 blocker remains for the preregistration deliverables.
- Manual researcher review is still required before B4.
- B2 status remains static_gate_only; it is not native replay_pass.
- The Original multi-transaction and Harness single-wrapper caller, atomicity,
  rollback, and Total calls caveats remain in force.
- B4 results may be considered for a public-benchmark main table only after
  complete execution, parser/status reconciliation, checksum review, and a
  fixed successful summary.
