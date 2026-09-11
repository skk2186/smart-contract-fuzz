# B5-5 Decision

Decision: BLOCKED_NEEDS_ENV_OR_RUNNER_FIX

## Basis

The B5-4 supported registry was valid at 120 rows and the four approved
candidates were confirmed. The first formal row was attempted, but the
dedicated runner raised an UnboundLocalError before configuration completion
because config_name was not initialized in the Original branch. No Echidna
formal invocation or solc compilation occurred.

## Accounting

- Batch: work/v1-restart/b5-5-formal-real-source-20260911-151720/
- Attempted: 1/120
- Preserved result records: 1
- Remaining rows: 119
- Exercise2: not executed
- Original run-id: preserved; not retried and not overwritten

## Required resolution

Stop at this partial batch. A researcher must review the runner defect and
decide whether a separately tracked B5-5R runner fix is authorized. A future
restart must use the frozen B5-4 registry unchanged, preserve this original
tool_error row, use new retry identifiers where applicable, and repeat the
environment and artifact gates. No B5-6 analysis is authorized from this
partial result.
