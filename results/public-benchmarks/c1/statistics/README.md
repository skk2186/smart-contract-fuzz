# C-1 statistical analysis

## Inputs

- `results/public-benchmarks/c1/parsed/echidna-flags.csv`
- `results/public-benchmarks/c1/parsed/echidna-multi.csv`
- `results/public-benchmarks/c1/parsed/exercise2-access-control.csv`
- `results/public-benchmarks/c1/parsed/smartbugs-multifunc.csv`
- `results/public-benchmarks/c1/parsed/smartbugs-onefunc.csv`
- `results/public-benchmarks/c1/public-c1-group-summary.csv`
- `results/public-benchmarks/c1/c1-path-preflight.csv`
- `results/public-benchmarks/c1/data-semantics.md`

The analysis validates exactly five benchmarks, three methods, 30 unique seeds per group, 450 rows, and the audited status totals before creating outputs.

## Outputs

- `success-rate-wilson.csv`: per-group success proportions and 95% Wilson intervals.
- `success-rate-pairwise.csv`: Fisher sensitivity analysis, paired exact McNemar tests, and Holm-adjusted McNemar p-values.
- `km-curves.csv`: Kaplan–Meier product-limit curves including right-censored runs.
- `time-to-falsification-summary.csv`: event/censor counts and KM/descriptive time summaries.
- `logrank-pairwise.csv`: two-sided log-rank tests and family-specific Holm adjustment.
- `overall-descriptive.csv`: descriptive totals only; no pooled significance test.
- `public-c1-statistical-report.md`: Chinese paper-oriented report.
- `input-checksums.sha256`: SHA-256 checksums of the inputs listed above.

## Definitions

- Success is `status=falsified`.
- Wilson intervals use the standard score interval with z=1.959963984540054.
- Fisher p-values sum fixed-margin tables with probability no greater than the observed table.
- Exact two-sided McNemar p-values use the binomial distribution of discordant seed pairs under p=0.5.
- Holm correction is applied separately to the predefined families: Primary has Full-K1 vs Original and Full-K5 vs Original across five benchmarks (10 tests); Exploratory has Full-K1 vs Full-K5 across five benchmarks (5 tests). Success-rate Holm values adjust McNemar p-values. Log-rank p-values are adjusted separately using the same family definitions.
- Kaplan–Meier uses `duration=fuzz_seconds`; only falsified runs are events. `budget_exhausted` and `passed` are right-censored.
- The two-sided log-rank test uses the usual observed-minus-expected statistic with the hypergeometric tie variance.

## Rebuild

```bash
python3 analyzer/analyze_public_c1_statistics.py \
  --input-dir results/public-benchmarks/c1/parsed \
  --output-dir results/public-benchmarks/c1/statistics
```

Generated with Python 3.14.6 using only the Python standard library; no external statistical dependency is required.

## Interpretation limits

The main experimental budget is `testLimit`, not a uniform wall-clock deadline. `fuzz_seconds` is an operational time-to-falsification measure. `Total calls` counts Echidna outer calls. Original uses `seqLen=4`; Harness uses `seqLen=1`, and one Harness call can bundle multiple target calls. Because their ABI, caller, atomicity, and target-call workload differ, calls and time describe observed tool performance rather than equal target-level algorithmic work. Overall 150-run rates are descriptive across five heterogeneous benchmarks and are not pooled inferential claims.
