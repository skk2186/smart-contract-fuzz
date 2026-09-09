# B5-1R3 Smoke Report

## SMOKE ONLY - NOT PAPER EVIDENCE

These runs validate environment, analyzer, Harness/observer generation, solc,
Echidna invocation, parser, metric extraction, artifact completeness, and
checksums. They are excluded from formal summaries and support no superiority,
speedup, significance, or semantic-equivalence claim.

Accepted required cells (seed=1, budget=100000):

| run_id | scenario | method | status | property | target | rank | top1/top5 | repeat/value | artifact/checksum |
|---|---|---|---|---|---|---|---|---|---|
| b5-smoke-c1-original-s1-r3-retry2 | C1 | Original | budget_exhausted | 0 | 0 | 1 | 1/1 | 0/0 | true/pass |
| b5-smoke-c1-full-k1-s1-r3 | C1 | Full-K1 | falsified | 1 | 1 | 1 | 1/1 | 1/1 | true/pass |
| b5-smoke-c2-original-s1-r3 | C2 | Original | falsified | 1 | 1 | blank | 0/0 | 0/0 | true/pass |
| b5-smoke-c2-full-k1-s1-r3 | C2 | Full-K1 | falsified | 1 | 1 | 1 | 1/1 | 3/1 | true/pass |
| b5-smoke-c3-original-s1-r3 | C3 | Original | falsified | 1 | 1 | 1 | 1/1 | 0/0 | true/pass |
| b5-smoke-c3-full-k1-s1-r3 | C3 | Full-K1 | falsified | 1 | 1 | 1 | 1/1 | 0/1 | true/pass |

All six accepted directories contain manifest, command, environment, generated,
raw, parsed, summary, status.env, checksums, and verification output. Manifest
and status use experiment_class=SMOKE_ONLY and paper_usable=false. Final metric
rows use the declared schema, artifact_complete=true, checksum_pass=pass.

C1 Original budget_exhausted means no counterexample was observed within the
declared budget; it is not a property pass, safety result, or PHS comparison.

## Retained engineering attempts

b5-smoke-c1-original-s1-r3 is retained as compile_error caused by the observer
absolute import rejected by solc. b5-smoke-c1-original-s1-r3-retry1 is retained
as budget_exhausted from a runner version that left metric finalization pending.
Neither is part of the accepted six-cell validation set; neither was deleted or
overwritten. The final accepted retry is ...-retry2.

The total invocation count is eight because two C1 Original engineering retries
are retained. This does not change the six-cell validation target or formal
denominator.

## Validation conclusions

Five accepted cells contain explicit property falsification markers and one is
right-censored. C2 Full-K1 selected candidates preserve advance() three times.
C3 uses storage route constants and require(route == 3), with no msg.value/payable.
These are pipeline observations only.
