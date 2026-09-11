# B5-3R Exercise2 Caller / Replay Gate Plan

Status: PREPARED_NOT_EXECUTED
Candidate: b5-rs-exercise2-access-control
Source: crytic/building-secure-contracts at commit 2de122e3a6b63bc450a1ec41215f0c44d72fb96b

## Why the task is conditional

The source uses msg.sender in Ownable.Owner(), onlyOwner, and the constructor-owned pause transition. The dependency closure also contains mapping(address => uint256) balances. The intended Owner() -> resume() path depends on the same caller becoming owner and then invoking resume. Original Echidna may use multiple independent transactions and may alternate callers. The generated Harness normally calls target functions through one Harness address and folds multiple calls into one wrapper transaction.

Therefore the task must remain conditional. A replay match under one caller is evidence for that declared schedule only; it is not semantic equivalence between Original and Harness.

## Same-caller replay

Use deterministic transactions with a fixed caller A:

1. Deploy TestToken under the declared deployer condition. Record paused(), owner and balances.
2. Confirm constructor state: pause() was called, then owner was set to address(0), so paused() is true.
3. Call Owner() from A. Record owner == A and paused() remains true.
4. Call resume() from A in a separate transaction. Confirm the call succeeds and paused() becomes false.
5. Evaluate echidna_no_transfer after the transition and record the property result.
6. Repeat the same sequence through the candidate Harness model and record target-state reachability, final paused state, rollback scope and caller identity.

The replay must record raw trace, caller, transaction boundary, success/revert status, state before/after and SHA-256.

## Alternating-caller replay

Run at least two deterministic schedules with distinct callers A and B:

- Owner() from A, resume() from B: resume() must fail under onlyOwner; record whether owner and paused state remain unchanged.
- Owner() from B, resume() from A: same caller mismatch check.
- If a wrapper invokes both calls atomically, compare the wrapper rollback state with the two-transaction Original state. A failed wrapper may roll back Owner() as well, which is a different boundary.

Do not use these schedules as fuzzer guidance. They are semantic gate inputs only.

## Required comparison fields

For each schedule record:

- deployment/deployer and initial owner;
- caller for every transaction or wrapper call;
- function and arguments;
- transaction boundary and block context;
- success or revert;
- paused(), owner and relevant mapping observations;
- property result;
- final state and rollback scope;
- original trace hash and Harness trace hash.

## Appendix-only outcomes

The following remain conditional appendix evidence:

- any result relying on a fixed caller;
- any alternating-caller result;
- any result where Original and Harness final property state differs;
- any result where wrapper rollback differs from the declared Original schedule;
- any result where caller identity or mapping key cannot be controlled;
- any result obtained after an adaptation changes owner, pause, resume, mapping or failure semantics.

## Mandatory BLOCK conditions

Set the gate to BLOCK if:

- source or LICENSE hash differs from this packet;
- the canonical commit cannot be verified;
- the dependency closure changes without a new packet;
- same-caller replay fails to reproduce the declared state transition;
- alternating-caller behavior is not separately recorded;
- a wrapper changes the property-relevant state relative to the declared schedule;
- an implementation attempts to hide caller alternation or rollback differences;
- a formal run is attempted before preregistration review.

## Prohibited interpretation

Do not claim Original and Harness semantic equivalence. Do not compare Total calls as equal work or speedup. Do not call budget_exhausted a property pass or safety result. The candidate cannot enter the supported pooled result even if same-caller replay succeeds.
