# 04 控制实验与消融

## 主附录：matched-random

[`results/matched-random-v1/`](../../results/matched-random-v1/) 是同一 Full 候选池中的随机 Top-1 对照：随机 87/270，Full-K1 240/270，使用同 seed 配对。它能说明候选池内排序选择的作用，但不能替代外部 SOTA，也不能覆盖所有候选生成机制。

## 可条件使用的早期消融

以下材料可用于机制附录，但不能和 Formal 主批次按同名基准 pooled：

- [`results/ablation-k/`](../../results/ablation-k/)：Dependency Top-K；
- [`results/branch-value/`](../../results/branch-value/)：Value 和 Top-K；
- [`results/reset-example/`](../../results/reset-example/)：Reset 的早期 Top-K；
- [`results/repeated-call/repeat-ablation/`](../../results/repeated-call/repeat-ablation/)：重复访问次数；
- [`results/value-invariance/`](../../results/value-invariance/)：重命名和声明顺序稳健性；
- [`results/paper-data/noisy-four-step/`](../../results/paper-data/noisy-four-step/)：调用顺序 permutation 文件和已整理的机制对照。

每一项都要在图表中标注旧批次、seed 数、预算或环境快照限制。

## V2 单独存放

[`results/native-corpus-seed-fair/`](../../results/native-corpus-seed-fair/) 和 [`results/paper-data/v2-native-ablation-summary.csv`](../../results/paper-data/v2-native-ablation-summary.csv) 是 V2 原生多交易 seed 的独立研究线。neutral 与 violation-boundary 不能并入 V1 主结果；后者是 oracle-assisted 敏感性结果。
