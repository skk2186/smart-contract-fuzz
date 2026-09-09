# B5-Min Preregistration

Status: frozen for B5-2 after B5-1R3. This is a future formal protocol, not a
formal result.

## Research questions

C1 tests whether property-directed filtering reduces irrelevant candidates in a
five-step state chain. C2 tests whether bounded repeat preserves three real
advance calls. C3 tests whether lightweight storage-constant/threshold evidence
ranks a verified route above competing routes. Across C1-C3, target rank,
Top-K retention, target-state reachability, repeat preservation, value flags,
fixed-budget trigger outcome, and censored timing are primary dimensions;
candidate counts are mechanism metrics.

PHS is an external property-directed preprocessing and Solidity Harness
synthesis layer before Echidna; it does not replace or modify Echidna.

## Frozen scenarios and oracle

All three are controlled/custom/synthetic, never public or real-world
benchmarks. Every property is echidna_exposure_safe and fails when exposure >
100.

- C1 source contracts/benchmarks/b5-controlled/IrrelevantStateExplosion.sol;
  skeleton initialize() -> configure() -> authorize() -> activate() ->
  expose(uint256); state initialized && configured && authorized && active.
- C2 source contracts/benchmarks/b5-controlled/DeepRepeatedTransition.sol;
  skeleton prepare() -> advance() x3 -> unlock() -> trigger(uint256); state
  prepared && progress == 3 && unlocked. max-function-visits=3.
- C3 source contracts/benchmarks/b5-controlled/ValueGatedCompetingPaths.sol;
  skeleton selectVerifiedRoute() -> unlock() -> activate() ->
  trigger(uint256); state unlocked && active, with route == 3 required.

The skeleton and passive observer are evaluation-only, never injected as
fuzzing guidance. C2 uses a real state-changing repeat; fewer than three
advance calls cannot unlock. C3 value evidence is limited to Solidity
parameters/storage constants/simple require comparisons, not msg.value/payable.

## Frozen methods and ablation

C1: Original, Dependency-only, Full-K1, Full-K5.
C2: Original, No-Repeat, Full-K1, Full-K5.
C3: Original, No-Value, Full-K1, Full-K5.

Original is the primary empirical baseline. Full-K1 and Full-K5 are PHS
configurations. Other methods are mechanism-targeted ablations. K=1 or 5 is
recorded only for Full-K1/Full-K5; non-K methods use a bounded five-candidate
Harness generation while recording k=NA.

## Frozen execution protocol

Formal seeds are exactly 1..10 with no substitution/deletion. Formal budget is
testLimit=100000, timeout=30s, workers=1, stopOnFail=false, property mode.
Original uses configs/b5-controlled-original.yaml (seqLen=6); Harness uses
configs/b5-controlled-harness.yaml (seqLen=1). Baseline is Python 3.11.15,
solc 0.8.20, Slither 0.11.5, Echidna 2.3.2. Formal and smoke output both use
work/v1-restart/<run_id>/; smoke is SMOKE_ONLY and paper_usable=false. Existing
run IDs/symlinks are rejected. Formal execution remains locked until B5-2.

All methods in a scenario share its declared budget. The 100000 budget comes
from the existing B4-scale config and was not tuned to smoke outcomes. No
results/frozen, results/matched-random-v1, B4 TSV, or legacy result path is an
output.

## Definitions, semantics, exclusion

falsified means an explicit property failure marker. budget_exhausted means no
observed counterexample within budget and is right-censored, never a pass or
safety proof. Falsification has priority over budget markers. Other states are
compile_error, startup_error, parser_error, unknown_error, incomplete.

The scenarios avoid msg.value, payable, msg.sender, caller alternation,
block.timestamp, block.number, tx.origin, external calls, delegatecall,
reentrancy, caller-keyed mappings, and failure-dependent progression. Original
still explores independent transactions; Harness executes candidate calls in one
wrapper transaction, so no semantic equivalence or Total-calls speedup claim is
authorized.

Exclude any future formal row with unreconciled source/config hash, method,
manifest, raw/parser/status, artifact, or checksum. Retain failed rows and
never replace seeds. Smoke is never formal evidence.

## Frozen hashes and scale

HEAD: f71c1a60870c93d26323daeedfbc8e9d4c021e59.
C1: 8588a49e2abc4cee2095151b1e5096d6244e9be5d8181f180cd2be255f51389a
C2: b90da876eb45c5cc362b7e036ecded16c7bb49c5fabce0afc8f9e11518b29b7a
C3: d06eb432877382dae3d9b5509ae804c215f49c9d4b67ba3b82443a90d8b477ac
scenario config: ceec93e6954e7a615111f84cf898e8faceff422c0aa3ba330147dd999dcaca6d
original config: 72f72d7d12872a9d68b9690371cab8f3299e9ca118b62a3e36c474161ed41fd5
harness config: 358ddfa976276895acde3818bed0cd142ae2a96c5dce8513aca083e5c9b7a486
runner: 65151990f9b18989d030f044a5f2bb6b6e41564965c9308f7df6e11318b729e3
metric analyzer: 9b0ff0d02d6e74ac8ee2cf5c99559cd962bb006ffa0e707240fa7ee2942636a6
wrapper: 9ab3aec9f8a40d640cbe98f0f60cfabd45c3d9ec43b335443f86092338d124b9

The expected registry contains 12 cells x 10 seeds = 120 planned formal runs:
40 each for C1, C2, C3. B5-Min adds non-saturated mechanism evidence and
component attribution, not run count for its own sake. No formal result TSV is
created in B5-1.
