# B5-3 Real-Source Conditional Preregistration

Status: CONDITIONAL_CANDIDATE_PENDING_MANUAL_PROVENANCE_AND_CALLER_GATE
Formal execution status: NOT_RUN

This preregistration is for one conditional appendix candidate. It does not authorize a B5-4 run yet. Execution requires completion of the source/archive and caller-controlled replay gate below.

## Benchmark identity

- benchmark_id: B5-RS-PUB05-EXERCISE2
- source_name: Building Secure Contracts exercise 2
- source_type: public training benchmark, conditionally adapted
- local screening source: contracts/public-benchmarks/raw/exercise2/solution.sol
- dependency closure: solution.sol imports token.sol from the same pinned source directory
- contract: TestToken
- source URL: https://github.com/crytic/building-secure-contracts/tree/2de122e3a6b63bc450a1ec41215f0c44d72fb96b/program-analysis/echidna/exercises/exercise2/solution.sol
- repository: crytic/building-secure-contracts
- commit: 2de122e3a6b63bc450a1ec41215f0c44d72fb96b
- source path: program-analysis/echidna/exercises/exercise2/solution.sol
- license: AGPL-3.0 as declared by SPDX headers in the local solution.sol and token.sol; canonical repository license archive remains a precondition
- compiler: solc 0.8.20, source pragma ^0.8.0

## Hashes

Original local screening files:

- solution.sol SHA-256: e52c8081b55f64ed7a562a492714e969026f5e548b2fa99e19213d9f6b59f8fe
- token.sol SHA-256: 87f802a00cb8b4fb991af8d80838fe40a24bd6b6cf1419f89e3505356065738a

Adapted file SHA-256: NOT_GENERATED_IN_B5-3
Canonical source archive hash: PENDING_MANUAL_ACQUISITION

## Property and target state

- property: echidna_no_transfer
- property source: upstream Echidna exercise property in solution.sol
- observed target state: paused() == true, so the property remains true
- audit sequence annotation: Owner() -> resume() under a fixed caller
- stateful depth estimate: 2
- relevant PHS pattern: property-dependent state plus owner/caller-gated transition
- passive observer: not required; any future view-only observer must be separately hashed

The sequence annotation is an audit/replay oracle only. It is not supplied to the fuzzer as guidance.

## Inclusion and exclusion rules

Include only after all of the following are complete:

1. Canonical solution.sol and token.sol are archived from the declared commit.
2. Canonical license evidence and source URL are stored in README_PROVENANCE.md.
3. Original and any adapted files have SHA-256 records.
4. Compiler and dependency closure are fixed.
5. Same-caller native replay confirms the target-state transition and property interpretation.
6. Caller alternation and rollback differences are recorded as semantic conditions.

Exclude from the supported pooled result if any of the following holds:

- caller identity is needed but not controlled or documented;
- source or license provenance remains unresolved;
- adaptation changes owner, pause, resume, mapping, failure or rollback semantics;
- the property is changed after seeing PHS outcomes;
- a run has unresolved compile, startup, parser, unknown or incomplete status;
- an output directory or raw log would be overwritten.

This candidate may be reported only as a conditional appendix until the inclusion gate passes.

## Methods and execution protocol

Planned methods are Original, PHS Full-K1 and PHS Full-K5. All use the same declared property, compiler and budget. The methods are not claimed semantically equivalent.

Planned first screening batch, only after gate completion:

- seeds: exactly 1..10;
- testLimit: 100000;
- timeout: 30s;
- workers: 1;
- stopOnFail: false;
- no seed substitution;
- no rerun over an existing run id;
- output root: work/v1-restart/<run_id>/.

B5-3 itself runs none of these methods.

## Status definitions

- falsified: explicit property failure marker observed.
- budget_exhausted: budget ended without an observed counterexample; right-censored, not a pass or safety proof.
- compile_error: declared source/config could not compile.
- startup_error: execution could not start.
- parser_error: raw output exists but cannot be classified by the fixed parser.
- unknown_error: unclassified termination.
- incomplete: required artifacts or completion marker missing.

Engineering errors remain in the denominator and are not replaced by another seed.

## Metrics

Primary:

- target-state reachability and reachability rate;
- target candidate rank;
- Top-1 and Top-5 retention;
- observed trigger outcome;
- falsification status and censored time-to-falsify.

Secondary:

- preprocessing time;
- process wall time, descriptively;
- artifact completeness;
- checksum pass;
- native replay agreement under the declared caller schedule.

## Prohibited claims

This preregistration does not authorize claims that:

- the adapted task represents the smart-contract ecosystem;
- the conditional task can be pooled with supported public or controlled/custom tasks;
- Original and Harness are semantically equivalent;
- Total calls measure equal underlying work or prove speedup;
- budget_exhausted means property passed or the contract is safe;
- a single conditional task proves general superiority;
- the source is untouched after adaptation.

## Required release gate

Before B5-4 execution, manually add the canonical source/archive evidence, update hashes, record adaptation diffs if any, complete same-caller and alternating-caller replay notes, and have the researcher review the final inclusion decision. No execution output is produced by B5-3.
