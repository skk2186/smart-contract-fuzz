# Phase B5-3 Real-Source Extension Screening

Date: 2026-09-11
Starting branch: develop
Starting HEAD: 30d1558c897321899a8de059e9585be08ff98b58

## Scope and inspected inputs

This stage performed repository-only candidate screening, semantic review and conditional preregistration preparation. It did not run a formal experiment.

Inspected inputs included:

- docs/START_HERE.md
- docs/DIRECTORY_GUIDE.md
- AGENTS.md
- docs/V1_EXPERIMENT_WORKFLOW.md
- paper-ready/00_PROJECT_SUMMARY.md
- paper-ready/FREEZE_STATUS.md
- paper-ready/v1/d0/d0_decision.md
- paper-ready/v1/d0/b5_options.md
- paper-ready/v1/b5/b5_preregistration.md
- paper-ready/v1/b5/b5_final_decision.md
- paper-ready/v1/b5/b5_cvenue_sufficiency_review.md
- paper-ready/v1/b5/b5_real_source_extension_decision.md
- docs/v1-restart/PHASE_B5_2_FORMAL_MAIN_RUN.md
- paper-ready/v1/b5/b5_results_summary.tsv
- paper-ready/v1/b5/b5_claim_evidence_update.tsv
- paper-ready/v1/public_benchmark_registry.tsv
- docs/v1-restart/SEMANTIC_BOUNDARY_AUDIT.md
- results/public-benchmarks/c2-screening/candidate-registry.tsv
- results/public-benchmarks/c2-screening/source-pools.tsv
- results/public-benchmarks/sources.tsv
- results/public-benchmarks/c1/adaptations.md
- contracts/public-benchmarks/raw and adapted source files

## Network and execution record

- network used: NO
- external source downloaded: NO
- external source copied into the repository: NO
- Solidity compiler run: NO
- Slither run: NO
- Echidna run: NO
- B5-Min formal run: NO
- B5-4 formal run: NO

The source URLs in the registry and preregistration are canonical references assembled from the pinned repository/path records already present in the local screening registry. They were not fetched or revalidated online in this stage.

## Created files

- paper-ready/v1/b5/b5_real_source_candidate_registry.tsv
- paper-ready/v1/b5/b5_real_source_screening_report.md
- paper-ready/v1/b5/b5_real_source_adaptation_plan.md
- paper-ready/v1/b5/b5_real_source_preregistration.md
- paper-ready/v1/b5/b5_real_source_decision.md
- docs/v1-restart/PHASE_B5_3_REAL_SOURCE_EXTENSION_SCREENING.md

No adapted source directory was created because the canonical source/license package is incomplete.

## Frozen-boundary audit

- B4 results: unchanged
- B5-Min/B5-2 results: unchanged
- results/frozen: unchanged
- results/matched-random-v1: unchanged
- controlled/custom source: unchanged
- candidate source code: unchanged
- pre-existing dirty files: left untouched
- commit or push: none

## Candidate counts

- accepted_for_preregistration: 0
- conditional_requires_adaptation: 1
- rejected: 3
- needs_manual_source: 4

The conditional candidate is exercise2-access-control. It cannot enter a supported pooled result because its caller and mapping semantics differ between Original and the current Harness model.

## Final decision and next recommendation

Final decision: NEED_MANUAL_CANDIDATE_SOURCE

B5-Min can proceed to C7 with its controlled/custom limitation. Before any B5-4 execution, manually provide canonical source/license packets, freeze hashes and adaptation diffs, complete the caller-controlled replay for exercise2, and have the researcher review the final inclusion rule. Do not use PHS outcomes to choose or discard candidates.

## Reviewer-facing conclusion

The screen found a defensible conditional extension candidate, but not a ready supported real-source pool. This is a provenance and semantic gate result, not a negative result about PHS. The proper next step is targeted manual source acquisition and replay preparation; no seed expansion, new controlled scenario, or formal fuzzing was authorized here.
