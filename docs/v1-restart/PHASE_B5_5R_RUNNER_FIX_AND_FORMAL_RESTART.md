# PHASE B5-5R Runner Fix and Formal Restart

Status: PASS (120/120 frozen rows executed and recorded; engineering failures preserved)
Stage: B5-5R Runner Fix + Formal Real-Source Restart
Starting branch: develop
Starting HEAD: 0c07953da45ff2ceedff802260a4c679a071936c
Formal batch Git commit record: work/v1-restart/b5-5r-formal-real-source-20260911-185330/raw/git_commit.txt

## Scope and input

The frozen input was `paper-ready/v1/b5/b5_4_expected_real_source_runs.tsv`. The runner accepted 120 non-empty supported rows, with exactly the four approved candidates, three methods (Original, Full-K1, Full-K5), seeds 1..10, and the preregistered budget `testLimit=100000;timeout=30s;workers=1;stopOnFail=false`.

The new batch directory was:

`work/v1-restart/b5-5r-formal-real-source-20260911-185330/`

The batch was authorized only in the execution process with `B5_5_REAL_SOURCE_AUTHORIZED=1`. The authorization was not persisted in a shell profile. Exercise2 was not executed.

## Original B5-5 block and runner fix

The prior B5-5 attempt preserved one original `tool_error` row because `config_name` was not initialized on the Original branch before the shared config load. That original record remains in `paper-ready/v1/b5/b5_5_supported_real_source_results.tsv`.

B5-5R initializes `k, config_name = METHODS[method]` before the Original/ Harness branch split. The Full-K1 and Full-K5 top-k and Harness config selection logic remains unchanged. The runner also writes the B5-5R output paths supplied on the command line, emits `retry_of`, records start time, writes per-run `raw/commands.txt`, and records the actual Git commit in the batch artifact.

Before formal execution, the runner passed `py_compile`, dry-run configuration checks for Original/Full-K1/Full-K5, and the missing-authorization refusal check. After the first formal row began, the runner source was not modified.

## Execution and environment

Expected rows: 120
Executed rows with preserved result records: 120
Remaining rows: 0
Formal execution class: formal
Exercise2: NO
B5-5 blocked artifact overwritten: NO
B5-4 gate artifact overwritten: NO
B5-4 frozen registry modified: NO
B4/B5-2/B5-Min/frozen/matched-random/legacy evidence modified: NO
New source packet created: NO

Batch environment records are in `work/v1-restart/b5-5r-formal-real-source-20260911-185330/environment.txt`.

- Python: 3.11.15 at `/home/skk/miniconda3/envs/contract-fuzz/bin/python`
- Echidna: 2.3.2 at `/usr/local/bin/echidna`
- Echidna-source candidates used Solidity 0.8.20: `Version: 0.8.20+commit.a1b79de6.Linux.g++`
- SmartBugs candidates used Solidity 0.4.25: `Version: 0.4.25+commit.59dbf8f1.Linux.g++`
- Each run contains `raw/solc_version.txt`; the result table preserves the corresponding `solc_version` field.

## Result overview

| Candidate | Original | Full-K1 | Full-K5 | Total |
|---|---:|---:|---:|---:|
| b5-rs-echidna-flags | 10 falsified | 10 falsified | 10 falsified | 30 |
| b5-rs-echidna-multi | 10 falsified | 10 falsified | 9 falsified, 1 budget_exhausted | 30 |
| b5-rs-smartbugs-multifunc | 10 falsified | 10 compile_error | 10 compile_error | 30 |
| b5-rs-smartbugs-onefunc | 10 falsified | 10 compile_error | 10 compile_error | 30 |

| Status | Count |
|---|---:|
| falsified | 79 |
| budget_exhausted | 1 |
| compile_error | 40 |
| tool_error | 0 |
| timeout | 0 |
| parser_error | 0 |
| startup_error | 0 |
| unknown_error | 0 |
| incomplete | 0 |

All 120 run artifacts are marked artifact-complete and checksum-pass. The 40 compile errors are preserved engineering outcomes. They arose in the SmartBugs Full-K1/Full-K5 generated Harness compile invocation because the generated input used a relative import that Solidity 0.4.25 could not resolve. No post-start source or runner repair was applied.

For the 79 falsified rows with parsed failure traces, calls-to-failure has median 2 and mean 2.56962; sequence length has median 2 and mean 2.56962. These are within-model observed trace summaries, not a speedup claim.

## Relationship to prior evidence

B5-5R is separately labeled adapted real-source evidence. It does not replace or reinterpret B5-2/B5-Min controlled evidence, B4 evidence, or any frozen/matched-random evidence. The first B5-5R row is an explicitly labeled retry of the preserved B5-5 original tool_error; the old result file was not edited.

A `falsified` row records an observed property violation under the declared execution model. A `budget_exhausted` row is right-censored: no violation was observed within budget, and it is not a property pass or safety result. Original and Harness are distinct execution models; semantic equivalence is not claimed. Total calls is not used to claim speedup.

## Next step

The generated B5-5R result table and summary are ready for B5-6 real-source analysis, with the 40 SmartBugs Harness compile-error rows kept as a separate engineering limitation. Any future import-path or Harness repair must be a separately reviewed follow-up with a new batch identifier; it must not overwrite these records or silently convert them into formal outcomes.
