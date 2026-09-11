# Phase B5-3R Real-Source Provenance and Adaptation Gate

Date: 2026-09-11
Starting branch: develop
Starting HEAD: 364c1dce1c85c8d1ec8d884c99ada25744ae165e
Parent B5-2 commit: 30d1558c897321899a8de059e9585be08ff98b58

## Network and acquisition

- network used: YES, direct pinned raw.githubusercontent.com retrieval
- source acquisition failures: NONE
- B5-4 formal fuzzing: NOT RUN
- 10-seed experiment: NOT RUN
- B5-Min controlled formal: NOT RUN
- Solidity compiler, Slither and Echidna: NOT RUN

Downloaded and archived source files:

- crytic/echidna @ 4454f3a: flags.sol and multi.sol;
- smartbugs/smartbugs-curated @ 230e649: integer_overflow_multitx_multifunc_feasible.sol and integer_overflow_multitx_onefunc_feasible.sol;
- crytic/building-secure-contracts @ 2de122e: solution.sol and token.sol.

Downloaded and archived license files:

- crytic/echidna @ 4454f3a: LICENSE;
- smartbugs/smartbugs-curated @ 230e649: LICENSE;
- crytic/building-secure-contracts @ 2de122e: LICENSE.

## Candidates processed

- b5-rs-echidna-flags
- b5-rs-echidna-multi
- b5-rs-smartbugs-multifunc
- b5-rs-smartbugs-onefunc
- b5-rs-exercise2-access-control

## Gate summary

- canonical source archived: 5/5
- license evidence confirmed: 5/5
- adapted candidate packet present: 5/5
- source/adapted hashes recorded: 5/5
- supported real-source candidates ready for B5-4 preregistration: 4
- conditional appendix candidates: 1
- unresolved source/license candidates: 0
- caller gate: exercise2 pending; other four have no caller-sensitive target-path signal but still require task replay
- property review: SmartBugs candidates pending explicit preregistration review

## Created files

For each candidate, the following were created:

- original/ source archive;
- original/LICENSE;
- adapted/ candidate copy or existing local adaptation;
- README_PROVENANCE.md;
- LICENSE_EVIDENCE.md;
- ADAPTATION_DIFF_NOTES.md;
- checksums.tsv;
- GATE_DECISION.md.

Additional files:

- paper-ready/v1/b5/b5_real_source_provenance_registry.tsv
- paper-ready/v1/b5/b5_exercise2_caller_replay_gate_plan.md
- paper-ready/v1/b5/b5_3r_real_source_gate_decision.md
- docs/v1-restart/PHASE_B5_3R_REAL_SOURCE_PROVENANCE_GATE.md

## Adapted-source status

No business-logic rewrite was made in B5-3R. Existing local adaptations were copied and disclosed. Echidna multi and exercise2 use byte-identical candidate copies. SmartBugs files retain the existing added property and compiler rationale. All adaptation differences are recorded before any B5-4 preregistration.

## Frozen-boundary audit

- results/frozen: unchanged
- results/matched-random-v1: unchanged
- B4 results: unchanged
- B5-Min/B5-2 results: unchanged
- paper-ready/v1/b5/b5_results_summary.tsv: unchanged
- controlled/custom sources: unchanged
- formal result TSV: not created
- commit/push: none

## B5-4 authorization

Final decision: GO_TO_B5_4_PREREGISTRATION

Only preregistration preparation is authorized. No B5-4 formal fuzzing, no 10-seed experiment and no B5-Min rerun is authorized by this closeout.

## Next phase

Prepare and review the B5-4 preregistration for the four provenance-ready candidates as a supported-real-source stratum. Keep exercise2 in a separate conditional appendix stratum until the caller/replay gate passes. Preserve the distinction between public/adapted evidence and controlled/custom evidence.
