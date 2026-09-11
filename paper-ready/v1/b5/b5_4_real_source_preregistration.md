# B5-4 Real-Source Extension Preregistration

Status: PREREGISTERED_FUTURE_EXECUTION_NOT_RUN

## Scope

This phase freezes a future PHS external-validity extension. It performs provenance, property, dependency and deterministic preflight only. It does not run Echidna formal fuzzing, the 10-seed matrix, B5-Min controlled runs or a 30-seed expansion. Real-source evidence stays separate from controlled/custom B5-Min and frozen B4/B5-2 evidence; Original and Harness are not asserted semantically equivalent.

## Strata and future plan

Supported: b5-rs-echidna-flags, b5-rs-echidna-multi, b5-rs-smartbugs-multifunc and b5-rs-smartbugs-onefunc. Each uses Original, Full-K1 and Full-K5, seeds 1..10, testLimit=100000, timeout=30s, workers=1, stopOnFail=false: 4 x 3 x 10 = 120 future formal rows.

Conditional appendix: b5-rs-exercise2-access-control. If separately authorized, it uses the same methods/seeds plus same-caller and alternating-caller replay. It is excluded from the supported expected registry and pooling.

## Provenance, license, hashes and compiler

Canonical packets are in contracts/benchmarks/b5-real-source-adapted/<candidate_id>/. Pinned commits, URLs, license evidence, original/adapted SHA-256 and packet checksums are in b5_real_source_provenance_registry.tsv and each packet.

| Candidate | Source/commit | License | Compiler | Dependency/adaptation |
|---|---|---|---|---|
| flags | crytic/echidna @ 4454f3a337ed58e89a3be488b8eac03e83cd40f2 | AGPL-3.0 archived | solc 0.8.20; pragma ^0.8.0 | self-contained; unrelated self-tests excluded |
| multi | crytic/echidna @ 4454f3a337ed58e89a3be488b8eac03e83cd40f2 | AGPL-3.0 archived | solc 0.8.20 pin; no source pragma | self-contained; byte-identical copy |
| multifunc | smartbugs/smartbugs-curated @ 230e649123477eff332742a59a1c7cc6dc286cab | Apache-2.0 archived | solc 0.4.25; pragma ^0.4.23 | self-contained after adaptation; property added |
| onefunc | smartbugs/smartbugs-curated @ 230e649123477eff332742a59a1c7cc6dc286cab | Apache-2.0 archived | solc 0.4.25; pragma ^0.4.23 | self-contained after adaptation; property added |

## Properties and gate

Flags retains upstream echidna_sometimesfalse; multi retains upstream echidna_state3. SmartBugs uses a researcher-authored echidna_count_does_not_underflow oracle derived from the archived overflow/underflow labels; it is not claimed as an upstream Echidna property. The construction review is in b5_4_smartbugs_property_review.md. No target sequence is supplied as fuzzer input.

analyzer/b5_4_real_source_gate.py defaults to dry-run. --execute-preflight is required to create gate-only artifacts; --compile only attempts compiler checking. Each run id is b5-4-gate-<candidate_id>-preflight; collisions are refused. Artifacts are under work/v1-restart/, paper_usable=false, and never formal results.

Future metrics: trigger outcome under the declared model, falsification versus right-censored budget_exhausted, target reachability, target rank, Top-1/Top-5 retention, preprocessing/process wall time and checksum completeness. Total calls is not a speedup measure.

## Rules and placement

Include only the four supported candidates after all gates pass. Exclude exercise2 from the supported pool and report it appendix-only after caller/replay review. Exclude mismatches, unresolved dependencies/properties, compile errors, caller-sensitive mismatch or unreviewed semantic changes. Do not select by PHS outcome. Future supported evidence may be separately labeled adapted real-source evidence with packet details in appendix/supplement. Do not claim ecosystem-wide superiority, Original/Harness equivalence, safety from budget exhaustion or upstream SmartBugs Echidna properties.

