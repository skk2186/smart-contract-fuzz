# 本地目标规模代理表

> 这是 11 个已冻结本地目标的源码/候选规模描述，不是大型真实合约的可扩展性证明。函数和状态变量数量来自保守正则/行级 proxy，不能替代 Solidity AST 统计。

- 目标：11；supported：10；conditional：1；
- 源码行数范围：32–79；
- retained path 数范围：1–33；

| cohort | benchmark | files | lines | functions | state proxy | retained paths | max sequence | semantic |
|---|---|---:|---:|---:|---:|---:|---:|---|
| formal | branch-value | 1 | 71 | 9 | 4 | 7 | 4 | supported |
| formal | noisy-four-step | 1 | 79 | 11 | 7 | 3 | 4 | supported |
| formal | repeated-call | 1 | 63 | 7 | 5 | 3 | 4 | supported |
| formal | reset-example | 1 | 79 | 10 | 4 | 33 | 4 | supported |
| formal-b2 | alternative-path | 1 | 43 | 6 | 2 | 11 | 4 | supported |
| formal-b2 | multi-property | 1 | 47 | 5 | 3 | 5 | 4 | supported |
| public-c1 | echidna-flags | 1 | 42 | 3 | 3 | 1 | 2 | supported |
| public-c1 | echidna-multi | 1 | 32 | 5 | 3 | 2 | 3 | supported |
| public-c1 | exercise2-access-control | 2 | 66 | 6 | 3 | 2 | 2 | conditional |
| public-c1 | smartbugs-multifunc | 1 | 36 | 3 | 2 | 3 | 3 | supported |
| public-c1 | smartbugs-onefunc | 1 | 33 | 2 | 2 | 1 | 2 | supported |

## 使用边界

该表可用于报告当前数据集的异质性和候选增长起点；不能外推到大型真实项目，也不能由路径数与源码行数的相关性自动推出 fuzzing 性能。后续取得更大公开任务后，应用 AST/Slither 统计替换 proxy，并把失败、超时和截断纳入分母。
