# B4 V1 Public Supported 10-Seed Main Results

## Overall result

- Expected and audited runs: 120 / 120.
- Status counts: falsified=118; budget_exhausted=2; startup_error=0; unknown_error=0; incomplete=0.
- Checksum: 120/120 passed.
- Parser/status mismatches: 0.
- Main-table eligibility: conditional.

budget_exhausted means no observed counterexample within the declared budget. It is not a property pass or contract-safety result.

## By benchmark and method

| benchmark | method | runs | falsified | budget_exhausted | falsification rate | usable |
|---|---|---:|---:|---:|---:|---|
| echidna-flags | Original | 10 | 10 | 0 | 1.000000 | conditional |
| echidna-flags | Full-K1 | 10 | 10 | 0 | 1.000000 | conditional |
| echidna-flags | Full-K5 | 10 | 10 | 0 | 1.000000 | conditional |
| echidna-multi | Original | 10 | 9 | 1 | 0.900000 | conditional |
| echidna-multi | Full-K1 | 10 | 10 | 0 | 1.000000 | conditional |
| echidna-multi | Full-K5 | 10 | 9 | 1 | 0.900000 | conditional |
| smartbugs-multifunc | Original | 10 | 10 | 0 | 1.000000 | conditional |
| smartbugs-multifunc | Full-K1 | 10 | 10 | 0 | 1.000000 | conditional |
| smartbugs-multifunc | Full-K5 | 10 | 10 | 0 | 1.000000 | conditional |
| smartbugs-onefunc | Original | 10 | 10 | 0 | 1.000000 | conditional |
| smartbugs-onefunc | Full-K1 | 10 | 10 | 0 | 1.000000 | conditional |
| smartbugs-onefunc | Full-K5 | 10 | 10 | 0 | 1.000000 | conditional |

## Audit exceptions

- b4-echidna-multi-original-s1: no observed counterexample within the declared budget
- b4-echidna-multi-full-k5-s7: no observed counterexample within the declared budget; Harness wrapper execution model; not equivalent to Original

## Interpretation limits

- Harness falsified means a counterexample under the generated wrapper execution model; it does not establish semantic equivalence with Original independent multi-transaction execution.
- Original and Harness Total calls are not used to claim speedup or equal work.
- These are descriptive results for the four preregistered supported public benchmarks, not broad superiority over Echidna, SMARTIAN, MuFuzz, or IR-Fuzz.
- exercise2-access-control and PUB06/PUB07/PUB08 are not included.

## Next step

The tables may enter C-stage paper result organization only after manual review of run-level evidence and semantic caveats. Broader benchmarks or conditional replay are separate experiments.
