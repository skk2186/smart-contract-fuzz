# 03 公开基准 C-1

## 结果入口

- [`public-c1-group-summary.csv`](../../results/public-benchmarks/c1/public-c1-group-summary.csv)：五个公开目标的运行级总表。
- [`statistics/public-c1-statistical-report.md`](../../results/public-benchmarks/c1/statistics/public-c1-statistical-report.md)：Wilson 区间、配对比较、KM/log-rank 和限制。
- [`c1-path-preflight.csv`](../../results/public-benchmarks/c1/c1-path-preflight.csv)：已知有效路径是否进入 K1/K5。
- [`adaptations.md`](../../results/public-benchmarks/c1/adaptations.md)：公开案例适配说明。
- [`data-semantics.md`](../../results/public-benchmarks/c1/data-semantics.md)：指标和状态语义。

## 关键数字

| 方法 | 运行数 | 发现反例 |
|---|---:|---:|
| Original | 150 | 144 |
| Full-K1 | 150 | 120 |
| Full-K5 | 150 | 149 |

`exercise2-access-control` 是关键条件案例：Full-K1 为 0/30，而 Full-K5 为 30/30；该目标涉及 `msg.sender` 和 address-keyed mapping，应按 conditional 语义披露。五个公开目标不代表真实生态总体，不能写成普遍优于 Original。

## 不属于 C-1 正式分母的内容

`c0/`、`c0-before-compat-fixes/`、`smoke/` 和 `runner-output.log` 只用于筛查、启动或编排追踪；它们保留用于审计，但不进入论文主表。
