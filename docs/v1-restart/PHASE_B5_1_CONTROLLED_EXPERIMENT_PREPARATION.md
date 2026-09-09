# Phase B5-1 Closeout: Controlled Experiment Preparation

## State and scope

Starting/ending HEAD: f71c1a60870c93d26323daeedfbc8e9d4c021e59.
Branch: develop. The five D0 pre-existing dirty files were preserved:
analyzer/build_main10_preregistration.py, analyzer/run_native_replay_gate.py,
docs/v1-restart/PHASE_B3_CLOSEOUT.md,
docs/v1-restart/PHASE_B3_MAIN10_PREREGISTRATION.md, and
scripts/run_v1_public_smoke_case.sh. Existing untracked B5 preparation files
were also preserved. No revert, cleanup, commit, or push was performed.

B5-1R3 ran only six accepted seed-1 smoke cells under
work/v1-restart/<run_id>/; each is SMOKE_ONLY/paper_usable=false. No formal
10-seed run, 30-seed expansion, public benchmark expansion, or external
baseline was executed. No frozen/B4/legacy result was touched.

## Scenarios and methods

C1 Irrelevant-State Explosion tests property-directed filtering in a five-step
chain. C2 Deep Repeated Transition requires three state-changing advance()
calls. C3 Value-Gated Competing Paths has three route setters but only route=3
passes the simple storage-value gate. Every property is echidna_exposure_safe.
Definitions are frozen in the registry and preregistration; target skeletons
are evaluation-only and never injected into fuzzing.

Formal cells are C1 Original/Dependency-only/Full-K1/Full-K5, C2
Original/No-Repeat/Full-K1/Full-K5, and C3 Original/No-Value/Full-K1/Full-K5.

## Smoke and engineering fixes

Accepted:
b5-smoke-c1-original-s1-r3-retry2 (budget_exhausted);
b5-smoke-c1-full-k1-s1-r3, b5-smoke-c2-original-s1-r3,
b5-smoke-c2-full-k1-s1-r3, b5-smoke-c3-original-s1-r3, and
b5-smoke-c3-full-k1-s1-r3 (falsified).

The first C1 Original attempt was compile_error due to an absolute import; the
next retry exposed metric finalization pending. Both failed engineering
attempts were retained and excluded from the accepted six. Total invocations:
eight. Accepted artifacts: 6/6 complete and checksum pass.

C1 smoke counts dependency=36/property=4/reduction=0.888889. C2 dependency=12/
property=3 and Full-K1 observed repeat=3. C3 dependency=21/property=5. These
are mechanism fields, not speedup claims. budget_exhausted remains
right-censored and not a pass/safety proof.

## Frozen protocol and provenance

Formal seeds=1..10; formal budget=testLimit=100000, timeout=30s, workers=1,
stopOnFail=false. Planned formal runs: 120 (40 per scenario), generated only
in b5_expected_runs.tsv; no formal result TSV exists. Source/config/runner/
analyzer hashes are frozen in b5_preregistration.md. B4 public evidence remains
120 formal runs, 118 falsified and 2 budget_exhausted; existing Formal evidence
is preserved. results/frozen/, results/matched-random-v1/, B4 TSVs and legacy
quarantine are unchanged.

## Readiness

**READY_FOR_B5_MAIN_RUN**

B5-2 must use only the expected registry after researcher review, preserve all
hashes, reject run-id collisions, and never replace failed seeds.
