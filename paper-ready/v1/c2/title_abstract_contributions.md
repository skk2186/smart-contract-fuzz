# 标题、摘要与贡献点候选

> 工作稿：用于人工修改。本文定位保持为面向既有属性模糊器的 Harness synthesis preprocessing，不将方法包装为新的通用模糊测试器。

## 一、中文标题候选

1. 面向属性模糊测试的智能合约交易序列 Harness 合成方法
2. 面向 Echidna 的属性定向交易序列 Harness 合成与语义边界审计
3. 面向有状态智能合约模糊测试的属性定向 Harness 合成：受控机制证据与有限公开基准研究

## 二、英文标题候选

1. Property-Directed Harness Synthesis for Stateful Smart-Contract Fuzzing: Controlled Mechanism Evidence and a Bounded Public-Benchmark Study
2. Property-Directed Transaction-Sequence Harness Synthesis for Echidna-Based Smart-Contract Fuzzing
3. Auditable Harness Synthesis for Property-Based Stateful Smart-Contract Fuzzing: Mechanisms, Public Tasks, and Semantic Boundaries

## 三、中文摘要候选

有状态智能合约中的安全属性往往需要多笔交易以特定顺序、重复访问或满足参数条件后才可能被触发。完全依赖随机交易序列会把搜索预算分配到与目标属性无关的状态路径上。本文研究一种位于 Echidna 之前的 property-directed Harness synthesis preprocessing 方法：从显式 safety property 读取的状态变量出发，反向筛选相关写入，构造交易序列候选，并结合有界重复、轻量值约束证据和可解释的 Top-K 排序，生成供 Echidna 继续进行参数与属性探索的 Solidity wrapper Harness。我们首先在为特定障碍设计的 Formal controlled benchmarks 上检查 Property、Value、Repeat 与 Top-K 的机制作用；随后在四个预登记 supported public tasks 上，对 Original、Full-K1 和 Full-K5 进行 seed 1–10 的 120-run 描述性比较。该批次观察到 118 个 `falsified` 和 2 个 `budget_exhausted`，120/120 个运行保留完整 artifact set，120/120 通过 checksum，且没有 parser/status mismatch、startup error、unknown error 或 incomplete run。上述结果只支持范围内的机制证据、运行链可审计性和描述性观察，不构成显著优越性、加速或真实生态泛化证明。尤其需要注意，生成的 Harness 将候选调用合并到 wrapper 执行模型中，与 Original 的多交易模型在 caller、transaction atomicity 和 rollback scope 等方面存在语义差异；`budget_exhausted` 仅表示在给定预算内未观察到反例，不表示属性通过或合约安全。

## 四、英文摘要候选

Stateful smart-contract properties may require a sequence of transactions, repeated invocations, or inputs satisfying intermediate guards before a counterexample becomes observable. Purely random sequence exploration can spend budget on state updates that are unrelated to the target property. We study a property-directed Harness-synthesis preprocessing method positioned before Echidna. Given an explicit safety property, the method extracts property-related state variables, filters relevant writes backward, constructs transaction-sequence candidates, adds bounded repetition and lightweight value evidence, ranks candidates with an interpretable Top-K policy, and emits a Solidity wrapper Harness for Echidna to continue fuzzing parameters and properties. We first examine the Property, Value, Repeat, and Top-K mechanisms on controlled Formal benchmarks designed around declared obstacles. We then report a descriptive 120-run comparison of Original, Full-K1, and Full-K5 over four preregistered supported public tasks and seeds 1–10. The runs contain 118 `falsified` outcomes and 2 `budget_exhausted` outcomes; all 120 artifact sets are complete, all 120 checksums pass, and no parser/status mismatch, startup error, unknown error, or incomplete run is observed. These results provide bounded mechanism evidence, an auditable execution pipeline, and descriptive observations within the declared scope; they do not establish significant superiority, speedup, or ecosystem-wide generalization. The generated Harness also uses a wrapper execution model that differs from Echidna's Original multi-transaction model in caller identity, transaction atomicity, and rollback scope. In particular, `budget_exhausted` means that no counterexample was observed within the declared budget, not that the property passed or that the contract is safe.

## 五、关键词

智能合约；有状态模糊测试；属性模糊测试；交易序列；property-directed；Harness synthesis；Echidna；Top-K；语义边界；可复现性

## 六、贡献点候选

1. **属性定向的外部前处理流程。** 给出一个位于 Echidna 之前的流程，将属性相关状态抽取、相关写入反向过滤、有界重复和值证据组合为可检查的交易序列候选生成过程；该流程不修改 Echidna core，也不替代 Echidna。
2. **受控机制证据。** 在专门设计的 Formal controlled benchmarks 上，分别检查 Property、Value、Repeat 和 Top-K 对无关路径、值方向、重复访问和候选选择障碍的作用，明确这些结果是机制范围内证据，而不是对真实合约总体的外推。
3. **可解释且可审计的 Harness 产物。** 将候选路径、Top-K 选择和 wrapper Harness 显式保存，使方法输出可以被人工检查，并把 manifest、command、environment、raw、parsed、summary、status 与 checksum 纳入统一 provenance 链。
4. **受限公开基准评价与语义边界报告。** 在四个预登记 supported public tasks 上报告 120-run 的描述性结果，同时保留 conditional 任务、static gate 限制、`budget_exhausted` 的正确解释以及 Harness/Original 的 caller、交易原子性和回滚边界。

## 七、禁止写法提醒

- 不写“Full-K1/Full-K5 显著优于 Original”或任何未经检验的 superiority 表述。
- 不写“Total calls 证明 speedup”；Original 与 Harness 的计数层次不同。
- 不写“Harness 与 Original 完全等价”；固定路径一致也不等于搜索过程和交易语义一致。
- 不把 `budget_exhausted` 写成 property passed、contract safe 或漏洞不存在。
- 不把四个 supported public tasks 写成真实生态代表样本。
- 不写 V1 普遍优于 Echidna、SMARTIAN、MuFuzz 或 IR-Fuzz；本文没有完成可比的工具级基线研究。
- 不把 `exercise2-access-control` 放入 supported pooled 结果。
- 不使用 `matched-random-v1` 支撑新论文主张；该材料保持 provenance quarantine。
