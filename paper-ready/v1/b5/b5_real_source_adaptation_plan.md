# B5-3 Real-Source Adaptation Plan

Status: conditional appendix preparation only; no adapted source was created in B5-3.

## Principle

Any future extension must remain an adapted real-source benchmark, not a claim about an untouched source artifact. The original source, the local adaptation, the property rationale and every compile-only change must be separately hashed and reviewable.

The proposed future directory for the conditional candidate is:

contracts/benchmarks/b5-real-source-adapted/b5-rs-exercise2-access-control/

This directory is intentionally not created in B5-3 because the canonical source/license packet is not yet archived.

## Conditional candidate: exercise2-access-control

### Original source preservation

Archive the canonical solution.sol and its imported token.sol from the pinned repository commit 2de122e3a6b63bc450a1ec41215f0c44d72fb96b. Preserve the retrieval URL, commit, license evidence, exact byte hashes and a provenance README. The current local raw files are evidence for screening only; they are not a substitute for a newly verified source packet.

The existing local hashes are:

- solution.sol: e52c8081b55f64ed7a562a492714e969026f5e548b2fa99e19213d9f6b59f8fe
- token.sol: 87f802a00cb8b4fb991af8d80838fe40a24bd6b6cf1419f89e3505356065738a

### Proposed adapted naming

- original/solution.sol
- original/token.sol
- adapted/TestTokenExercise2Echidna.sol
- README_PROVENANCE.md
- ADAPTATION_DIFF_NOTES.md
- checksums.tsv

No adapted file should be generated until the canonical snapshot and license are manually confirmed.

### Dependencies and stubs

The current closure is solution.sol -> token.sol with no external import. No dependency stub is planned. If a future environment requires a stub, the stub must be a separate file with a diff note and the task must be downgraded unless the target state transition is demonstrated unchanged.

### Permitted source changes

- pin the compiler invocation to solc 0.8.20 for pragma ^0.8.0;
- add or rename a passive observer only if it cannot alter target state;
- add an Echidna property only if the property is part of the declared task and its construction is recorded.

No change may alter owner initialization, pause/resume behavior, caller checks, balances mapping or failure behavior.

### Semantic changes and gate

The source uses msg.sender, owner equality and an address-keyed balances mapping. The key path is Owner() -> resume() under one caller. Original may explore multiple senders while the wrapper usually calls through one Harness address. Therefore:

- same-caller replay is a conditional compatibility check;
- alternating-caller replay is a separate semantic-risk case;
- any caller-dependent result is excluded from the supported pooled result;
- wrapper-wide rollback and multi-transaction rollback must be logged separately;
- no task with an unresolved caller/rollback mismatch enters execution.

### Property and observer

The declared property is echidna_no_transfer, observing paused() == true. The source already includes the property. A passive observer is not required. If a helper observer is added for target-state reachability, it must be view-only, hash-recorded and excluded from the fuzzer guidance.

The Owner() -> resume() sequence is an audit annotation and replay oracle only. It must not be inserted as a fixed fuzzer input or encoded as a target skeleton in a way that guides the fuzzer.

### Future method comparison

After the gate, compare:

- Original Echidna on the archived source;
- PHS Full-K1;
- PHS Full-K5.

Use the same declared property and budget, while reporting the execution-model boundary. Compare target-state reachability, candidate rank, Top-K retention, trigger outcome, falsification status and censored time-to-falsify. Do not use Total calls as an equal-work speedup measure.

This task must remain a separate conditional stratum. It must not be pooled with supported public tasks or controlled/custom scenarios.

## Candidates requiring manual source acquisition

The four non-conditional legacy candidates are structurally promising but cannot move forward on the current local packet:

- Echidna flags: source license evidence and canonical snapshot;
- Echidna multi: source license evidence and canonical snapshot;
- SmartBugs multi-function: source license evidence, canonical snapshot and property-construction review;
- SmartBugs one-function: source license evidence, canonical snapshot and property-construction review.

For each, provide repository URL, pinned commit/tag, exact source path, license evidence, original checksum, compiler record, dependency closure and a predeclared property rationale. Do not choose among them after looking at PHS results.

## Recommended future execution protocol

Only after source/adaptation gate passes:

- 10 seeds per method for the first conditional screening batch, seeds 1..10;
- testLimit=100000;
- timeout=30s;
- workers=1;
- stopOnFail=false;
- methods: Original, Full-K1, Full-K5;
- preserve every compile_error, startup_error, parser_error, unknown_error and incomplete row;
- budget_exhausted is right-censored and never a property pass;
- no replacement seed and no overwritten run directory.

Recommended metrics:

- target-state reachability and reachability rate;
- target candidate rank and Top-1/Top-5 retention;
- observed trigger outcome;
- falsification status and censored time-to-falsify;
- process wall time and preprocessing time, reported descriptively;
- artifact completeness and input/output checksums;
- semantic replay agreement under the declared caller schedule.

A later expansion to 30 seeds is not part of B5-3 and should require a separate preregistration decision.

## Main-text and appendix boundary

Until the gate passes, do not write execution outcomes into the main results. If the conditional task passes the gate, report it as a separately labeled external-validity appendix/case study. It can support a narrow statement about the screened task under the declared caller schedule; it cannot support a broad statement about smart contracts generally.
