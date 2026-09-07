# Phase B4 Closeout: V1 Public Supported 10-Seed Main Run

## Repository and execution state

- Branch: develop.
- HEAD: 2764c5c00354d411d07520f91e966b463e225f4d.
- Initial WSL Git status: clean.
- Runner index mode: 100755.
- Runner filesystem mode in WSL: 755.
- Runner mode: main10 only.
- Runner method version: Full-v1.0.1-compat.
- Echidna fuzzing: yes, for all 120 main runs.
- Slither/solc preprocessing: yes, as recorded in each environment.txt.
- 10-seed run: yes, seeds 1-10 only.
- 30-seed run: no.
- results/ or frozen evidence modified: no.
- results/matched-random-v1 modified or used: no.
- exercise2-access-control/PUB05 included: no; it remains conditional.
- PUB06/PUB07/PUB08 included: no; they remain excluded.
- New benchmark added: no.
- Analyzer method logic changed for B4: no.
- Automatic commit or push: no.

## Scope and counts

- Expected runs: 120.
- Actual B4 run directories: 120.
- Benchmarks: echidna-flags, echidna-multi, smartbugs-multifunc, smartbugs-onefunc.
- Methods: Original, Full-K1, Full-K5.
- Seeds: 1-10.
- Complete artifact sets: 120/120.
- Checksum pass: 120/120.
- Parser/status mismatches: 0.
- startup_error: 0.
- unknown_error: 0.
- incomplete: 0.
- falsified: 118.
- budget_exhausted: 2.
- Other status classes: 0.

The B4 root also contains four earlier b3-main10 safe-check directories. They
were not expected B4 runs and were excluded from the 120-run summary.

## Result interpretation

The two budget_exhausted runs are:
- b4-echidna-multi-original-s1
- b4-echidna-multi-full-k5-s7

budget_exhausted means no observed counterexample within the declared budget.
It is not a property passed result and not a safety proof. Harness results are
reported under the wrapper execution model; no Original/Harness equivalence or
Total calls speedup claim is made.

## Paper and next-stage decision

- C-stage paper result organization: allowed conditionally after manual review.
- B4 repair required: no.
- Additional benchmark required to close B4: no.
- Broader benchmark, conditional exercise2 replay, or external competitor
  comparison: separate future experiment.
- The raw work directory remains untracked and must not be committed.

## Files produced for review

- docs/v1-restart/PHASE_B4_MAIN10_RUN.md
- docs/v1-restart/PHASE_B4_CLOSEOUT.md
- analyzer/summarize_main10_results.py
- paper-ready/v1/main10_results_by_run.tsv
- paper-ready/v1/main10_results_summary.tsv
- paper-ready/v1/main10_results_summary.md

The evidence index was extended with E20_PHASE_B4_MAIN10_RUN,
E21_MAIN10_RESULTS_BY_RUN, and E22_MAIN10_RESULTS_SUMMARY. No results/ file
was changed.
