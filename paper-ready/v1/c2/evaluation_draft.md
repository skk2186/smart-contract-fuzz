# 6 Evaluation（中文草稿）

## 6.1 评价目标与研究问题

本文将评价分为四个研究问题。

- **RQ1：** 属性定向的 sequence planning 能否生成预期的候选路径，并在受控障碍上体现 Property、Value、Repeat 与 Top-K 的机制作用？
- **RQ2：** 在声明的 wrapper execution model 下，自动生成的 Harness 能否完成公开属性任务的执行、解析和 provenance 留存？
- **RQ3：** 在预登记的 supported public tasks 上，Original、Full-K1 和 Full-K5 的观察结果如何？
- **RQ4：** 哪些语义边界限制了 Harness 结果的解释？

四个问题分别关注候选机制、运行链完整性、范围内描述性比较和执行模型边界。它们共同评价的是 Echidna 之前的 property-directed Harness synthesis preprocessing，而不是一个独立的通用模糊测试器。

## 6.2 实验对象与范围

机制评价使用 Formal controlled benchmarks。NoisyFourStep 用于观察无关路径和属性过滤，BranchValue 用于观察依赖相同但值方向不同的分支，RepeatedCall 用于观察必须重复访问的路径，ResetExample 用于观察 reset 干扰、同分候选和 Top-K 区分。四个合约是为特定障碍设计的 controlled benchmarks；它们有助于隔离组件作用，但不代表真实生态的规模、调用者或语义多样性。

公开评价只纳入四个预登记 supported public tasks：echidna-flags、echidna-multi、smartbugs-multifunc 和 smartbugs-onefunc。exercise2-access-control 依赖 msg.sender、owner equality、caller alternation 和 address-keyed mapping，保持 conditional，不进入 supported pooled 结果。alternative-path-internal、multi-property-internal 和 three-step-internal 是内部候选或受控材料，不是新增 public benchmark，也不进入分母。

公开比较使用三组方法：Original、Full-K1 和 Full-K5。每个任务使用 seed 1–10，每组 10 次运行，共 4 × 3 × 10 = 120 runs。Original 采用 public-c1-original.yaml，Harness 方法采用 public-c1-harness.yaml；记录的预算为 testLimit 100000、timeout 30 秒、workers 1、stopOnFail true、property mode。工具 provenance 中保留 Python 3.11.15、Slither 0.11.5、Echidna 2.3.2、相应 solc 0.8.20 或 0.4.25，以及方法版本 Full-v1.0.1-compat。

Original 的 seqLen=4 描述 Echidna 的多交易搜索，Harness 的 seqLen=1 描述一次外层 wrapper 调用；wrapper 内可以有多个目标函数调用。因此，seqLen 不是两种方法之间的等价交易长度，K1/K5 也不是 Original 中等价的交易数。

## 6.3 指标和审计规则

每次运行使用互斥状态分类。falsified 表示在声明的执行模型、输入和预算内观察到属性反例；budget_exhausted 表示在预算内没有观察到反例；startup_error、unknown_error 和 incomplete 分别表示启动、未知错误和不完整运行。按 benchmark 和 method 报告 runs、falsified、budget_exhausted 以及 observed falsification rate，后者定义为 falsified / runs。

该比率只是给定任务、配置和 seed 范围内的描述性比率，不是属性通过率、安全概率、无偏漏洞发现率或跨生态泛化估计。两个 budget_exhausted 运行必须保留并单独解释为“在声明预算内没有观察到反例”，不能写成 property passed、contract safe 或不存在漏洞。

运行链指标与安全语义指标分开。artifact set completeness、checksum pass 和 parser/status agreement 用于回答日志、解析和 provenance 是否完整；它们不能证明合约安全，也不能证明两个执行模型等价。本评价不使用 Original 与 Harness 的 Total calls 构造 speedup，因为两者处在不同的外层计数层次，不能视为等量工作。

## 6.4 RQ1：Formal controlled benchmarks 的机制证据

受控 Formal 结果支持对组件作用作范围内、可解释的判断。四个主要受控基准的候选路径从 Dependency 阶段合计 92 条降至 Property 阶段 31 条，减少 61 条，即 66.30%。NoisyFourStep 的候选从 30 条降至 3 条，并将目标路径变为唯一的 Top-1。这说明从属性读取状态反向过滤候选，能够去除一部分明显无关路径；它不说明候选减少必然带来端到端 fuzzing 加速。

组件对照呈现出与障碍相符的方向性。BranchValue 中，Property-K1 为 0/30，而加入值方向证据后的 Value-K1 与 Full-K1 均为 30/30，说明单纯变量相关性可能不足以区分写入方向。RepeatedCall 中，不允许重复访问的配置为 0/30，完整方法为 30/30，说明在该受控目标中，禁止重复会漏掉所需路径。有界重复允许候选包含同一函数的有限次访问，但不意味着所有任务都需要同样的展开上限。

ResetExample 展示了另一个排序问题：重复扩展和 reset 干扰会增大同分候选集合，单靠显示排名不能把“建立状态后正确使用”的路径与“建立后又被清除”的路径区分开；值证据可以提供额外的局部判断。上述结果是为特定障碍设计的机制证据，不能被写成真实合约总体的有效率、工具级优越性或速度证明。

## 6.5 RQ2：公开 Harness 运行链的完整性

四个 supported public tasks 的 120 个预登记运行全部完成。每个运行均保留 manifest、command、environment、raw、parsed、summary、status 和 checksum 产物，artifact set completeness 为 120/120，checksum pass 为 120/120，parser/status mismatch 为 0；startup_error、unknown_error 和 incomplete 均为 0。这些结果说明，在声明配置和当前 wrapper execution model 下，生成、编译、运行、解析、状态分类和 provenance 链条完整可审计。

这里的“完成”只描述运行链。它不等于完整 native EVM replay，不等于 Original/Harness 语义等价，也不等于属性通过或合约安全。B2 的 static_gate_pass 同样只是静态适用性门，不是 native replay 结果。主表中的 main_table_usable 仍全部为 conditional，因为完整产物不能消除 caller、transaction atomicity、rollback 和其他环境语义风险。

## 6.6 RQ3：Original、Full-K1 与 Full-K5 的描述性结果

四个任务、三种方法和 10 个 seed 的结果如下。表中的 falsified 表示在相应执行模型下观察到反例，budget exhausted 表示在预算内没有观察到反例。

| Benchmark | Method | Runs | Falsified | Budget exhausted | Observed rate |
|---|---|---:|---:|---:|---:|
| echidna-flags | Original | 10 | 10 | 0 | 1.000000 |
| echidna-flags | Full-K1 | 10 | 10 | 0 | 1.000000 |
| echidna-flags | Full-K5 | 10 | 10 | 0 | 1.000000 |
| echidna-multi | Original | 10 | 9 | 1 | 0.900000 |
| echidna-multi | Full-K1 | 10 | 10 | 0 | 1.000000 |
| echidna-multi | Full-K5 | 10 | 9 | 1 | 0.900000 |
| smartbugs-multifunc | Original | 10 | 10 | 0 | 1.000000 |
| smartbugs-multifunc | Full-K1 | 10 | 10 | 0 | 1.000000 |
| smartbugs-multifunc | Full-K5 | 10 | 10 | 0 | 1.000000 |
| smartbugs-onefunc | Original | 10 | 10 | 0 | 1.000000 |
| smartbugs-onefunc | Full-K1 | 10 | 10 | 0 | 1.000000 |
| smartbugs-onefunc | Full-K5 | 10 | 10 | 0 | 1.000000 |

总体上，120 个运行中有 118 个 falsified、2 个 budget_exhausted。两个预算耗尽运行分别是 b4-echidna-multi-original-s1 和 b4-echidna-multi-full-k5-s7。前者表示 Original 在该 seed 和预算内没有观察到反例，后者表示 Full-K5 在 wrapper 执行模型下没有观察到反例；二者都不能写成属性通过。四个任务中，echidna-flags 的三种方法均为 10/10，smartbugs-multifunc 和 smartbugs-onefunc 的三种方法也均为 10/10；差异只出现在 echidna-multi 的观察状态上。

因此，本文只把该表作为四任务、seed 1–10 范围内的 descriptive comparison。可以说 Full-K1 和 Full-K5 在多数任务组中观察到 falsified，也可以报告 echidna-multi 的三组计数不同；但这些差异没有被解释为显著性、superiority、稳定性或速度优势。本文不报告 p-value，也不使用 Total calls 作为 speedup 证据。四个任务数量少，每组只有 10 个 seed，且 Original 与 Harness 的执行语义不同，均限制了比较的解释范围。

## 6.7 RQ4：语义边界与结果解释

Original 是多笔独立交易。sender 可能随外层交易变化，某笔交易失败通常只回滚该笔交易，交易之间的区块环境和 msg.value 也可能不同。Harness 则在一次外层 wrapper 调用中按固定候选顺序连续调用目标函数，目标函数通常看到同一个 Harness caller，多个调用可能处于同一 transaction atomicity；中间一步 revert 可能导致整个 wrapper 回滚。当前生成器也没有通用的逐步 value 或不同 sender 模拟。

这些差异影响 access control、owner、address-keyed mapping、跨交易提交、失败前缀、时间锁、external call 和 reentrancy 等语义。exercise2-access-control 正因为依赖 msg.sender、owner equality、caller alternation 和按地址索引的 balances mapping，仍为 conditional，不能与四个 supported tasks pooled。B2 的 static_gate_pass 是静态 gate，不应写成完整 native EVM replay。固定成功路径的 11/11 最终属性相关状态一致，即使作为窄范围复核，也不能证明完整随机搜索过程、sender 搜索、失败前缀和 rollback scope 等价。

## 6.8 结果边界与小结

本评价支持以下窄结论：V1 能在受控 Formal benchmarks 上生成可检查的属性定向候选路径，并观察到 Property、Value、Repeat 和 Top-K 对预先声明障碍的方向性作用；在四个预登记 supported public tasks 上，三种配置均完成了 120 个运行的可审计描述性比较；运行链具有完整的 artifact 和 checksum provenance。

本评价不支持 Full-K1/Full-K5 显著优于 Original，不支持 Total calls speedup，不支持 Harness 与 Original 完全等价，不支持 budget_exhausted 等于属性通过或合约安全，不支持四个任务代表真实生态，也不支持 V1 普遍优于 Echidna、SMARTIAN、MuFuzz 或 IR-Fuzz。exercise2-access-control、内部 excluded tasks 和 matched-random-v1 不进入该 supported pooled 表。后者 provenance unresolved，只能继续 quarantine。
