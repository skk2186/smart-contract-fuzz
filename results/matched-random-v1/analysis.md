# Matched-random Top-1 对 Full-K1 配对分析

> 事件定义：Echidna 在预算内报告目标属性 falsified；budget_exhausted 作为未发现事件保留。两组使用同一 benchmark、同一 fuzz seed，只有冻结的候选路径选择不同。

- 配对运行：270；
- matched-random：87/270 = 0.3222；
- Full-K1：240/270 = 0.8889；

| cohort | benchmark | runs | random | Full-K1 | random-only | Full-only | exact McNemar p |
|---|---|---:|---:|---:|---:|---:|---:|
| formal | branch-value | 30 | 4/30 | 30/30 | 0 | 26 | 2.9802e-08 |
| formal | noisy-four-step | 30 | 10/30 | 30/30 | 0 | 20 | 1.907349e-06 |
| formal | repeated-call | 30 | 10/30 | 30/30 | 0 | 20 | 1.907349e-06 |
| formal | reset-example | 30 | 1/30 | 30/30 | 0 | 29 | 3.725e-09 |
| formal-b2 | alternative-path | 30 | 6/30 | 30/30 | 0 | 24 | 1.19209e-07 |
| formal-b2 | multi-property | 30 | 6/30 | 30/30 | 0 | 24 | 1.19209e-07 |
| public-c1 | echidna-multi | 30 | 15/30 | 30/30 | 0 | 15 | 6.1035156e-05 |
| public-c1 | exercise2-access-control | 30 | 15/30 | 0/30 | 15 | 0 | 6.1035156e-05 |
| public-c1 | smartbugs-multifunc | 30 | 20/30 | 30/30 | 0 | 10 | 0.001953125 |

## 解释边界

这是一项候选池内部的因果控制，不是外部SOTA比较。它只评估在相同Full候选池中，将确定性Top-1替换为均衡随机Top-1的影响；不能据此宣称方法优于SMARTIAN、IR-Fuzz等外部工具。
