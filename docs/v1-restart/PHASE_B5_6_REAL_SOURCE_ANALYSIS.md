# Phase B5-6: Real-Source Result Analysis

## Stage status

**PASS - analysis complete.** This report presents **adapted real-source evidence** from the preserved B5-5R 120-row result table. It does not broaden the evidence to ecosystem-wide superiority.

- Stage: B5-6 Real-Source Result Analysis
- Starting branch: develop
- Starting HEAD: 8ee3301f2e747d122796089db166ed41435c044a
- Worktree at start: clean in the Ubuntu-20.04 workspace.
- Analysis date: 2026-09-11
- New formal fuzzing run: **NO**.
- Echidna/Slither/solc rerun: **NO**.
- Historical evidence modified: **NO**.
- B5-4 frozen preregistration modified: **NO**.
- B5-5 blocked artifact modified: **NO**.
- B5-5R raw result TSV modified: **NO**.
- exercise2 executed or included: **NO**.

## Inputs

- paper-ready/v1/b5/b5_5r_supported_real_source_results.tsv
- paper-ready/v1/b5/b5_5r_supported_real_source_summary.md
- paper-ready/v1/b5/b5_5r_decision.md
- paper-ready/v1/b5/b5_4_expected_real_source_runs.tsv
- paper-ready/v1/b5/b5_5_supported_real_source_results.tsv

## Input audit

- B5-5R result rows: **120/120**.
- B5-4 frozen registry rows: **120/120**.
- Executed rows with non-empty status: **120/120**.
- Preserved result rows with complete registry join: **120/120**.
- artifact_complete=true: **120**.
- checksum_pass=pass: **120**.
- paper_usable=true: **80**.
- paper_usable=false: **40**.
- B5-5 blocked result remains present: **YES**.
- First B5-5R row retries b5-4-rs-b5-rs-echidna-flags-original-s1, the first B5-5 tool_error run: **YES**.
- Supported candidates: **b5-rs-echidna-flags, b5-rs-echidna-multi, b5-rs-smartbugs-multifunc, b5-rs-smartbugs-onefunc**.
- exercise2 present in B5-5R or registry: **NO**.

Input SHA-256 values:

- b5_5r_supported_real_source_results.tsv: 09740dba8e550dc2b5a1b069bd154c6c5bf5627b99bd992d89bbfcbc5547b6de
- b5_5r_supported_real_source_summary.md: f62f5c227925bfdff35c4c7f1fcb3743d67f8bde260e683ec51c1bcfcf01b7ec
- b5_5r_decision.md: a44d84b87240bea93764284ad7824a3fa083ba9a84a87266925791c88ec0eabd
- b5_4_expected_real_source_runs.tsv: 65cbc9c391f2356a5bad2bcc30a46a6bbd7f64d3fae92f1f0865c4ecc8253dbf
- b5_5_supported_real_source_results.tsv: caff0d5253675cc4082c3a9239492060526cf8a12fad97ff0aca512bf6350ce9


## Status distribution

| Status | Rows | Share | Interpretation |
| --- | --- | --- | --- |
| falsified | 79 | 0.6583 | Observed property violation under the declared execution model. |
| budget_exhausted | 1 | 0.0083 | Right-censored: no counterexample observed within budget; not safe or passed. |
| compile_error | 40 | 0.3333 | Engineering limitation; excluded from comparative outcomes. |
| tool_error | 0 | 0.0000 | Tool/runner error; not observed in B5-5R. |
| timeout | 0 | 0.0000 | Timeout; not observed in B5-5R. |
| parser_error | 0 | 0.0000 | Parser error; not observed in B5-5R. |
| incomplete | 0 | 0.0000 | Incomplete record; not observed in B5-5R. |
| startup_error | 0 | 0.0000 | Startup error; not observed in B5-5R. |
| unknown_error | 0 | 0.0000 | Unknown error; not observed in B5-5R. |

budget_exhausted is right-censored. It means no counterexample was observed within the declared budget. It is not a property pass, safety result, or evidence that no vulnerability exists.

## Candidate-level aggregation

All discovery metrics below use status=falsified rows only. They describe observed discovery traces under the declared execution model and are not speedup measures.

| Candidate | Rows | Falsified | Budget | Compile error | Usable | Engineering rows | Median calls | Mean calls | Median seq. | Mean seq. | Median fuzz s | Mean fuzz s | Median wall s | Mean wall s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b5-rs-echidna-flags | 30 | 30 | 0 | 0 | 30 | 0 | 1 | 2.3 | 1 | 2.3 | 2.48 | 2.4 | 2.522 | 2.434 |
| b5-rs-echidna-multi | 30 | 29 | 1 | 0 | 30 | 0 | 1 | 2.655 | 1 | 2.655 | 4.85 | 5.786 | 4.88 | 5.814 |
| b5-rs-smartbugs-multifunc | 30 | 10 | 0 | 20 | 10 | 20 | 3 | 3.4 | 3 | 3.4 | 1.42 | 1.436 | 1.469 | 1.479 |
| b5-rs-smartbugs-onefunc | 30 | 10 | 0 | 20 | 10 | 20 | 2 | 2.3 | 2 | 2.3 | 1.495 | 1.502 | 1.519 | 1.524 |

Machine-readable table: paper-ready/v1/b5/b5_6_candidate_aggregate.tsv.

## Method-level aggregation

| Method | Rows | Falsified | Budget | Compile error | Usable | Median calls | Mean calls | Median seq. | Mean seq. | Median fuzz s | Mean fuzz s | Median wall s | Mean wall s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Original | 40 | 40 | 0 | 0 | 40 | 4.5 | 4.1 | 4.5 | 4.1 | 1.855 | 2.3 | 1.895 | 2.331 |
| Full-K1 | 40 | 20 | 0 | 20 | 20 | 1 | 1 | 1 | 1 | 3.035 | 4.36 | 3.075 | 4.393 |
| Full-K5 | 40 | 19 | 1 | 20 | 20 | 1 | 1 | 1 | 1 | 2.91 | 4.736 | 2.924 | 4.767 |

Machine-readable table: paper-ready/v1/b5/b5_6_method_aggregate.tsv.

## Candidate x method matrix

status_summary lists all nonzero statuses for each cell. Discovery metrics use falsified rows only.

| Candidate | Method | Rows | Status summary | Falsified | Budget | Compile error | Median calls | Mean calls | Median seq. | Mean seq. | Median wall s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b5-rs-echidna-flags | Original | 10 | falsified=10 | 10 | 0 | 0 | 5 | 4.9 | 5 | 4.9 | 2.522 |
| b5-rs-echidna-flags | Full-K1 | 10 | falsified=10 | 10 | 0 | 0 | 1 | 1 | 1 | 1 | 2.522 |
| b5-rs-echidna-flags | Full-K5 | 10 | falsified=10 | 10 | 0 | 0 | 1 | 1 | 1 | 1 | 2.472 |
| b5-rs-echidna-multi | Original | 10 | falsified=10 | 10 | 0 | 0 | 6 | 5.8 | 6 | 5.8 | 2.773 |
| b5-rs-echidna-multi | Full-K1 | 10 | falsified=10 | 10 | 0 | 0 | 1 | 1 | 1 | 1 | 6.16 |
| b5-rs-echidna-multi | Full-K5 | 10 | falsified=9;budget_exhausted=1 | 9 | 1 | 0 | 1 | 1 | 1 | 1 | 6.636 |
| b5-rs-smartbugs-multifunc | Original | 10 | falsified=10 | 10 | 0 | 0 | 3 | 3.4 | 3 | 3.4 | 1.469 |
| b5-rs-smartbugs-multifunc | Full-K1 | 10 | compile_error=10 | 0 | 0 | 10 | n.a. | n.a. | n.a. | n.a. | n.a. |
| b5-rs-smartbugs-multifunc | Full-K5 | 10 | compile_error=10 | 0 | 0 | 10 | n.a. | n.a. | n.a. | n.a. | n.a. |
| b5-rs-smartbugs-onefunc | Original | 10 | falsified=10 | 10 | 0 | 0 | 2 | 2.3 | 2 | 2.3 | 1.519 |
| b5-rs-smartbugs-onefunc | Full-K1 | 10 | compile_error=10 | 0 | 0 | 10 | n.a. | n.a. | n.a. | n.a. | n.a. |
| b5-rs-smartbugs-onefunc | Full-K5 | 10 | compile_error=10 | 0 | 0 | 10 | n.a. | n.a. | n.a. | n.a. | n.a. |

Machine-readable table: paper-ready/v1/b5/b5_6_candidate_method_matrix.tsv.

## Comparable subsets

### A. Full comparable real-source subset

The candidate-level comparable set is b5-rs-echidna-flags and b5-rs-echidna-multi. Each has 30 rows with Original, Full-K1, and Full-K5 represented and no compile_error cell. Together they contain **60 rows**, of which **59 are falsified** and **1 are right-censored**. Method-level comparison is restricted to these candidates, identical adapted properties, and the same declared execution model. The right-censored row is retained for completeness but excluded from calls-to-failure and sequence-length summaries.

### B. Original-only SmartBugs subset

The SmartBugs Original-only descriptive subset contains **20 falsified rows**. These rows show that the adapted SmartBugs targets can execute under Original and expose an observed property violation. They are not used for Original-versus-Harness performance comparisons.

### C. Engineering limitation subset

The SmartBugs Full-K1/Full-K5 Harness subset contains **40 compile_error rows**. These are preserved engineering outcomes. They are excluded from usable comparative outcomes, are not counted as falsified, and are not interpreted as a low method discovery rate. The result indicates an engineering limitation in the Harness generation/import path under Solidity 0.4.25.

Machine-readable subset files:

- paper-ready/v1/b5/b5_6_usable_subset.tsv: 80 retained rows with subset_label values comparable_echidna_origin, smartbugs_original_only, or right_censored.
- paper-ready/v1/b5/b5_6_excluded_engineering_rows.tsv: 40 excluded SmartBugs Harness compile_error rows.

## Paper-usable conclusions and boundaries

The claims and limitations are in paper-ready/v1/b5/b5_6_paper_claims.md. Supported conclusions:

1. On the two Echidna-origin adapted real-source candidates, Full-K1 and Full-K5 retained the ability to produce observed property violations under the adapted real-source execution model.
2. For falsified rows, calls-to-failure and sequence-length are descriptive measures of observed discovery-trace complexity.
3. SmartBugs Original rows demonstrate that the adapted SmartBugs targets can execute and expose observed property violations under Original.
4. The 40 SmartBugs Harness compile_error rows expose a cross-version Harness generation/import limitation under Solidity 0.4.25 and belong in threats to validity.

The evidence does not establish ecosystem-wide superiority, semantic equivalence between Original and Harness, a speedup from total calls, or safety for budget_exhausted rows.

## Next-step recommendation

Decision: GO_TO_B5_7_PAPER_INTEGRATION

B5-6 is complete and supports cautious paper strengthening. Later integration must preserve the adapted real-source label, keep the 40 compile_error rows excluded from comparative outcomes, retain right-censoring language, and keep SmartBugs Original separate from Harness performance comparison.
