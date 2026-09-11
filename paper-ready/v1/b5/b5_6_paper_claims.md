# B5-6 Paper Claims and Threats to Validity

## Results statements suitable for the experimental-results section

1. B5-5R provides **adapted real-source evidence** with **120/120 result records** preserved against the B5-4 frozen registry.
2. On the two Echidna-origin candidates, b5-rs-echidna-flags and b5-rs-echidna-multi, Original, Full-K1, and Full-K5 all produced parseable non-compile-error records under the same declared adapted execution model.
3. Full-K1 and Full-K5 retained the ability to expose observed property violations on this comparable Echidna-origin subset.
4. Among the 79 falsified rows, calls-to-failure and sequence-length provide descriptive summaries of observed discovery traces; they are not direct measures of equal-work speedup.
5. The adapted SmartBugs Original configurations produced 20 falsified rows, showing that these adapted targets were executable and that property violations were observable under Original.
6. The B5-5R batch contains 79 falsified rows, 1 right-censored budget_exhausted row, and 40 preserved engineering compile_error rows.
7. The SmartBugs Full-K1 and Full-K5 compile_error records reveal a cross-version Harness generation/import limitation under Solidity 0.4.25.
8. The findings strengthen the description of V1 behavior on a small adapted real-source pool, while remaining limited to adapted real-source evidence.

## Statements suitable for Threats to Validity

1. The real-source pool contains four preregistered adapted candidates and should not be treated as representative of the smart-contract ecosystem.
2. Adaptation for compiler and property compatibility may alter source structure or execution details, so the results do not automatically transfer to unadapted contracts.
3. Original and Harness are different execution models. Caller identity, transaction atomicity, and rollback scope may differ, so semantic equivalence is not claimed.
4. The 40 SmartBugs Harness compile_error rows are excluded from comparative outcomes. They indicate an engineering limitation rather than a detection failure.
5. The one budget_exhausted row is right-censored. It records no observed violation within budget, not safety, property passage, or absence of a vulnerability.
6. Fuzz seconds, wall seconds, calls-to-failure, and sequence length are descriptive observations and do not by themselves establish speedup or equal-work efficiency.
7. Ten seeds per candidate-method cell provide repeated observations, but the independent unit for external validity is the candidate and property, not the row count alone.
8. SmartBugs Original-only results are not performance comparisons against Harness because the corresponding Harness rows are compile_error engineering outcomes.

## Conclusions that must not be used

- The method outperforms the baseline on all real contracts.
- SmartBugs Harness has a lower discovery rate.
- Compile_error means the method failed to detect the vulnerability.
- Budget_exhausted means the property passed or the contract is safe.
- Original and Harness are semantically equivalent.
- The method achieves speedup based on Total calls.
- These four adapted candidates establish ecosystem-wide superiority.
