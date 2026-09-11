# B5 Ceiling Effect Review

A 10/10 trigger count is reviewed separately from mechanism metrics.
## C1 Irrelevant-State Explosion

classification: not_fully_saturated

| Method | Falsified | Budget exhausted | Reachability | Median rank | Top-1 |
|---|---|---|---|---|---|
| Original | 5/10 | 5 | 8/10 | 1.000 | 10/10 |
| Dependency-only | 10/10 | 0 | 10/10 | 1.000 | 10/10 |
| Full-K1 | 10/10 | 0 | 10/10 | 1.000 | 10/10 |
| Full-K5 | 10/10 | 0 | 10/10 | 1.000 | 10/10 |

## C2 Deep Repeated Transition

classification: not_fully_saturated

| Method | Falsified | Budget exhausted | Reachability | Median rank | Top-1 |
|---|---|---|---|---|---|
| Original | 10/10 | 0 | 10/10 |  | 0/10 |
| No-Repeat | 0/10 | 10 | 0/10 |  | 0/10 |
| Full-K1 | 10/10 | 0 | 10/10 | 1.000 | 10/10 |
| Full-K5 | 10/10 | 0 | 10/10 | 1.000 | 10/10 |

## C3 Value-Gated Competing Paths

classification: trigger_ceiling_but_mechanism_discriminative

| Method | Falsified | Budget exhausted | Reachability | Median rank | Top-1 |
|---|---|---|---|---|---|
| Original | 10/10 | 0 | 10/10 | 1.000 | 10/10 |
| No-Value | 10/10 | 0 | 10/10 | 3.000 | 0/10 |
| Full-K1 | 10/10 | 0 | 10/10 | 1.000 | 10/10 |
| Full-K5 | 10/10 | 0 | 10/10 | 1.000 | 10/10 |

Conclusion: saturation is not called a failure when rank, Top-K, repeat, value, or reachability still distinguishes methods.
