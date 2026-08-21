# Matched Random Top-K预注册报告

## 设计

- 候选池：V1 Full阶段保留的同一组路径；
- Top-K：1；
- 每个非退化目标计划运行：30个fuzz seed；
- 独立调度种子：20260805；
- 排列算法：SHA-256键排序与循环窗口，不依赖Python随机数实现；
- fuzz seed只决定Echidna随机过程，路径选择由预先冻结的调度表决定；
- 每个候选的入选次数最大差值不超过1。

该基线只隔离Full候选池内部的排序/Top-1选择效果，不评估Property或Repeat是否应把路径保留进候选池。

## 汇总

- 目标数：11；
- 非退化目标：9；
- 与Full完全相同而不运行的单候选目标：2；
- 计划随机基线运行：270；
- 入选平衡检查：PASS。

| cohort | benchmark | candidates | runs | min includes | max includes | full-rank1 includes | scope |
|---|---|---:|---:|---:|---:|---:|---|
| formal | branch-value | 7 | 30 | 4 | 5 | 4 | supported |
| formal | noisy-four-step | 3 | 30 | 10 | 10 | 10 | supported |
| formal | repeated-call | 3 | 30 | 10 | 10 | 10 | supported |
| formal | reset-example | 33 | 30 | 0 | 1 | 1 | supported |
| formal-b2 | alternative-path | 11 | 30 | 2 | 3 | 3 | supported |
| formal-b2 | multi-property | 5 | 30 | 6 | 6 | 6 | supported |
| public-c1 | echidna-flags | 1 | 0 | 0 | 0 | 0 | supported |
| public-c1 | echidna-multi | 2 | 30 | 15 | 15 | 15 | supported |
| public-c1 | exercise2-access-control | 2 | 30 | 15 | 15 | 15 | conditional |
| public-c1 | smartbugs-multifunc | 3 | 30 | 10 | 10 | 10 | supported |
| public-c1 | smartbugs-onefunc | 1 | 0 | 0 | 0 | 0 | supported |

## 分析边界

- path count为1的目标不运行random-K1，因为结果与Full-K1完全相同；
- exercise2仍是conditional，只能在调用者关系限制下解释；
- 计划运行前必须从调度表生成Harness并完成编译预检；
- 不得重新抽取一个对结果更有利的调度表；
- 该内部控制不能替代外部SOTA比较。
