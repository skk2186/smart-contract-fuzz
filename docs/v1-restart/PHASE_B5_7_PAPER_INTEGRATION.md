# Phase B5-7: Paper Integration

## Stage status

**PASS — paper integration materials complete.** The work integrates the previous adapted real-source evidence into a cautious conference-paper narrative. It does not claim a large-scale real-world evaluation or ecosystem-wide superiority.

- Stage: B5-7 Paper Integration
- Starting branch: develop
- Starting HEAD: f9f1ea47dacac7159723c3a981d4b480bf9696bd
- Worktree at start: clean in the Ubuntu-20.04 workspace.
- New experiments: **NO**.
- New Echidna formal fuzzing: **NO**.
- B5-5R rows rerun: **NO**.
- Historical evidence modified: **NO**.
- B5-4 preregistration, B5-5 blocked artifact, B5-5R raw result TSV, and B5-6 analysis inputs: **NOT MODIFIED**.
- exercise2 executed or included in the supported pool: **NO**.

## Inputs

1. docs/v1-restart/PHASE_B5_6_REAL_SOURCE_ANALYSIS.md
2. paper-ready/v1/b5/b5_6_real_source_analysis_summary.md
3. paper-ready/v1/b5/b5_6_candidate_method_matrix.tsv
4. paper-ready/v1/b5/b5_6_status_breakdown.tsv
5. paper-ready/v1/b5/b5_6_usable_subset.tsv
6. paper-ready/v1/b5/b5_6_excluded_engineering_rows.tsv
7. paper-ready/v1/b5/b5_6_paper_claims.md
8. paper-ready/v1/b5/b5_6_decision.md

## B5-6 result summary carried into the paper

- B5-5R result records: **120/120**.
- Usable or descriptive subset rows: **80**.
- Excluded engineering rows: **40**, all SmartBugs Full-K1/Full-K5 compile_error outcomes.
- Comparable Echidna-origin rows: **60**, comprising 59 falsified and 1 right-censored row.
- SmartBugs Original-only falsified rows: **20**.
- Candidate count: **4**, so the data cannot be described as a large-scale real-contract evaluation.
- Status totals: 79 falsified, 1 budget_exhausted, and 40 compile_error.
- budget_exhausted remains right-censored. It is not a safety or pass result.
- All real-source statements are labeled adapted real-source evidence.
- exercise2 was not executed.

## Integration strategy

The paper should present the contribution as property-oriented transaction-sequence generation. The method combines property-relevant state-dependency filtering, require-condition and state-value matching, bounded repetition, and top-K Harness construction. Controlled evidence carries the primary mechanism argument because it isolates the intended obstacles and reports repeatable outcomes under known conditions.

The adapted real-source material is a supplementary external-validity check. It asks whether the generated execution paths remain applicable to a small set of adapted real-source tasks. It is not pooled with controlled evidence, and it is not used to claim broad real-world superiority.

## Main experiment and supplementary experiment division

- Main experiment: controlled benchmarks and their component-specific evidence. These results evaluate whether the proposed path-generation mechanisms address the intended obstacles.
- Supplementary real-source experiment: four preregistered adapted candidates and 120 runs. The two Echidna-origin candidates form the only full Original/Full-K1/Full-K5 comparable set. SmartBugs Original is descriptive-only, while its 40 Harness compile_error rows are engineering limitations excluded from comparative outcomes.
- Cross-cutting interpretation: calls-to-failure and sequence-length are descriptive trace-complexity measures on falsified rows. Total calls is not a speedup measure, and Original and Harness are not treated as semantically equivalent.

## Recommended next step

Decision: GO_TO_C7_DRAFT_INTEGRATION

The evidence is sufficiently organized for a cautious paper draft. The draft should preserve the small adapted candidate pool, the 40 excluded compile_error rows, right-censoring language, and the execution-model distinction.
