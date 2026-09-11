# B5 Combination Effect Analysis

Formal commit: 13457133a43c52f0eafdb43cc576735ab6b2a632. Analysis is descriptive and scenario-stratified; no
pooled p-value is claimed. budget_exhausted is right-censored.

Single-component evidence:
- C1 property filtering: Full-K5 median candidate reduction ratio is 0.889.
- C2 bounded repeat: No-Repeat reachability is 0.000 versus Full-K5 1.000.
- C3 value evidence: No-Value median rank is 3.000 versus Full-K5 1.000.
- Top-K is reported as Full-K1 versus Full-K5 without assuming monotonic benefit.

Full PHS combination: SUPPORTED. The targeted contrasts jointly cover
candidate relevance, repeat-preserving reachability, and value-directed rank.
This supports a combination claim under the declared execution models, not
individual component novelty or Original/Harness semantic equivalence.

Safe wording: PHS combines property-directed filtering, bounded repeat,
lightweight value evidence, and interpretable Top-K retention in an auditable
Echidna-external Harness synthesis workflow, with scenario-specific gains.

Limitations: C1-C3 are controlled/custom; trigger outcomes may saturate.
Original uses independent transactions while Harness uses a wrapper transaction.
Total calls are not a speedup metric; public external validity is not
established by B5 alone.
