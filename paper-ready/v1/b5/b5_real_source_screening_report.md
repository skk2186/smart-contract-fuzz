# B5-3 Real-Source Extension Screening Report

Date: 2026-09-11
Starting branch: develop
Starting HEAD: 30d1558c897321899a8de059e9585be08ff98b58
Decision: NEED_MANUAL_CANDIDATE_SOURCE

## Scope

B5-3 screens a small set of real-source or adapted-real-source candidates for a possible stronger external-validity package. It does not run formal fuzzing, does not run B5-Min again, and does not change the B4 or B5-2 evidence layers.

The fixed method remains PHS (Property-directed Harness Synthesis), an explicit safety-property-driven preprocessing and external Solidity Harness synthesis layer before Echidna. PHS does not replace or modify Echidna core.

## What B5-Min already supports

B5-Min has three controlled/custom scenarios:

- C1 Irrelevant-State Explosion;
- C2 Deep Repeated Transition;
- C3 Value-Gated Competing Paths.

The frozen package has 12 cells and 120 formal runs. It supports scenario-specific evidence for candidate relevance, bounded repeat, value evidence, target rank, Top-K retention and target-state reachability. It does not by itself establish broad real-contract external validity. Controlled/custom sources are therefore kept separate from the real-source screen.

## Why an extension is considered

A stronger C-venue package would benefit from a small number of independently sourced contracts whose state transitions and properties are not authored as B5 mechanisms. The purpose is external-validity evidence, not a replacement for the controlled mechanism layer and not a race to increase the run count.

## Scan procedure and evidence boundary

This was a repository-only static scan. No network access was used. No external source was downloaded or copied. No Solidity compiler, Slither, Echidna fuzzing, or formal experiment was run in B5-3.

The scan inspected the required B5/D0/B5-2 documents plus:

- results/public-benchmarks/c2-screening/candidate-registry.tsv;
- results/public-benchmarks/c2-screening/source-pools.tsv;
- results/public-benchmarks/sources.tsv;
- results/public-benchmarks/c1/adaptations.md;
- the five existing public source closures under contracts/public-benchmarks;
- the existing semantic gate and public registry.

The structured C2 registry records repository names, pinned revisions and source paths for five legacy candidates. The separate sources.tsv is not parseable as a tab-separated file in the current checkout: its rows have no tab delimiters. This is recorded as a provenance-quality finding, not repaired in B5-3.

## Candidate judgments

The complete row-level record is in b5_real_source_candidate_registry.tsv.

| Candidate group | Reviewer-style judgment | Status |
|---|---|---|
| Echidna flags | Structurally relevant two-step property state, but the local package lacks a canonical license/source archive. The adapted file removes two framework properties and must retain that diff. | needs_manual_source |
| Echidna multi | Three-step require-gated property chain with low target-path semantic risk, but source/license evidence is incomplete in the local package. | needs_manual_source |
| SmartBugs multi-function | Repeated state transition is relevant, but the Echidna property is locally constructed from a vulnerability label and the 0.4.x compiler semantics need explicit provenance. | needs_manual_source |
| SmartBugs one-function | Repeated transition is relevant but mainly integration evidence; the property is locally constructed and the source license packet is incomplete. | needs_manual_source |
| exercise2-access-control | Clear public training source and explicit SPDX license in the local closure, but caller identity and address-keyed state make the task conditional. It requires caller-controlled replay before any execution result. | conditional_requires_adaptation |
| Internal AlternativePath, MultiProperty, ThreeStep | Useful controlled/custom records, but repository-authored and not independent external sources. | rejected |

Counts are: accepted_for_preregistration = 0; conditional_requires_adaptation = 1; rejected = 3; needs_manual_source = 4.

## Selection-bias risk

The candidate list was inherited from the previously frozen local public registry and screened by source/provenance and semantic criteria, not by B5 outcome. No candidate was added, removed or upgraded because PHS appeared successful. The main remaining risk is availability bias: the local pool is a small legacy sample and lacks a complete archived source/license packet. A later acquisition must freeze the candidate set before looking at PHS results and must preserve all screened-out rows.

## Semantic-mismatch risk

The existing semantic audit identifies caller, transaction atomicity, rollback, value, block environment and external-call boundaries as risks. The conditional exercise2 task uses msg.sender, owner equality and an address-keyed mapping. Its Owner() -> resume() path depends on caller consistency. The current PHS wrapper model cannot be treated as equivalent to Original multi-transaction execution for this task. Any later execution must be conditional, with same-caller and alternating-caller schedules explicitly separated.

The other four legacy candidates have lower target-path semantic risk in the local static scan, but that does not repair the missing source/license packet or prove semantic equivalence.

## Property-construction risk

The Echidna examples expose upstream properties. The SmartBugs cases do not: the local adaptation adds an Echidna property to a vulnerability-labeled arithmetic source. That property construction is reasonable as a screening hypothesis, but it is a researcher-authored oracle and must be documented, independently reviewed and hash-frozen before execution. A label is not automatically an Echidna safety property.

## C-venue stronger-package assessment

B5-3 does not yet provide an unconditional supported real-source pool. It provides one potentially usable conditional appendix candidate and four candidates requiring manual source/license acquisition. The conditional candidate can improve external validity only as narrowly reported evidence after the required gate. It cannot change the B5-Min conclusion, be pooled with the four supported legacy tasks, or support a general superiority claim.

If manual provenance is supplied and the caller gate passes, one conditional task is still a small external-validity increment. It would be appropriate as a separate appendix or a clearly labeled case study; it is not enough to claim broad real-world coverage. A second independent candidate with a different state pattern would materially strengthen the package.

## No fabrication rule

No candidate is promoted merely because it is already present in the repository. Internal controlled/custom contracts remain controlled/custom. If a source archive, license evidence, commit/tag and property rationale cannot be supplied, the candidate remains outside the execution pool. The study should report the screening failure instead of manufacturing a larger benchmark set.

## Immediate next action

Obtain or provide canonical source packets for the four needs_manual_source candidates, and a license/source archive plus caller-controlled replay plan for exercise2. Then freeze the candidate registry, adaptation diffs, hashes and execution protocol before any B5-4 run. Until that occurs, C7 may proceed with the documented limitation that external validity is limited.
