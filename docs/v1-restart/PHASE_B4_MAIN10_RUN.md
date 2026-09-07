# Phase B4: V1 Public Supported 10-Seed Main Run

## Purpose and boundary

B4 executes the B3 preregistered V1 public supported main run. The research
question is whether the fixed Original versus Full-K1 versus Full-K5 comparison
can produce a complete, classifiable, and auditable result set for the four
supported public tasks.

This phase ran only the 120 rows in the B3 expected-run table. It did not run
30 seeds, add benchmarks, modify the method logic, or pool conditional or
excluded tasks.

## B3 preregistration recheck

- Branch: develop.
- Commit: 2764c5c00354d411d07520f91e966b463e225f4d.
- Preregistration rows: 12 data rows.
- Expected runs: 120 data rows.
- Benchmarks: PUB01 echidna-flags; PUB02 echidna-multi; PUB03
  smartbugs-multifunc; PUB04 smartbugs-onefunc.
- Methods: Original, Full-K1, Full-K5.
- Seeds: 1 through 10 only.
- Configuration: configs/public-c1-original.yaml for Original and
  configs/public-c1-harness.yaml for Full-K1/Full-K5.
- Output root: work/v1-restart/b4-public-supported-10seed-main/.
- All expected rows were status=preregistered.
- exercise2-access-control/PUB05, PUB06, PUB07, PUB08, conditional tasks,
  excluded tasks, and matched-random-v1 were outside the expected table.

The preregistration checker reported: 4 benchmarks, 3 methods, 10 seeds, 120
expected runs.

## Execution

Each row was executed with the locked runner shape:

    bash scripts/run_v1_public_smoke_case.sh --mode main10 --run-id <run_id> --benchmark <benchmark_name> --method <method> --seed <seed>

The runner used the existing WSL contract-fuzz environment and recorded the
actual paths and versions in every environment.txt:

- Python 3.11.15
- Slither 0.11.5
- solc-select with 0.4.23, 0.4.25, and 0.8.20 available
- solc 0.8.20 or 0.4.25 according to the benchmark
- Echidna 2.3.2
- testLimit 100000, timeout 30s, workers 1, stopOnFail true
- method version Full-v1.0.1-compat
- Echidna, Slither, solc, and solc-select were invoked for the main runs

All 120 run directories are below the B4 work root. Four earlier B3 safe-check
directories also exist below that root, but have b3-main10 run IDs and were not
included in the B4 expected-run audit.

## Artifact and audit results

For each expected B4 run, the audit found manifest.tsv, command.txt,
environment.txt, raw/, parsed/, summary/, status/, status/status.env,
status/checksums.sha256, parsed/smoke.csv, summary/smoke.csv, and a raw
seed log.

- Complete expected run directories: 120/120.
- Raw logs: 120/120.
- Parsed smoke CSVs: 120/120.
- Summary smoke CSVs: 120/120.
- status.env: 120/120.
- Checksum files: 120/120; checksum verification passed 120/120.
- Parser/status mismatches: 0.
- startup_error: 0.
- unknown_error: 0.
- incomplete: 0.
- Results written under results/: 0.
- Runner mode records: MODE=main10 for 120/120.
- Seed 11-30 command entries: 0.
- Forbidden or conditional benchmark command entries: 0.

## Results

| Benchmark | Method | Runs | Falsified | Budget exhausted | Falsification rate |
|---|---|---:|---:|---:|---:|
| echidna-flags | Original | 10 | 10 | 0 | 1.000000 |
| echidna-flags | Full-K1 | 10 | 10 | 0 | 1.000000 |
| echidna-flags | Full-K5 | 10 | 10 | 0 | 1.000000 |
| echidna-multi | Original | 10 | 9 | 1 | 0.900000 |
| echidna-multi | Full-K1 | 10 | 10 | 0 | 1.000000 |
| echidna-multi | Full-K5 | 10 | 9 | 1 | 0.900000 |
| smartbugs-multifunc | Original | 10 | 10 | 0 | 1.000000 |
| smartbugs-multifunc | Full-K1 | 10 | 10 | 0 | 1.000000 |
| smartbugs-multifunc | Full-K5 | 10 | 10 | 0 | 1.000000 |
| smartbugs-onefunc | Original | 10 | 10 | 0 | 1.000000 |
| smartbugs-onefunc | Full-K1 | 10 | 10 | 0 | 1.000000 |
| smartbugs-onefunc | Full-K5 | 10 | 10 | 0 | 1.000000 |

Overall: 118 falsified and 2 budget_exhausted. The budget observations are
b4-echidna-multi-original-s1 and b4-echidna-multi-full-k5-s7. A
budget_exhausted run means no observed counterexample within the declared
budget; it is not a property pass or a contract-safety result.

## Claims supported

B4 supports a phase-scoped descriptive table for the four preregistered
supported public benchmarks, the three declared methods, and seeds 1-10. It
supports reporting the observed falsified and budget_exhausted counts with
their run-level provenance and audit status.

## Claims not supported

B4 does not establish that V1 is generally better than Echidna, SMARTIAN,
MuFuzz, or IR-Fuzz. It does not establish that four tasks represent the
real-contract ecosystem. Harness falsification is under the generated wrapper
execution model and does not prove equivalence with Original independent
multi-transaction execution. Original and Harness Total calls are not used as
equal-work speedup.

Conditional exercise2-access-control and excluded PUB06/PUB07/PUB08 remain
outside the supported pooled result.

## C-stage decision

The B4 result set may proceed to C-stage paper result organization
conditionally, after manual review of the run-level tables, raw logs, checksums,
and semantic caveats. No B4 repair is required, and no benchmark supplementation
is required for this phase. Any broader benchmark, conditional replay, or
competitor comparison is a separate preregistered experiment.
