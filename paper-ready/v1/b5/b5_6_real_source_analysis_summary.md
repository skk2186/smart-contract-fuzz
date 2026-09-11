# B5-6 Adapted Real-Source Analysis Summary

## Result overview

B5-5R is complete and parseable as **adapted real-source evidence**: **120/120 result records** are preserved against the B5-4 frozen registry. All 120 rows have complete artifacts and passing checksums. The batch contains 79 falsified, 1 budget_exhausted, and 40 compile_error rows. The 40 compile_error rows are excluded from comparative outcomes. budget_exhausted is right-censored and is not a safety or pass result.

No new formal fuzzing was run. No historical evidence was modified. exercise2 was not executed.

## Main usable findings

- The two Echidna-origin candidates, b5-rs-echidna-flags and b5-rs-echidna-multi, form the full comparable real-source candidate set. Each has all three methods represented without compile_error.
- Full-K1 and Full-K5 retain observed property-violation capability on this adapted Echidna-origin subset. This is a capability statement, not an ecosystem-wide superiority claim.
- For the full batch, calls-to-failure median/mean are 2/2.57 and sequence-length median/mean are 2/2.57, over n=79 falsified rows. These are descriptive metrics.
- SmartBugs Original contributes 20 falsified rows that demonstrate execution and an observable property violation in adapted sources. They are Original-only descriptive evidence.

## Comparable and non-comparable subsets

### Comparable Echidna-origin subset

The two Echidna-origin candidates contain 60 rows: 59 falsified and 1 right-censored. Compare methods only within these same candidates, properties, budgets, and execution model. Do not compare Original and Harness as semantically equivalent transactions.

### SmartBugs Original-only subset

The 20 SmartBugs Original falsified rows support the statement that adapted SmartBugs targets can run and expose observed violations. They do not support Harness performance or failure-rate claims.

### Engineering limitation subset

The SmartBugs Full-K1/Full-K5 configurations contain **40 compile_error rows**. These are engineering limitations in the cross-version Harness generation/import path under Solidity 0.4.25. They are not detection failures, performance results, or negative discovery-rate outcomes.

## Paper-ready claims

1. In two Echidna-origin adapted real-source candidates, Full-K1 and Full-K5 maintained the ability to expose observed property violations under the declared adapted execution model.
2. Calls-to-failure and sequence-length can be reported as descriptive discovery-trace metrics for falsified rows.
3. SmartBugs Original rows show that the adapted SmartBugs targets were executable and that their properties could be observed as violated under Original.
4. The SmartBugs Harness compile_error records identify a Solidity 0.4.25 cross-version import/generation limitation that should be reported as a threat to validity.

## Prohibited claims

- Do not claim superiority over a baseline on all real contracts or across the ecosystem.
- Do not claim that SmartBugs Harness has a low failure-discovery rate.
- Do not treat compile_error as a method detection failure.
- Do not treat budget_exhausted as safe, passed, or vulnerability-free.
- Do not claim Original and Harness semantic equivalence.
- Do not claim speedup from Total calls. At most report descriptive calls-to-failure differences within the same candidate, property, and execution-model boundary.

## Threats to validity

- The real-source pool is small and adapted, so it does not represent the full smart-contract ecosystem.
- Source and property adaptations may affect execution and must remain disclosed.
- Original uses multi-transaction execution while the generated Harness uses its own wrapper execution model; caller identity, transaction atomicity, and rollback boundaries can differ.
- The 40 SmartBugs Harness compile_error rows reduce the comparative Harness evidence and indicate a cross-version engineering limitation.
- The single budget_exhausted row is right-censored. It does not support a safety conclusion.
- Calls, fuzz seconds, and wall seconds are descriptive observations under this execution model, not normalized work or speedup measurements.
- Seed-level rows are repeated runs over a small candidate pool, not independent ecosystem contracts.

## Recommended next decision

Decision: GO_TO_B5_7_PAPER_INTEGRATION

This decision is appropriate because the analysis is complete and can strengthen the paper when all evidence boundaries above are preserved.
