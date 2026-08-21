# C-1 公开基准统计报告

## 1. 数据与实验单位

本报告基于 5 个公开基准、3 种方法、每组 30 个相同 seed，共 450 次有效运行。统计事件定义为 `status=falsified`；`budget_exhausted` 是右删失，表示在当前 `testLimit` 预算内未发现反例，不表示性质通过或合约安全。实验单位是单个 benchmark/method/seed 运行。

## 2. 成功率与 95% Wilson 区间

| 基准 | 方法 | falsified/runs | 成功率 | Wilson 95% CI |
|---|---|---:|---:|---:|
| echidna-flags | original | 30/30 | 1.0000 | [0.8865, 1.0000] |
| echidna-flags | full-k1 | 30/30 | 1.0000 | [0.8865, 1.0000] |
| echidna-flags | full-k5 | 30/30 | 1.0000 | [0.8865, 1.0000] |
| echidna-multi | original | 24/30 | 0.8000 | [0.6269, 0.9049] |
| echidna-multi | full-k1 | 30/30 | 1.0000 | [0.8865, 1.0000] |
| echidna-multi | full-k5 | 29/30 | 0.9667 | [0.8333, 0.9941] |
| exercise2-access-control | original | 30/30 | 1.0000 | [0.8865, 1.0000] |
| exercise2-access-control | full-k1 | 0/30 | 0.0000 | [0.0000, 0.1135] |
| exercise2-access-control | full-k5 | 30/30 | 1.0000 | [0.8865, 1.0000] |
| smartbugs-multifunc | original | 30/30 | 1.0000 | [0.8865, 1.0000] |
| smartbugs-multifunc | full-k1 | 30/30 | 1.0000 | [0.8865, 1.0000] |
| smartbugs-multifunc | full-k5 | 30/30 | 1.0000 | [0.8865, 1.0000] |
| smartbugs-onefunc | original | 30/30 | 1.0000 | [0.8865, 1.0000] |
| smartbugs-onefunc | full-k1 | 30/30 | 1.0000 | [0.8865, 1.0000] |
| smartbugs-onefunc | full-k5 | 30/30 | 1.0000 | [0.8865, 1.0000] |

## 3. 每基准的方法比较

配对 exact McNemar 利用相同 seed 标签，是主要比较；Fisher 精确检验作为不使用配对关系的敏感性分析。不同 ABI 和动作空间下，同一 seed 不保证形成相同随机轨迹，因此配对强度不应被夸大。Primary family 预先包含 Full-K1/Original 与 Full-K5/Original 的 10 项比较；Exploratory family 包含 K1/K5 的 5 项比较，分别执行 Holm 校正。

| 基准 | 比较 | 成功率差 | Fisher p | McNemar p | Holm p | family |
|---|---|---:|---:|---:|---:|---|
| echidna-flags | full-k1 vs original | 0.0000 | 1 | 1 | 1 | Primary |
| echidna-flags | full-k5 vs original | 0.0000 | 1 | 1 | 1 | Primary |
| echidna-flags | full-k1 vs full-k5 | 0.0000 | 1 | 1 | 1 | Exploratory |
| echidna-multi | full-k1 vs original | 0.2000 | 0.02372 | 0.03125 | 0.2812 | Primary |
| echidna-multi | full-k5 vs original | 0.1667 | 0.1028 | 0.125 | 1 | Primary |
| echidna-multi | full-k1 vs full-k5 | 0.0333 | 1 | 1 | 1 | Exploratory |
| exercise2-access-control | full-k1 vs original | -1.0000 | 1.691e-17 | 1.863e-09 | 1.863e-08 | Primary |
| exercise2-access-control | full-k5 vs original | 0.0000 | 1 | 1 | 1 | Primary |
| exercise2-access-control | full-k1 vs full-k5 | -1.0000 | 1.691e-17 | 1.863e-09 | 9.313e-09 | Exploratory |
| smartbugs-multifunc | full-k1 vs original | 0.0000 | 1 | 1 | 1 | Primary |
| smartbugs-multifunc | full-k5 vs original | 0.0000 | 1 | 1 | 1 | Primary |
| smartbugs-multifunc | full-k1 vs full-k5 | 0.0000 | 1 | 1 | 1 | Exploratory |
| smartbugs-onefunc | full-k1 vs original | 0.0000 | 1 | 1 | 1 | Primary |
| smartbugs-onefunc | full-k5 vs original | 0.0000 | 1 | 1 | 1 | Primary |
| smartbugs-onefunc | full-k1 vs full-k5 | 0.0000 | 1 | 1 | 1 | Exploratory |

## 4. 右删失、Kaplan–Meier 与 log-rank

`duration=fuzz_seconds`；只有 falsified 是事件，budget_exhausted/passed 均为右删失。所有 37 个预算耗尽样本都保留在风险集中，没有只比较成功样本平均时间。实验主要截止机制是 `testLimit`，并非各组统一的固定墙钟截止；因此 fuzz_seconds 是本实验的操作性时间到反例指标。

| 基准 | 方法 | events/censored | KM 中位时间 | 成功样本描述性中位数 | 最大观察时间 |
|---|---|---:|---:|---:|---:|
| echidna-flags | original | 30/0 | 0.6 | 0.62 | 2.49 |
| echidna-flags | full-k1 | 30/0 | 0.56 | 0.585 | 1.42 |
| echidna-flags | full-k5 | 30/0 | 0.59 | 0.58 | 1.42 |
| echidna-multi | original | 24/6 | 2.91 | 1.585 | 5.94 |
| echidna-multi | full-k1 | 30/0 | 3.4 | 3.2 | 8.21 |
| echidna-multi | full-k5 | 29/1 | 5.77 | 5.44 | 11.64 |
| exercise2-access-control | original | 30/0 | 0.44 | 0.44 | 0.46 |
| exercise2-access-control | full-k1 | 0/30 | 未达到 | 未达到 | 14.47 |
| exercise2-access-control | full-k5 | 30/0 | 0.45 | 0.45 | 0.48 |
| smartbugs-multifunc | original | 30/0 | 0.45 | 0.45 | 0.59 |
| smartbugs-multifunc | full-k1 | 30/0 | 0.46 | 0.46 | 0.54 |
| smartbugs-multifunc | full-k5 | 30/0 | 0.46 | 0.46 | 0.55 |
| smartbugs-onefunc | original | 30/0 | 0.45 | 0.45 | 0.54 |
| smartbugs-onefunc | full-k1 | 30/0 | 0.46 | 0.46 | 0.47 |
| smartbugs-onefunc | full-k5 | 30/0 | 0.46 | 0.46 | 0.51 |

log-rank 同样按 Primary/Exploratory family 分别 Holm 校正：

| 基准 | 比较 | log-rank χ² | 未校正 p | Holm p | family |
|---|---|---:|---:|---:|---|
| echidna-flags | full-k1 vs original | 1.293 | 0.2555 | 0.6312 | Primary |
| echidna-flags | full-k5 vs original | 1.569 | 0.2104 | 0.6312 | Primary |
| echidna-flags | full-k1 vs full-k5 | 0.00909 | 0.924 | 0.924 | Exploratory |
| echidna-multi | full-k1 vs original | 0.4101 | 0.5219 | 0.6312 | Primary |
| echidna-multi | full-k5 vs original | 9.521 | 0.002031 | 0.014 | Primary |
| echidna-multi | full-k1 vs full-k5 | 11.02 | 0.0009028 | 0.003611 | Exploratory |
| exercise2-access-control | full-k1 vs original | 65.31 | 6.403e-16 | 6.403e-15 | Primary |
| exercise2-access-control | full-k5 vs original | 13.08 | 0.0002989 | 0.002391 | Primary |
| exercise2-access-control | full-k1 vs full-k5 | 66.35 | 3.768e-16 | 1.884e-15 | Exploratory |
| smartbugs-multifunc | full-k1 vs original | 9.549 | 0.002 | 0.014 | Primary |
| smartbugs-multifunc | full-k5 vs original | 15.5 | 8.237e-05 | 0.0007414 | Primary |
| smartbugs-multifunc | full-k1 vs full-k5 | 2.383 | 0.1227 | 0.368 | Exploratory |
| smartbugs-onefunc | full-k1 vs original | 5.656 | 0.0174 | 0.06958 | Primary |
| smartbugs-onefunc | full-k5 vs original | 6.469 | 0.01098 | 0.05489 | Primary |
| smartbugs-onefunc | full-k1 vs full-k5 | 1.065 | 0.302 | 0.604 | Exploratory |

## 5. Top-K 敏感性

- exercise2-access-control 的有效最短路径 `Owner() -> resume()` 排名为 2。它不在 K1、在 K5；因此观察到 Full-K1 0/30、Full-K5 30/30。Top-1 的 `Owner() -> pause()` 不是已确认有效触发路径。
- smartbugs-multifunc 的最短路径 `init() -> run(uint256)` 排名为 3，不在 K1；但 K1 包含另一条经原始反例确认的有效路径 `init() -> run(uint256) -> run(uint256)`，所以 K1 仍为 30/30。
- echidna-multi 的 K5 为 29/30，仅 seed 7 在预算内未发现反例。单个右删失样本不足以断言 K5 系统性差于 K1。

## 6. 统计结果、效应大小与工程意义

成功率差是当前 30 个 seed 下的观察效应；检验 p 值描述与相应零假设的不相容程度；工程意义还取决于路径覆盖、动作空间和实际预算。三者不能互相替代。Original 与 Harness 的 ABI、调用者和原子执行边界不同，Harness 一次外层调用还可能封装多个目标调用。时间比较可描述实际工具运行表现，但不能解释为等量底层目标函数工作下的算法效率。

## 7. 当前证据支持的结论

- C-1 的 450 次运行中，Full-K5、Original、Full-K1 的描述性成功数分别为 149/150、144/150、120/150。
- exercise2 显示 Top-K 是否包含正确状态方向会实质影响有限预算结果。
- smartbugs-multifunc 显示精确最短路径缺失不等价于不存在其他有效触发路径。
- Kaplan–Meier 与 log-rank 分析保留了所有预算耗尽样本，避免了只分析成功样本造成的选择偏差。

## 8. 不能支持的结论

- 五个公开基准不足以支持普遍优越性或对任意智能合约的泛化结论。
- budget_exhausted 不能写成性质通过、漏洞不存在或合约安全。
- 不能由 echidna-multi 的一个 K5 预算耗尽样本断言 K5 系统性更差。
- 不能直接使用 Original 与 Harness 的 `Total calls` 宣称同等底层工作量下加速。
- 描述性 150 次汇总不能替代按基准分层的推断分析。

## 9. 推荐论文表述

> 在五个 C-1 公开基准、每组 30 个固定 seed 和 100000 次外层调用预算下，Full-K5、Original 与 Full-K1 分别在 149/150、144/150 与 120/150 次运行中发现反例。按基准报告的 Wilson 区间、配对 exact McNemar 检验以及含右删失的 Kaplan–Meier/log-rank 分析用于刻画该实验范围内的不确定性；这些结果不构成对更广泛合约总体的普遍优越性声明。

> 未发现反例的运行统一表述为预算耗尽，而非性质通过。由于 Original 与 Harness 的调用语义及每次外层调用包含的目标操作数不同，调用数和 fuzz_seconds 只用于描述实际工具运行表现，不解释为等量底层工作下的算法加速。

## 10. 统计限制

- 每个基准每种方法只有 30 次运行，极端比例的 Wilson 区间仍有不可忽略宽度。
- 基准数仅为 5，且性质结构存在明显异质性。
- 相同 seed 标签不保证不同 ABI 下的随机轨迹逐步配对。
- testLimit 是主要预算，而 fuzz_seconds 会受不同执行语义和每次调用成本影响。
- 已知触发路径集合来自当前人工审计，不是完整语义可达性证明。
- 总体汇总仅为描述性，不执行忽略基准异质性的 pooled 显著性检验。

## 附：总体描述性汇总

| 方法 | falsified/runs | pooled rate | macro rate | 30/30 基准数 | 有预算耗尽的基准数 |
|---|---:|---:|---:|---:|---:|
| original | 144/150 | 0.9600 | 0.9600 | 4 | 1 |
| full-k1 | 120/150 | 0.8000 | 0.8000 | 4 | 1 |
| full-k5 | 149/150 | 0.9933 | 0.9933 | 4 | 1 |
