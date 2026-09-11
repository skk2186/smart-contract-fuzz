# B5-5R Supported Real-Source Summary

Status: FORMAL_EXECUTION_COMPLETE

This is adapted real-source evidence under the B5-4 declared execution models. It is separate from B5-Min controlled/custom evidence and B4/B5-2/frozen/matched-random evidence.

- Batch run directory: work/v1-restart/b5-5r-formal-real-source-20260911-185330
- Frozen supported rows: 120
- Executed rows with preserved records: 120/120
- Exercise2 executed: NO
- B5-4 gate artifacts overwritten: NO
- Historical evidence modified: NO

## Candidate and method counts

| Candidate | Original | Full-K1 | Full-K5 | Total |
|---|---:|---:|---:|---:|
| b5-rs-echidna-flags | 10 | 10 | 10 | 30 |
| b5-rs-echidna-multi | 10 | 10 | 10 | 30 |
| b5-rs-smartbugs-multifunc | 10 | 10 | 10 | 30 |
| b5-rs-smartbugs-onefunc | 10 | 10 | 10 | 30 |

## Status counts

| Status | Count |
|---|---:|
| budget_exhausted | 1 |
| compile_error | 40 |
| falsified | 79 |
| incomplete | 0 |
| parser_error | 0 |
| startup_error | 0 |
| timeout | 0 |
| tool_error | 0 |
| unknown_error | 0 |

Successful discovery calls-to-failure summary: median=2; mean=2.56962; n=79.
Successful discovery sequence-length summary: median=2; mean=2.56962; n=79.

A falsified row records an observed violation under the declared model. A budget_exhausted row is right-censored: no counterexample was observed within budget; it is not property passed or safe.

Original and Harness are distinct execution models; no semantic equivalence is claimed. Total calls is not a speedup measure. Exercise2 is outside the supported pool.

The first B5-5R row is an explicitly labeled retry of the preserved B5-5 tool_error record; the B5-5 blocked artifact was not overwritten.

If complete and parseable, this batch can support separately labeled adapted real-source external-validity analysis for the four preregistered candidates. It does not establish ecosystem-wide superiority.

## B5-5R engineering note

The 40 compile_error rows are preserved engineering outcomes, not counterexample outcomes. They are concentrated in the SmartBugs Full-K1 and Full-K5 Harness configurations because the generated input used a relative import that the Solidity 0.4.25 compile invocation could not resolve.
These rows are not counted as falsified or budget_exhausted and are not paper-usable comparative outcomes.
