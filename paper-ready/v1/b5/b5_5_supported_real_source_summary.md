# B5-5 Supported Real-Source Summary

Status: BLOCKED_AFTER_PARTIAL_RUN

This is a partial execution report, not a completed real-source experiment.
The frozen B5-4 registry contains 120 supported adapted real-source rows. The
batch stopped at the first row after a runner configuration exception.

## Completeness

| Item | Count |
|---|---:|
| Frozen supported rows | 120 |
| Attempted rows | 1 |
| Preserved result rows | 1 |
| Completed fuzzing rows | 0 |
| Remaining rows | 119 |

## Candidate and method counts

| Candidate | Original | Full-K1 | Full-K5 | Total |
|---|---:|---:|---:|---:|
| b5-rs-echidna-flags | 1 | 0 | 0 | 1 |
| b5-rs-echidna-multi | 0 | 0 | 0 | 0 |
| b5-rs-smartbugs-multifunc | 0 | 0 | 0 | 0 |
| b5-rs-smartbugs-onefunc | 0 | 0 | 0 | 0 |

## Status counts

| Status | Count |
|---|---:|
| falsified | 0 |
| budget_exhausted | 0 |
| compile_error | 0 |
| tool_error | 1 |
| timeout | 0 |
| startup_error | 0 |
| parser_error | 0 |
| unknown_error | 0 |
| incomplete | 0 |

Calls-to-failure median/mean: not applicable; Echidna was not invoked.

## Interpretation boundary

The sole preserved row is a runner engineering failure:
UnboundLocalError because config_name was not initialized on the Original
branch. It is not a falsification, budget exhaustion, or property result.
The B5-5 result TSV retains the row with experiment_class=formal,
adapted_real_source_evidence in notes, paper_usable=false, and the original
artifact directory.

This phase did not modify B5-Min controlled/custom evidence, B4/B5-2/frozen
evidence, matched-random evidence, legacy evidence, B5-3R packets, or B5-4
gate artifacts. Exercise2 was not executed. No retry, seed replacement, or
formal rerun was performed.

Future budget_exhausted rows must be treated as right-censored: no
counterexample was observed within budget; this is not property passed or
safe. Original and Harness remain distinct execution models. Total calls
must not be used to claim speedup.

## Decision

Decision: BLOCKED_NEEDS_ENV_OR_RUNNER_FIX. A runner review/fix and a fresh
researcher-authorized start audit are required before any remaining formal
row can be executed. This partial artifact cannot support a comparative
adapted real-source claim.
