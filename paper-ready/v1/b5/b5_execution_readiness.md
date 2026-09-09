# B5-1R3 Execution Readiness

## Final decision

**READY_FOR_B5_MAIN_RUN**

This authorizes B5-2 preparation only; it does not execute or promote a formal
result.

## Environment

- contract-fuzz Python 3.11.15: PASS
- solc 0.8.20: PASS
- Slither 0.11.5: PASS
- Echidna 2.3.2 via echidna: PASS
- echidna-test alias: unavailable and not used
- bash -n scripts/run_b5_controlled.sh: PASS

## Runner gates

py_compile, CLI help, invalid scenario, invalid method, dry-run, duplicate
run-id guard, and smoke/formal isolation: PASS. Original observer relative
import normalization and final metric/checksum finalization: PASS. Formal runs
remain authorization-locked.

## Scenario gates

- C1 PASS: source compiled; accepted Original and Full-K1 completed; metrics
  dependency=36, property=4, reduction=0.888889, target rank=1; no forbidden
  caller/value/time/external-call/reentrancy dependency.
- C2 PASS: source compiled; required advance repeat=3 and bound=3; Full-K1
  observed repeat=3 and reached passive target; target skeleton is not runner
  guidance.
- C3 PASS: source compiled; value evidence is storage constants plus
  require(route == 3); no msg.value/payable; rank, Top-K, reachability and
  value flags are available.

## Smoke gates

Required cells: 6/6 accepted after engineering fixes. One Original and one
Full-K1 for each scenario. All accepted artifacts are complete and checksum
verified. Two earlier C1 Original attempts remain retained outside the accepted
set.

## Metrics and provenance

Accepted rows contain status, property/budget flags, target reachability/rank/
Top-K, candidate counts/reduction, repeat/value flags, timing, artifact and
checksum fields. Empty fields represent non-applicability; unknown values are
not fabricated zeros. Each run has manifest, command, environment, generated,
raw, parsed, summary, status, checksums and verification output. Smoke is never
a formal summary input.

## Planned B5-Min scale

C1 = 4 methods x 10 seeds = 40; C2 = 4 x 10 = 40; C3 = 4 x 10 = 40;
total = 120 planned formal runs. Seeds are exactly 1..10. Formal budget is
testLimit=100000, timeout=30s, workers=1, stopOnFail=false. No 30-seed
expansion, public benchmark, or external baseline is planned.

Existing evidence remains B4 public = 120 formal runs (118 falsified,
2 budget_exhausted); existing Formal mechanism evidence is preserved. Frozen,
legacy, B4, and matched-random results were not modified.
