# Evaluation 章节草稿

## 1. 实验问题

本节围绕四个问题组织评价。

- RQ1：属性定向的序列规划能否生成预期的候选调用路径，并在受控障碍上体现 Property、Value、Repeat 与 Top-K 机制的作用？
- RQ2：在声明的 wrapper 执行模型下，自动生成的 Harness 能否稳定完成公开属性基准的执行、解析和 provenance 留存？
- RQ3：在预登记的四个 supported public tasks 上，Original、Full-K1 与 Full-K5 的观察结果如何？
- RQ4：哪些语义边界限制了 Harness 结果的解释？

这些问题分别对应机制可解释性、执行链完整性、范围内描述性比较和语义适用性。它们不把 Harness synthesis 重新定义为新的通用模糊器，也不把结果扩展为对所有智能合约的性能结论。

## 2. 实验对象

被评价的方法是 V1 的外部前处理流程：从合约和显式 Echidna safety property 中提取状态读写关系，进行属性相关过滤，按需要加入有界重复访问和值约束，再选择 Top-K 候选路径并生成 Solidity Harness。Echidna 仍负责后续的参数和属性探索；因此，本文将该方法定位为面向既有属性模糊测试器的 property-directed Harness synthesis preprocessing。

机制问题使用为特定障碍设计的 Formal benchmarks，包括无关路径干扰、值方向分支、重复调用和 reset 干扰。它们用于验证组件是否解决了预先声明的障碍，不代表真实合约总体。

公开任务只包括四个经过登记并进入主运行的任务：echidna-flags、echidna-multi、smartbugs-multifunc 和 smartbugs-onefunc。exercise2-access-control 因 msg.sender、owner equality、caller alternation 和 address-keyed mapping 保持 conditional；AlternativePath、MultiProperty 和 ThreeStep 是内部候选，不属于公开基准池，也不贡献主运行分母。

## 3. 实验设置

公开任务采用预登记的三组方法：Original、Full-K1 和 Full-K5，每个任务使用 seed 1–10，共 4 × 3 × 10 = 120 个运行。Original 使用 public-c1-original.yaml，Harness 方法使用 public-c1-harness.yaml；testLimit 为 100000，timeout 为 30 秒，workers 为 1，stopOnFail 为 true，运行模式为 property。

编译器记录按任务保留：echidna-flags 和 echidna-multi 使用 solc 0.8.20，两个 SmartBugs 适配任务使用 solc 0.4.25，并保留 Solidity 0.4.x unchecked arithmetic 语义。已完成运行的工具 provenance 记录包括 Python 3.11.15、Slither 0.11.5 和 Echidna 2.3.2；方法版本记录为 Full-v1.0.1-compat。

Original 的 seqLen=4 表示 Echidna 的多交易搜索；Harness 的 seqLen=1 表示一次外层 wrapper 调用，而 wrapper 内可以连续调用多个目标函数。因此，seqLen 不是两个方法之间的等价交易长度。所有 Harness 结果均按 wrapper 执行模型解释。

本节不纳入 exercise2-access-control、PUB06–PUB08 或 matched-random-v1，也不重新运行任何工具。static_gate_pass 只作为静态适用性审计结果，不写成 native EVM replay 结果。

## 4. 指标定义

对于每个运行，保留以下互斥状态：

- falsified：在声明的执行模型、输入和预算内观察到属性反例；
- budget_exhausted：在声明预算内没有观察到属性反例；
- startup_error、unknown_error 和 incomplete：分别表示启动、未知错误和不完整运行。

按任务和方法报告 runs、falsified、budget_exhausted 及 observed falsification rate，其中 observed falsification rate 定义为 falsified / runs。该比率是给定任务、配置和 seed 范围内的描述性统计，不是属性通过率、安全概率或跨生态泛化估计。特别地，budget_exhausted 不能解释为 property passed、contract safe 或 absence of vulnerability。

执行链的可靠性另外由 artifact set completeness、checksum pass 和 parser/status agreement 衡量。它们回答的是结果是否可追溯和可复核，不回答合约是否安全。Original 与 Harness 的 Total calls 位于不同的外层计数层次，本评价不使用它来计算 speedup。

## 5. 结果概述

四个公开任务的 120 个预登记运行全部完成，118 个被分类为 falsified，2 个被分类为 budget_exhausted；startup_error、unknown_error、incomplete 和 parser/status mismatch 均为 0。120/120 个运行目录的 artifact set 完整，120/120 checksum 通过。两个 budget_exhausted 运行是 echidna-multi/Original/seed 1 和 echidna-multi/Full-K5/seed 7。

任务级结果如下。echidna-flags 上三种方法均为 10/10 falsified。echidna-multi 上 Original 为 9/10、Full-K1 为 10/10、Full-K5 为 9/10，剩余运行均为 budget_exhausted。smartbugs-multifunc 和 smartbugs-onefunc 上三种方法均为 10/10 falsified。表格化结果见 evaluation_tables.md；run-level provenance 应置于附录。

这些结果显示三种执行配置在当前四个任务上都能观察到反例，但并不形成一致的、可作统计推断的优越性排序。尤其是 echidna-multi 中 Full-K1 的 10/10 与另外两组 9/10 的差异只是一项有限范围内的观察，不能写成显著优于 Original。

## 6. RQ1：候选路径规划的机制证据

受控 Formal 结果支持对机制作用作窄范围、可解释的描述。四个主要受控基准的候选路径总数从 Dependency 阶段的 92 条降至 Property 阶段的 31 条，减少 66.30%。在 NoisyFourStep 中，属性过滤将候选从 30 条缩减到 3 条，并使目标路径成为唯一 Top-1。该结果说明属性相关状态可以用于压缩候选空间，但不自动说明模糊测试端到端加速。

组件障碍的对照结果也具有方向性。BranchValue 中，仅按属性依赖的 Property-K1 为 0/30，而加入值匹配后的 Value-K1 和 Full-K1 均为 30/30；RepeatedCall 中，不允许重复访问的配置为 0/30，而完整方法为 30/30。ResetExample 中，值约束帮助在较大的同分集合中区分目标路径。由于这些合约是为特定障碍设计的，上述结果支持“组件解决声明障碍”的机制主张，不支持真实生态总体有效性或工具级胜出。

## 7. RQ2：Harness 执行链的可审计性

在四个预登记 supported public tasks 上，所有 120 个运行都留下 manifest、command、environment、raw、parsed、summary、status 和 checksum 产物；checksum 120/120 通过，parser/status mismatch 为 0，且没有 startup_error、unknown_error 或 incomplete。由此可以确认，在声明的配置和当前 wrapper 模型下，公开任务的生成、执行、解析和 provenance 链条是完整可审计的。

这里的“可靠”仅指运行链和分类链的完整性，不是完整 EVM 语义等价或安全性证明。静态 gate 不能替代 native replay；四个任务的正式论文纳入仍应保留任务级语义复核条件。对于 Harness，falsified 的含义是 wrapper 执行模型下观察到反例，而不是自动转换为 Original 多交易模型下完全相同的反例。

## 8. RQ3：三种方法的描述性比较

结果表允许在预登记的四个 supported public tasks 和 seed 1–10 范围内并列报告 Original、Full-K1 和 Full-K5。三种方法在 echidna-flags、smartbugs-multifunc 和 smartbugs-onefunc 上均在全部 10 个运行中观察到反例；差异集中在 echidna-multi，其中 Full-K1 为 10/10，Original 和 Full-K5 各为 9/10。

这一模式适合写成描述性观察：Full-K1 和 Full-K5 在多数任务组中观察到了 falsified。它不适合写成显著优于、稳定快于或普遍优于 Original。原因包括样本只覆盖四个 supported 任务、每组只有 10 个 seed、结果状态包含 budget_exhausted，以及 Original 和 Harness 的调用者、交易边界和回滚语义不同。Total calls 也不能弥补这些差异，因为两个方法的计数层次并不相同。

## 9. RQ4：语义边界

Original 由多笔独立交易组成，不同外层交易可能使用不同 sender；某一步失败通常只回滚该交易。Harness 则在一次外层 wrapper 调用中连续执行候选函数，目标函数通常看到相同的 Harness caller，一步 revert 可能回滚整个 wrapper。msg.value、payable 行为、区块环境、external call、reentrancy、constructor/deployer 和 address-keyed state 也不能默认对齐。

因此，当前四个任务只能在静态筛查和已声明输入条件下作为 supported pool 报告。exercise2-access-control 明确依赖 msg.sender、owner equality 和 address-keyed mapping，且需要比较 same-caller 与 alternating-caller；它不能进入 supported pooled 结果。固定成功路径上的最终属性相关状态一致，也只能说明窄条件下的可重放性，不能证明完整搜索过程、调用次数、失败前缀和回滚范围等价。

## 10. 不能由本评价得出的结论

本评价不支持以下结论：Full-K1 或 Full-K5 显著优于 Original；Total calls 证明 speedup；Harness 与 Original 完全等价；budget_exhausted 表示属性通过或合约安全；四个公开任务代表真实合约生态；V1 普遍优于 Echidna、SMARTIAN、MuFuzz 或 IR-Fuzz；matched-random-v1 可以作为新的控制证据；或当前结果已经证明大型真实合约上的可扩展性。

## 11. 小结

综合来看，现有证据支持一个窄定位的评价结论：V1 能在受控 Formal benchmarks 上生成具有可解释性的属性定向候选路径，并在四个预登记 supported public tasks 上完成 120 个运行的可审计描述性比较。118 个运行观察到 falsified，2 个运行在预算内未观察到反例；该状态分布及完整 provenance 可以进入论文初稿，但必须同时保留 wrapper 语义差异、static gate 限制、公开任务数量有限和缺少工具级竞品比较等边界。
