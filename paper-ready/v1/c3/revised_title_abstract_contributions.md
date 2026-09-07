# PHS：标题、摘要与贡献点（修订稿）

## 中文标题候选

1. PHS：面向有状态智能合约属性模糊测试的 Harness 合成方法
2. 面向属性定向交易序列的 Harness 合成：受控机制证据与有限公开任务评价
3. 面向 Echidna 的属性定向 Harness 合成与执行语义边界分析

## 英文标题候选

1. PHS: Property-directed Harness Synthesis for Stateful Smart-Contract Fuzzing
2. Property-Directed Harness Synthesis for Echidna-Based Stateful Smart-Contract Fuzzing: Controlled Mechanism Evidence and a Bounded Public-Task Study
3. Auditable Property-Directed Harness Synthesis for Smart-Contract Fuzzing: Top-K Candidate Planning and Semantic Boundaries

## 中文摘要

有状态智能合约中的安全属性往往需要一组具有特定顺序、重复访问模式或参数条件的交易才能被触发。若完全依赖随机交易序列，搜索可能被与目标属性无关的状态写入和不可行前缀分散。本文提出属性定向 Harness 合成方法（Property-directed Harness Synthesis，PHS）：从显式 safety property 读取的状态变量出发，反向筛选相关写入，构造 transaction sequence 候选，并结合 bounded repeat、轻量 value evidence 和可解释的 Top-K 排序，生成供 Echidna 继续探索参数与属性的 Solidity wrapper Harness。PHS 不修改 Echidna core，而是作为其前处理步骤。我们在针对特定障碍设计的 Formal controlled benchmarks 上考察属性过滤、值方向匹配、重复访问和 Top-K 选择；随后在四个预登记的 supported public tasks 上，对 Original、Full-K1 和 Full-K5 进行 seed 1–10 的 120-run 描述性比较。该比较包含 118 个 falsified 和 2 个 budget_exhausted，120/120 个运行具有完整产物链，120/120 通过 checksum，且未观察到 parser/status mismatch、startup_error、unknown_error 或 incomplete。结果支持受控机制证据、运行链可审计性和声明范围内的描述性观察，但不支持超出任务与执行模型的效果推断。生成的 Harness 使用 wrapper execution model，与 Original multi-transaction model 在 caller、transaction atomicity 和 rollback scope 等方面存在差异；budget_exhausted 仅表示在给定预算内没有观察到反例，不表示属性通过或合约安全。

## English Abstract

Stateful smart-contract properties may require a particular transaction order, repeated invocations, or inputs satisfying intermediate guards before a counterexample becomes observable. Purely random transaction-sequence exploration can spend search budget on state updates unrelated to the target property or on infeasible prefixes. We present Property-directed Harness Synthesis (PHS), a preprocessing method positioned before Echidna. PHS extracts state variables read by an explicit safety property, filters relevant writes backward, constructs transaction-sequence candidates, adds bounded repetition and lightweight value evidence, ranks candidates with an interpretable Top-K policy, and emits a Solidity wrapper Harness for Echidna to continue exploring parameters and properties. PHS does not modify the Echidna core. We examine its filtering, value, repetition, and Top-K mechanisms on controlled Formal benchmarks designed around declared obstacles, and report a descriptive 120-run comparison of Original, Full-K1, and Full-K5 over four preregistered supported public tasks with seeds 1–10. The comparison contains 118 falsified and 2 budget_exhausted outcomes; all 120 artifact sets are complete, all 120 checksums pass, and no parser/status mismatch, startup error, unknown error, or incomplete run is observed. The evidence supports bounded mechanism observations and an auditable execution pipeline within the declared scope. It does not establish a broader effectiveness claim. The generated Harness uses a wrapper execution model that differs from Echidna's Original multi-transaction model in caller identity, transaction atomicity, and rollback scope. In particular, budget_exhausted means that no counterexample was observed within the declared budget; it is not a passed property or a safety proof.

## 关键词

智能合约；有状态模糊测试；属性模糊测试；property-directed；Harness synthesis；transaction sequence；Top-K；Echidna；语义边界；可复现性

## 贡献点

1. 提出 PHS，一种位于 Echidna 之前的 property-directed Harness synthesis preprocessing，将属性相关状态、相关写入、bounded repeat、value evidence 与 Top-K 候选选择组织为可检查的流程。
2. 在受控 Formal benchmarks 上分别考察无关路径、值方向、重复调用和候选截断等机制问题，展示组件作用并明确其受控适用范围。
3. 将候选路径、生成 Harness、运行状态和 checksum 纳入统一的 provenance 设计，使候选选择和结果分类能够回溯到输入与原始产物。
4. 在四个预登记 supported public tasks 上报告 120-run 的描述性结果，并将 wrapper execution model 与 Original multi-transaction model 的语义边界作为评价的一部分。

## 写作边界

摘要和贡献只使用窄定位：PHS 是既有属性模糊器的外部前处理与 Harness 合成方法。不得把观察结果改写为显著优越、速度提升、完全语义等价、属性通过、合约安全或真实生态代表性结论。exercise2-access-control 继续作为 conditional 任务，历史控制实验因 provenance 不完整不用于新的论文主张。
