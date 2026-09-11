# B5-4 SmartBugs Property-Construction Review

Status: COMPLETED_FOR_PREREGISTRATION; FUTURE_EXECUTION_REQUIRES_PREFLIGHT

Source: smartbugs/smartbugs-curated at commit 230e649123477eff332742a59a1c7cc6dc286cab, Apache-2.0 archived. The two files are adapted public-dataset tasks and are not presented as untouched upstream artifacts.

## Multifunc

Original label: integer overflow/underflow in a feasible multi-transaction, multi-function task.

Adapted property: echidna_count_does_not_underflow() returns count <= 1. Initial count is 1; init() enables run(input), whose original unchecked Solidity 0.4.x subtraction wraps above 1 when decremented below zero. The oracle therefore observes the invariant corresponding to the label while preserving initialized, count, init, run and arithmetic.

## Onefunc

Original label: integer overflow/underflow in a feasible multi-transaction, one-function task.

Adapted property: echidna_count_does_not_underflow() returns count <= 1. The first run call sets initialized and returns; a later run(input) executes the original unchecked subtraction and can wrap count above 1. The adaptation adds the researcher-authored oracle and integration naming only.

For both candidates, the property is a researcher-authored oracle, not an upstream Echidna property. No known counterexample path is injected. The tasks can support adapted vulnerability-dataset applicability after compile/preflight review, not broad ecosystem coverage. Remaining limits are oracle validity, the 0.4.25 arithmetic dependency, local adaptation and wrapper transaction-atomicity.

