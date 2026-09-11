# B5-3R Real-Source Gate Decision

Decision: GO_TO_B5_4_PREREGISTRATION

## 1. Canonical source archive

All five candidates have canonical source files archived from their pinned commits under:

contracts/benchmarks/b5-real-source-adapted/<candidate_id>/original/

The archived dependency closure for exercise2 contains solution.sol and token.sol. The other four candidates are self-contained.

## 2. License confirmation

All five repository LICENSE files were retrieved and archived:

- crytic/echidna: AGPL-3.0;
- crytic/building-secure-contracts: AGPL-3.0;
- smartbugs/smartbugs-curated: Apache-2.0.

The exercise2 source files also contain SPDX AGPL-3.0 headers. The exact LICENSE and source hashes are in b5_real_source_provenance_registry.tsv and each packet's checksums.tsv.

## 3. Supported real-source candidates

Four candidates are ready for B5-4 preregistration as supported real-source candidates under the declared execution model:

- b5-rs-echidna-flags;
- b5-rs-echidna-multi;
- b5-rs-smartbugs-multifunc;
- b5-rs-smartbugs-onefunc.

Ready for preregistration does not mean formal execution has occurred. The four tasks remain small public/adapted integration cases, and the SmartBugs properties are locally added or adapted oracles that must be frozen in the next preregistration.

## 4. Conditional appendix candidate

b5-rs-exercise2-access-control remains conditional_appendix_only. It requires same-caller and alternating-caller replay, explicit rollback recording and researcher review. It must not enter a supported pooled result.

## 5. Remaining gates

- task-level deterministic replay for the four supported candidates;
- property-construction review for both SmartBugs candidates;
- caller/replay gate for exercise2;
- B5-4 preregistration fixing methods, seeds, budget, metrics, status definitions and exclusion rules.

## 6. B5-4 readiness

B5-3R authorizes progression to B5-4 preregistration only. It does not authorize B5-4 formal fuzzing, 10-seed experiments or any controlled formal rerun.

## 7. C7 and external validity

C7 writing may proceed now with the existing B5-Min conclusion and the explicit limitation that external validity is narrow. The new packets strengthen provenance and prepare a possible external-validity appendix; they do not prove broad real-world coverage or universal superiority.

## 8. Required separation

Controlled/custom B5 scenarios, previously screened public evidence, the four preregistration-ready adapted candidates and exercise2 conditional evidence must remain separate strata. No pooled result is created by B5-3R.
