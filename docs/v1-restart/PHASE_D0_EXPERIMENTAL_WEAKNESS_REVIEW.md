# Phase D0: Experimental Weakness Review + B5 Decision

## Phase objective

D0 按现实 C 会 short/regular research paper 的标准复核 V1 实验体系：区分真正会导致 reviewer 拒稿的缺口与可通过定位/措辞化解的限制，并选择最小、可执行、以论文闭环为目标的 B5 路线。D0 不运行实验，不新增 benchmark 源码，不修改现有 benchmark，不修改 frozen/quarantined/legacy 结果，不执行 B4，也不继续 C7 正文润色。

## Repository state

- Repository: \\wsl.localhost\Ubuntu-20.04\home\skk\research\smart-contract-fuzz
- Branch: develop
- HEAD: 9e3c842b9cf7efeb9084b55996c1fdaa28b9ae79
- HEAD subject: docs: prepare V1 paper polish and citation integration
- Expected remote baseline: matched at HEAD.
- Pre-existing worktree entries: five files were already marked modified before D0 (analyzer/build_main10_preregistration.py, analyzer/run_native_replay_gate.py, docs/v1-restart/PHASE_B3_CLOSEOUT.md, docs/v1-restart/PHASE_B3_MAIN10_PREREGISTRATION.md, scripts/run_v1_public_smoke_case.sh). D0 did not edit, revert, stage, commit, or push them.

## Files inspected

### Mandatory repository guidance

- docs/START_HERE.md
- docs/DIRECTORY_GUIDE.md
- paper-ready/00_PROJECT_SUMMARY.md
- paper-ready/FREEZE_STATUS.md
- AGENTS.md
- docs/V1_EXPERIMENT_WORKFLOW.md

### Evidence and stage records

- docs/v1-restart/PAPER_EVIDENCE_LOCK.md
- docs/v1-restart/SEMANTIC_BOUNDARY_AUDIT.md
- docs/v1-restart/PHASE_B1_PUBLIC_EXPANSION_PREREGISTRATION.md
- docs/v1-restart/PHASE_B2_NATIVE_REPLAY_GATE.md
- docs/v1-restart/PHASE_B3_MAIN10_PREREGISTRATION.md
- docs/v1-restart/PHASE_B4_MAIN10_RUN.md
- docs/v1-restart/PHASE_B4_CLOSEOUT.md
- docs/v1-restart/PHASE_C1_PAPER_READY_CLOSEOUT.md
- docs/v1-restart/PHASE_C6_DRAFT_POLISH_PREP_CLOSEOUT.md
- paper-ready/v1/evidence_index.tsv
- paper-ready/v1/public_benchmark_registry.tsv
- paper-ready/v1/main10_preregistration.tsv
- paper-ready/v1/main10_expected_runs.tsv
- paper-ready/v1/main10_results_by_run.tsv
- paper-ready/v1/main10_results_summary.tsv
- paper-ready/v1/c1/rq_evidence_map.tsv
- paper-ready/v1/c1/claim_evidence_matrix.tsv
- paper-ready/v1/c1/evaluation_tables.md
- paper-ready/v1/c3/revised_full_draft_zh.md
- paper-ready/v1/c3/revised_evaluation.md
- paper-ready/v1/c4/evidence_crosswalk.tsv
- paper-ready/v1/c5/draft_evidence_audit.md
- paper-ready/v1/c5/forbidden_claim_scan.md
- paper-ready/v1/c6/cleaned_draft_with_markers.md
- paper-ready/v1/c6/polish_issue_list.tsv
- paper-ready/v1/c6/target_venue_readiness_checklist.md
- paper-ready/v1/c6/c6_decision.md
- results/formal/formal-candidate-summary.csv
- results/formal/formal-group-summary.csv
- results/paper-data/synthetic-six-benchmark-summary.csv
- results/public-benchmarks/c1/statistics/public-c1-statistical-report.md

## Files created

- paper-ready/v1/d0/experimental_weakness_review.md
- paper-ready/v1/d0/reviewer_risk_matrix.tsv
- paper-ready/v1/d0/experiment_claim_fit.tsv
- paper-ready/v1/d0/b5_options.md
- paper-ready/v1/d0/d0_decision.md
- docs/v1-restart/PHASE_D0_EXPERIMENTAL_WEAKNESS_REVIEW.md

## Experiments and source changes

- Experiments executed: **NONE**.
- Echidna/Slither/solc/fuzzer/runner executed: **NONE**.
- Benchmark source changes: **NONE**.
- Existing benchmark changes: **NONE**.
- Frozen result changes: **NONE**.
- matched-random-v1 used for new claims: **NO**; it remains quarantined.
- V2/C2 results pooled into V1: **NO**.
- Commit or push: **NONE**.

## Key findings

1. The current evaluation has a strong provenance and mechanism-evidence foundation, not merely a single toy demonstration.
2. The largest C-venue risks are four-task public diversity, falsification-rate ceiling effect, incomplete target-rank/reachability metric coverage, and the lack of one unified lightweight component ablation.
3. Ten seeds are adequate for the next scoped descriptive step; full 10→30 expansion would add repeated runs but not new contracts, mechanisms, or semantic validity.
4. Original Echidna is the correct main executable baseline because PHS is a preprocessing layer before Echidna. Literature tools remain conceptual/Related Work baselines unless a fair, low-cost executable alignment becomes available.
5. Controlled/custom scenarios are academically legitimate when they isolate the declared stateful fuzzing obstacles and are labeled honestly. They should be a core mechanism layer, not a disguised public ecosystem claim.

## B5 decision

**YES — GO TO B5.**

Recommended B5-Min: three deeper controlled/custom scenarios plus lightweight ablation, using rank/Top-K hit, target-state reachability, hard-scenario trigger/time, and seed stability as the main dimensions. Preserve B4 exactly, use Original Echidna as the main baseline, and do not run the full 30-seed expansion.

## Recommended next phase

The next phase is B5 pre-registration and execution preparation. Before any execution, separately freeze scenario source, property, method versions, budgets, seeds, semantic model, success/failure definitions, output roots and checksum rules. If two independent public tasks pass source and semantic gates, add them as the B5-Strong extension; otherwise do not fabricate public diversity. A later C7 remains a writing/venue-formatting phase after the selected evidence package is complete.

## Git diff summary

D0 adds only the six review/decision/closeout documents listed above. The five pre-existing worktree modifications listed under Repository state remain untouched. No files under results/frozen/, results/matched-random-v1/, or existing benchmark source directories were changed by D0.
