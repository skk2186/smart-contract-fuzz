# B5 Paper Tables

## Table B5-1. Formal execution completeness
| Metric | Count |
|---|---|
| Expected | 120 |
| Observed expected dirs | 120 |
| Parsed | 120 |
| Derived paper-usable | 120 |
| Artifact complete | 120 |
| Checksum pass | 120 |
| Falsified | 105 |
| Budget exhausted | 15 |
| Compile error | 0 |
| Startup error | 0 |
| Parser error | 0 |
| Unknown error | 0 |
| Incomplete | 0 |

## Table B5-2. Scenario x method outcome
| Scenario | Method | Runs | Falsified | Budget exhausted | Reachability | Median rank | Top-1 | Top-5 |
|---|---|---|---|---|---|---|---|---|
| C1 Irrelevant-State Explosion | Original | 10 | 5/10 | 5 | 8/10 | 1.000 | 10/10 | 10/10 |
| C1 Irrelevant-State Explosion | Dependency-only | 10 | 10/10 | 0 | 10/10 | 1.000 | 10/10 | 10/10 |
| C1 Irrelevant-State Explosion | Full-K1 | 10 | 10/10 | 0 | 10/10 | 1.000 | 10/10 | 10/10 |
| C1 Irrelevant-State Explosion | Full-K5 | 10 | 10/10 | 0 | 10/10 | 1.000 | 10/10 | 10/10 |
| C2 Deep Repeated Transition | Original | 10 | 10/10 | 0 | 10/10 |  | 0/10 | 0/10 |
| C2 Deep Repeated Transition | No-Repeat | 10 | 0/10 | 10 | 0/10 |  | 0/10 | 0/10 |
| C2 Deep Repeated Transition | Full-K1 | 10 | 10/10 | 0 | 10/10 | 1.000 | 10/10 | 10/10 |
| C2 Deep Repeated Transition | Full-K5 | 10 | 10/10 | 0 | 10/10 | 1.000 | 10/10 | 10/10 |
| C3 Value-Gated Competing Paths | Original | 10 | 10/10 | 0 | 10/10 | 1.000 | 10/10 | 10/10 |
| C3 Value-Gated Competing Paths | No-Value | 10 | 10/10 | 0 | 10/10 | 3.000 | 0/10 | 10/10 |
| C3 Value-Gated Competing Paths | Full-K1 | 10 | 10/10 | 0 | 10/10 | 1.000 | 10/10 | 10/10 |
| C3 Value-Gated Competing Paths | Full-K5 | 10 | 10/10 | 0 | 10/10 | 1.000 | 10/10 | 10/10 |

## Table B5-3. Mechanism and ablation result
| Scenario | Comparison | Method | Dependency median | Property median | Reduction | Repeat observed | Rank | Reachability | Falsified |
|---|---|---|---|---|---|---|---|---|---|
| C1 Irrelevant-State Explosion | Dependency-only vs Full-K5 | Dependency-only | 36.000 | 4.000 | 0.889 |  | 1.000 | 1.000 | 10/10 |
| C1 Irrelevant-State Explosion | Dependency-only vs Full-K5 | Full-K5 | 36.000 | 4.000 | 0.889 |  | 1.000 | 1.000 | 10/10 |
| C1 Irrelevant-State Explosion | Dependency-only vs Full-K5 | Original | 36.000 | 4.000 | 0.889 |  | 1.000 | 0.800 | 5/10 |
| C1 Irrelevant-State Explosion | Full-K1 vs Full-K5 | Full-K1 | 36.000 | 4.000 | 0.889 |  | 1.000 | 1.000 | 10/10 |
| C2 Deep Repeated Transition | No-Repeat vs Full-K5 | No-Repeat | 12.000 | 3.000 | 0.750 | 1.000 |  | 0.000 | 0/10 |
| C2 Deep Repeated Transition | No-Repeat vs Full-K5 | Full-K5 | 12.000 | 3.000 | 0.750 | 3.000 | 1.000 | 1.000 | 10/10 |
| C2 Deep Repeated Transition | No-Repeat vs Full-K5 | Original | 12.000 | 3.000 | 0.750 | 1.000 |  | 1.000 | 10/10 |
| C2 Deep Repeated Transition | Full-K1 vs Full-K5 | Full-K1 | 12.000 | 3.000 | 0.750 | 3.000 | 1.000 | 1.000 | 10/10 |
| C3 Value-Gated Competing Paths | No-Value vs Full-K5 | No-Value | 21.000 | 5.000 | 0.762 |  | 3.000 | 1.000 | 10/10 |
| C3 Value-Gated Competing Paths | No-Value vs Full-K5 | Full-K5 | 21.000 | 5.000 | 0.762 |  | 1.000 | 1.000 | 10/10 |
| C3 Value-Gated Competing Paths | No-Value vs Full-K5 | Original | 21.000 | 5.000 | 0.762 |  | 1.000 | 1.000 | 10/10 |
| C3 Value-Gated Competing Paths | Full-K1 vs Full-K5 | Full-K1 | 21.000 | 5.000 | 0.762 |  | 1.000 | 1.000 | 10/10 |

## Table B5-4. Target rank, Top-K, and reachability
| Scenario | Method | Median target rank | Rank range | Top-1 | Top-5 | Reachability |
|---|---|---|---|---|---|---|
| C1 Irrelevant-State Explosion | Original | 1.000 | 1-1 | 10/10 | 10/10 | 8/10 |
| C1 Irrelevant-State Explosion | Dependency-only | 1.000 | 1-1 | 10/10 | 10/10 | 10/10 |
| C1 Irrelevant-State Explosion | Full-K1 | 1.000 | 1-1 | 10/10 | 10/10 | 10/10 |
| C1 Irrelevant-State Explosion | Full-K5 | 1.000 | 1-1 | 10/10 | 10/10 | 10/10 |
| C2 Deep Repeated Transition | Original |  |  | 0/10 | 0/10 | 10/10 |
| C2 Deep Repeated Transition | No-Repeat |  |  | 0/10 | 0/10 | 0/10 |
| C2 Deep Repeated Transition | Full-K1 | 1.000 | 1-1 | 10/10 | 10/10 | 10/10 |
| C2 Deep Repeated Transition | Full-K5 | 1.000 | 1-1 | 10/10 | 10/10 | 10/10 |
| C3 Value-Gated Competing Paths | Original | 1.000 | 1-1 | 10/10 | 10/10 | 10/10 |
| C3 Value-Gated Competing Paths | No-Value | 3.000 | 3-3 | 0/10 | 10/10 | 10/10 |
| C3 Value-Gated Competing Paths | Full-K1 | 1.000 | 1-1 | 10/10 | 10/10 | 10/10 |
| C3 Value-Gated Competing Paths | Full-K5 | 1.000 | 1-1 | 10/10 | 10/10 | 10/10 |

Notes: budget_exhausted is right-censored, not a pass or safety result.
Original/Harness use their declared execution models; total calls are not used
as speedup.
