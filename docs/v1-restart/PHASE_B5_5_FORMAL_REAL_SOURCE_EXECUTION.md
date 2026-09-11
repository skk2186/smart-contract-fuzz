# PHASE B5-5 Formal Real-Source Execution

Status: BLOCKED_AFTER_PARTIAL_RUN

## Start and input gate

- Branch: develop
- Starting HEAD: 0b984586ebd6d61eceb262d9a32cb7a0e4c5566e
- Starting worktree audit: clean before creation of the B5-5 runner
- Frozen input: paper-ready/v1/b5/b5_4_expected_real_source_runs.tsv
- Expected supported rows: 120
- Actual registry data rows: 120
- Supported candidates: b5-rs-echidna-flags, b5-rs-echidna-multi, b5-rs-smartbugs-multifunc, b5-rs-smartbugs-onefunc
- Exercise2 in supported registry: NO

The initial branch, HEAD, clean-worktree, registry-count, candidate-set and
exercise2-exclusion checks passed. A dedicated B5-5 runner was then created
before formal execution and passed syntax/dry-run checks.

## Formal execution

Batch directory:

    work/v1-restart/b5-5-formal-real-source-20260911-151720/

The first preregistered row was attempted:

    b5-4-rs-b5-rs-echidna-flags-original-s1

The runner failed before Echidna invocation because the Original branch did not
initialize its config_name variable. This is recorded as tool_error in the
B5-5 result table and in the preserved run artifact. The original run-id was
not retried or overwritten. Formal execution stopped immediately; the runner
was not modified after the first formal attempt.

- Planned rows: 120
- Attempted rows: 1
- Completed fuzzing rows: 0
- Preserved result rows: 1
- Remaining registry rows: 119
- Echidna formal invocation: NO
- solc compilation: NO
- PHS preprocessing for row 1: reached before the configuration error
- Exercise2 execution: NO
- 30-seed expansion: NO

## Environment records

The batch raw artifact records:

- Python: Python 3.11.15
- Python path: /home/skk/miniconda3/envs/contract-fuzz/bin/python
- Active environment: contract-fuzz
- Echidna: Echidna 2.3.2 at /usr/local/bin/echidna
- Initial solc: 0.8.20
- First candidate solc probe: Version 0.8.20+commit.a1b79de6.Linux.g++

The required per-candidate solc probe was reached for the first candidate and
is stored at the run's raw/solc_version.txt. No 0.4.25 candidate was started.

## Evidence boundaries

This phase did not modify B4, B5-2, B5-Min, frozen, matched-random, legacy,
B5-3R provenance packets, or B5-4 gate artifacts. The new result table is
partial and must not be interpreted as a real-source performance result.
The only row is an engineering failure; no property outcome was observed.
budget_exhausted remains right-censored by policy and is not property passed
or safe. Original and Harness are not claimed semantically equivalent, and
Total calls is not a speedup measure.

## Decision and next step

Decision: BLOCKED_NEEDS_ENV_OR_RUNNER_FIX

The researcher must review the runner defect and authorize a separately
tracked B5-5R fix/restart decision. Any later retry must use a new retry id,
preserve this original tool_error row and artifact, and re-audit the frozen
120-row registry. No remaining row was silently substituted or removed.
