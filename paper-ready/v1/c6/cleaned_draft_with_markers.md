# 面向有状态智能合约属性模糊测试的 Harness 合成方法

## 摘要

有状态智能合约中的安全属性往往需要特定的交易顺序、重复访问或中间参数条件才能观察到反例。若完全依赖随机交易序列，搜索预算可能被与目标属性无关的状态写入和不可行前缀消耗。本文提出属性定向 Harness 合成方法（Property-directed Harness Synthesis，PHS）：从显式 safety property 读取的状态变量出发，反向筛选相关写入，构造 transaction sequence 候选，并结合 bounded repeat、lightweight value evidence 和可解释的 Top-K 排序，生成供 Echidna 继续探索参数与属性的 Solidity wrapper Harness。

PHS 位于 Echidna 之前，是外部预处理层，不修改 Echidna core，也不替代下游模糊执行。本文首先在 NoisyFourStep、BranchValue、RepeatedCall 和 ResetExample 四个受控机制基准上观察依赖、值、重复和排序因素；随后在四个 supported public tasks 上，对 Original、Full-K1 和 Full-K5 进行 seed 1--10 的 120-run 描述性比较。该批次包含 118 次 falsified 和 2 次 budget_exhausted，120/120 个运行具备完整工件并通过 checksum，parser/status mismatch、startup_error、unknown_error 和 incomplete 均为 0。[TABLE:MAIN10_SUMMARY]

这些结果支持受控机制证据、运行链可审计性和声明范围内的描述性观察，不支持超出任务与执行模型的效果推断。生成的 Harness 使用 wrapper execution model，与 Original multi-transaction model 在 caller、transaction atomicity 和 rollback scope 等方面存在语义差异。[FIG:SEMANTIC_BOUNDARY] `budget_exhausted` 仅表示在声明预算内未观察到反例，不表示属性通过或合约安全。

**关键词：** 智能合约；有状态模糊测试；属性模糊测试；property-directed；Harness synthesis；transaction sequence；Top-K；Echidna；语义边界；可复现性

## 1 引言

智能合约的行为由持久化状态、调用者身份以及一系列交易共同决定。一个安全属性可能只有在若干次状态更新之后才有机会被违反：前一笔调用写入状态，下一笔调用读取并改变控制流，最后的调用才触发属性检查。因此，属性模糊测试面对的不是单独的参数生成问题，而是交易顺序、状态积累和参数约束共同决定的可达性问题。[CITE:STATEFUL_FUZZING]

Property-based smart-contract fuzzing 以显式 safety property 作为判定接口，由测试器生成交易、参数和执行上下文，并寻找违反该条件的反例。[CITE:ECHIDNA] Echidna 是本文所采用的下游执行平台；本文关注的是在执行前如何从显式 property 中提取可解释的候选序列结构。[CITE:ECHIDNA_DOC]

普通的多交易探索保留了较大的入口集合。当目标属性只依赖少量状态变量时，无关状态写入会增加搜索噪声；当属性还依赖重复调用或中间 require 条件时，仅按函数可调用性组织序列又不足以表达这些约束。本文因此研究一个范围明确的问题：给定显式 safety property，能否在不修改下游 fuzzer core 的前提下，生成一组有针对性且可审计的候选 Harness，为后续参数模糊提供结构化输入？

PHS 选择 Harness synthesis 作为接口。PHS 负责属性相关状态分析、候选 transaction sequence 构造和排序，Echidna 继续负责 Harness 参数和 property 的模糊执行。这样，候选序列、重复上限和值线索可以作为独立中间产物检查。需要同时明确，生成的 Harness 是 Solidity wrapper，可能改变 caller、交易原子性、失败回滚、msg.value、block context 以及外部调用边界。因此，Harness 与 Original 多交易模型之间只能进行有语境的描述性比较，不能默认视为语义等价。[FIG:PHS_OVERVIEW]

本文的证据分为两类。第一类是针对单一障碍设计的 Formal controlled benchmarks，用于隔离依赖、值、重复和排序现象。第二类是四个 registry 中的 supported public tasks，用于报告有限范围内的运行状态和工件完整性；exercise2-access-control 因 caller 与地址键控状态语义保持为 conditional，不进入四任务 pooled 结果。[TABLE:BENCHMARK_REGISTRY]

本文的贡献是：

1. 定义一个位于 Echidna 之前的 property-directed preprocessing 接口，将属性相关状态、反向写入筛选、bounded repeat、lightweight value evidence 和 Top-K 组合为可检查的候选规划流程。
2. 在受控机制基准上分别观察 Dependency、Property、Repeat、Value 和 Top-K 的作用，并将这些结果限定为机制证据。[TABLE:CONTROLLED_MECHANISM]
3. 建立覆盖候选、生成、运行、解析、状态和 checksum 的 provenance 链，使候选选择和结果分类能够回溯到输入与原始产物。[FIG:PROVENANCE_PIPELINE]
4. 在四个 supported public tasks 上报告 Original、Full-K1 和 Full-K5 的 120-run 描述性结果，并把 wrapper execution model 与 Original multi-transaction model 的语义边界纳入评价。

## 2 背景

### 2.1 属性模糊测试与 safety property

属性模糊测试把待验证行为写成可执行的 safety property。对智能合约而言，属性通常读取一个或多个状态变量，并在状态不满足预期关系时返回假。测试器持续生成调用和参数，直到观察到违反条件的执行，或在声明预算内没有观察到反例。[CITE:ECHIDNA]

本文将 `falsified` 定义为：在给定执行模型、输入和预算内观察到属性反例；将 `budget_exhausted` 定义为：在声明预算内没有观察到反例。后者不是 property passed、contract safe 或漏洞不存在的证明。这一区分同时适用于 Original 和 Harness 结果。

### 2.2 状态读写与 transaction sequence

若函数 A 写入状态变量 s、函数 B 读取 s，则 A 可能是到达 B 所需状态的候选前驱。由此，一个 transaction sequence 可以表示为有序的交易调用列表，而不是单个函数调用。读写依赖只是必要线索：写入值可能方向错误，reset 可能清除中间状态，目标也可能需要重复访问同一函数。

这种分析与数据流引导、状态反馈和序列变异等方向相关，但 PHS 采用的是面向显式 property 的轻量预处理。它不试图建立完整的合约语义模型，也不把静态关系直接解释为可达性证明。[CITE:SMARTIAN] [CITE:STATEFUL_FUZZING]

### 2.3 Harness 与 Top-K

Harness 是用于组织测试调用的外部合约或包装层。PHS 将候选 transaction sequence 写入 Solidity wrapper；候选顺序在生成阶段固定，Echidna 继续对 wrapper 参数和 property 进行 fuzz。Top-K 表示写入 Harness 的候选条目数量：Full-K1 保留一条候选，Full-K5 保留五条候选。K 表示 Harness 条目数量，不是 Original 模型的等价交易长度，也不定义相同的底层工作量。

可解释排序使研究者能够检查候选为何被保留：它是否触及 property 相关状态，是否包含必要重复，是否匹配简单值条件，是否存在冲突或 unknown 条件，以及它是否位于候选池前 K 名。

### 2.4 Original 与 wrapper execution model

Original multi-transaction model 中，Echidna 探索多笔独立交易。每笔交易通常有自己的边界，sender 可能变化，某笔交易失败通常只回滚当前交易；交易间的 msg.value、区块环境和外部交互时机也可能不同。

wrapper execution model 则在一次外层 wrapper 调用中连续执行候选函数。目标调用通常由同一个 Harness 地址发起，多个调用可能共享一次 transaction atomicity；某一步 revert 可能使整个 wrapper 回滚。当前生成器也没有通用的逐步 msg.value 或不同 sender 模拟。因此，caller、transaction atomicity、rollback scope、payable、区块环境、external call 和 reentrancy 都需要单独审计。[FIG:SEMANTIC_BOUNDARY]

## 3 动机

考虑一个包含初始化函数、目标函数、无关状态写入函数和 reset 函数的合约。目标 property 只读取最后一个状态变量，而该变量需要由准备函数先行写入。若在所有入口之间盲目排列，候选序列会包含大量不能推进目标属性的路径。

NoisyFourStep 以受控方式体现这一问题：Dependency 阶段有 30 条候选，属性相关过滤后保留 3 条，目标路径成为唯一 Top-1。该结果说明 property-directed filtering 可以减少明显无关路径，但候选数量的变化不等于端到端运行效率变化。

BranchValue 体现了“写入相关变量”与“抵达目标分支”之间的差异。仅保留 property 相关结构时，候选可能仍无法接近关键 require 或比较条件；在该受控结果中，Property-K1 为 0/30，而 Value-K1 和 Full-K1 均为 30/30。这里的 value evidence 只提供局部、可解释的值方向线索，不求解全部路径约束。[TABLE:CONTROLLED_MECHANISM]

RepeatedCall 体现了重复访问障碍。若第一次调用建立状态、第二次调用才使累计量达到目标，禁止函数重复就无法生成必要路径；受控对照中，不允许重复的配置为 0/30，完整方法为 30/30。PHS 因此在声明上限内加入 bounded repeat，同时控制候选增长。

ResetExample 用于观察 reset 干扰和候选排序。当多个序列具有相近的依赖结构时，轻量值证据和顺序信息可以帮助区分候选。上述例子支持的是组件对预先声明障碍的方向性作用；四个合约均为 purpose-built controlled benchmarks，不代表真实合约生态。

## 4 方法

### 4.1 总体流程

PHS 的输入包括 Solidity 合约、一个或多个显式 safety property、可调用函数集合、分析配置、重复上限和候选数量参数 K。输出是一组带有来源信息的 transaction sequence 候选，以及由候选生成的 Solidity wrapper Harness。Echidna 继续负责参数探索和属性判定。[FIG:PHS_OVERVIEW]

处理顺序为：

1. 从 property 中提取被读取的状态变量和条件表达式；
2. 反向筛选可能写入这些状态的调用；
3. 组合满足顺序约束的候选 transaction sequence；
4. 在声明上限内加入 bounded repeat；
5. 从 require 和比较条件提取 lightweight value evidence；
6. 计算可解释分数并保留 Top-K；
7. 为候选生成 Solidity wrapper Harness；
8. 将 Harness 交给 Echidna 执行，并保留参数 fuzz 与属性检查边界。

该流程位于 Echidna 之前，目标是减少候选结构中的无关性并改善可审计性，不是给出合约安全证明。[CITE:ECHIDNA_DOC]

### 4.2 Property-related state extraction

第一步识别 property 直接读取或通过表达式间接引用的状态变量。分析器记录变量名、读取位置、比较方向和逻辑关系，并将其作为目标状态集合。对于 mapping、数组或结构体字段，需要保留能够影响判断的字段或访问模式；复杂表达式若无法可靠解析，应保留 unknown 或风险标记。

该步骤输出的是可追溯的候选入口，而不是完整语义依赖图。每个目标状态应能回指 property 中的使用位置，并在后续生成记录中保留分析配置。

### 4.3 Backward filtering of relevant writes

对每个目标状态，PHS 反向查找可能写入它的函数或调用点。直接赋值、递增、清零或沿可识别 storage 路径更新目标状态的函数进入相关写入集合；调用顺序、可见性和基础签名约束可进一步移除明显不适合的候选。

反向筛选用于缩小候选空间，不证明写入一定可达，也不证明写入一定导致 property 违反。函数间间接调用、动态 dispatch、外部合约和复杂 storage alias 可能超出轻量分析范围，因此未知状态不能被解释为无依赖。

### 4.4 Candidate transaction-sequence construction

分析器将相关写入调用组织为候选 transaction sequence。候选可以包含状态准备调用、改变控制流的中间调用和最终触发 property 检查的调用。顺序优先遵循显式依赖和可观察的调用关系；在无法确定顺序时使用受限组合，而不是无限排列。

候选构造阶段记录来源函数、目标状态覆盖、潜在前置条件和过滤原因。这样，Top-K 条目可以解释为“为何被保留”，而不只是不可追溯的编号。

### 4.5 Bounded repetition

某些状态转换要求同一个函数被调用多次，例如计数器达到阈值、累积量超过条件或重复操作触发边界。PHS 允许对部分调用生成有限次数的重复候选，并在 manifest 中记录重复函数、访问次数和配置上限。

有界重复只扩大候选结构的表达能力，同时控制组合规模。它不表示无限执行，也不表示重复调用必然导致 property 违反；RepeatedCall 只用于检查该机制在预先声明障碍上的可观察性。

### 4.6 Lightweight value evidence

PHS 从常量赋值、简单算术、入口 require 和比较表达式中提取局部值证据。若前置函数的写入方向与后续条件匹配，候选获得匹配标记；若存在冲突，则保留冲突或降低优先级。unknown 不能被改写为满足，复杂跨合约和环境值也不在该轻量证据的保证范围内。[CITE:SMARTEST] [CITE:SYMBOLIC_ANALYSIS]

lightweight value evidence 不是完整符号执行，也不是精确求解器。方法输出应写成“包含值线索的候选”，而不是“已求得满足约束的输入”。

### 4.7 Interpretable Top-K ranking

候选根据 property 相关状态覆盖、反向写入链、前置条件匹配、重复机制、值证据和无关调用等因素进行可解释排序。排序的目的，是在候选数量有限时保留较容易检查的前 K 个条目。

Full-K1 和 Full-K5 表示生成一条或五条候选 Harness 条目；K 不是 Original 多交易模型的等价交易长度。排名也不是全局搜索最优性证明：高分序列仍可能不可达，低分序列也可能包含未被分析器捕获的有效路径。

### 4.8 Solidity Harness synthesis

对于每个保留候选，PHS 生成一个 Solidity wrapper Harness。wrapper 按固定候选结构调用合约入口，同时保留供 Echidna fuzz 的参数位置。不同候选可以对应不同 Harness 条目或 wrapper 函数，具体映射由生成配置和 manifest 记录。

PHS 输出的是测试输入结构，不是合约修复或独立漏洞检测器。生成文件、分析摘要、命令和环境信息应一并保留，便于从候选回溯到 property 和证据来源。[FIG:PROVENANCE_PIPELINE]

### 4.9 Semantic boundary of generated Harness

生成 Harness 与 Original multi-transaction model 之间存在明确语义边界。wrapper 可能固定或改变 caller；多个目标调用可能被组织到同一 wrapper 执行路径；失败时的 atomicity 和 rollback 范围可能不同；msg.value、block timestamp、block number、外部调用和 reentrancy 上下文也可能不同。

因此，Harness 的 falsified 首先表示在 wrapper execution model、给定输入和预算内观察到 property 反例。只有在语义对齐后，才能进一步讨论它与 Original 模型的关系。现有 static gate 是适用性筛查，不能表述为完整 native EVM replay；没有 caller-controlled replay 时，也不能把 wrapper 结果直接解释为所有真实交易环境中的结论。[FIG:SEMANTIC_BOUNDARY]

## 5 实现与证据链

实现输入包括合约、property、配置、编译器、重复上限、Top-K 和下游 Echidna 配置。分析器生成读写摘要、基础依赖路径、属性相关路径、重复感知路径和值证据；Harness 生成器将选中候选转换为 Solidity wrapper；runner 负责预检、编译、执行、原始日志保存、解析和汇总。

每个运行应记录 run_id、Git SHA、方法版本、合约、property、配置、编译器和工具版本、seed、testLimit、timeout、workers、stopOnFail、实际命令和时间范围。运行目录区分 manifest、command、environment、generated、raw、parsed、summary、status 和 checksum。该结构使原始输出与派生表之间的关系可被检查。[TABLE:EXPECTED_RUN_MANIFEST]

状态分类包括 falsified、budget_exhausted、startup_error、unknown_error 和 incomplete。falsified 表示观察到违反 property 的反例；budget_exhausted 表示在给定预算内未观察到反例；parser/status mismatch 是解析结果与运行状态不一致的阻塞性信号，不能为了生成汇总而忽略。[TABLE:EVIDENCE_INDEX]

provenance 关注输入、命令、环境、原始输出和派生结果之间的关系。关键输入和输出记录 SHA-256，summary 由 parsed 数据按固定规则派生，status 记录执行完整性，evidence index 连接正文 claim 与源文件。工件完整和 checksum pass 说明记录链可追溯，不等于安全结论或独立复现。

历史控制实验若 provenance 不完整，则保持 quarantine，不作为新的论文主张。matched-random-v1 的来源链尚未解决，不能与当前任务结果 pooled。[TABLE:CLAIM_BOUNDARY]

## 6 实验评估

### 6.1 研究问题与实验范围

评价围绕四个问题展开：

- **RQ1：** 属性定向 sequence planning 能否在受控障碍上产生预期候选，并体现 Property、Value、Repeat 与 Top-K 的作用？
- **RQ2：** 生成 Harness 能否在声明的 wrapper execution model 下完成公开任务的执行、解析和 provenance 留存？
- **RQ3：** 在 supported public tasks 上，Original、Full-K1 和 Full-K5 的观察结果如何？
- **RQ4：** 哪些执行语义限制了这些结果的解释？

机制实验使用 NoisyFourStep、BranchValue、RepeatedCall 和 ResetExample 四个 Formal controlled benchmarks，分别构造无关路径、值方向冲突、重复调用和 reset/Top-K 障碍。公开评价只纳入 echidna-flags、echidna-multi、smartbugs-multifunc 和 smartbugs-onefunc 四个 supported public tasks。exercise2-access-control 因 msg.sender、owner equality、caller alternation 和 address-keyed mapping 依赖保持 conditional；AlternativePath、MultiProperty 和 ThreeStep 不进入分母。[TABLE:BENCHMARK_REGISTRY]

公开比较包含 Original、Full-K1 和 Full-K5，每个任务使用 seed 1--10，每种方法 10 次，共 120 runs。配置记录为 testLimit 100000、timeout 30 秒、workers 1、stopOnFail true 和 property mode；工具记录包括 Python 3.11.15、Slither 0.11.5、Echidna 2.3.2，以及按任务使用的 solc 0.8.20 或 0.4.25。Original 的 seqLen=4 与 Harness 的 seqLen=1 位于不同调用层次，不构成等价交易长度。

### 6.2 受控机制证据

四个主要受控基准的候选路径从 Dependency 阶段合计 92 条降至 Property 阶段的 31 条，减少 61 条，即 66.30%。NoisyFourStep 从 30 条降至 3 条，目标路径成为唯一 Top-1。BranchValue 中 Property-K1 为 0/30，Value-K1 和 Full-K1 均为 30/30。RepeatedCall 中不允许重复访问的配置为 0/30，完整方法为 30/30。ResetExample 显示，reset 干扰会扩大同分候选集合，局部值证据可以为 Top-K 选择提供额外区分。[TABLE:CONTROLLED_MECHANISM]

这些观察支持“组件对预先声明障碍具有可观察作用”的窄结论。由于合约规模小且障碍经过专门设计，结果停留在机制层面，不外推为一般合约效果、生态结论或工具排名。

### 6.3 运行链完整性

四个 supported public tasks 的 120 个预登记运行全部完成。120/120 个运行保留 manifest、command、environment、raw、parsed、summary、status 和 checksum；120/120 checksum pass；parser/status mismatch、startup_error、unknown_error 和 incomplete 均为 0。

这些数字说明在声明配置和 wrapper execution model 下，生成、执行、解析、状态分类和 provenance 链完整可审计。它们不表示 native EVM replay 已完成，不证明 Original 与 Harness 的语义一致，也不表示属性通过或合约安全。所有结果分组的 `main_table_usable` 仍为 `conditional`。[TABLE:MAIN10_SUMMARY]

### 6.4 公开任务的描述性比较

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

总体共有 118 个 falsified 和 2 个 budget_exhausted。两个 budget_exhausted 分别为 echidna-multi/Original/seed 1 和 echidna-multi/Full-K5/seed 7，均表示在各自执行模型和预算内没有观察到反例。echidna-flags、smartbugs-multifunc 和 smartbugs-onefunc 的三种配置均为 10/10；差异集中在 echidna-multi 的观察状态上。

该表是四个任务、三种配置和 seed 1--10 范围内的 descriptive comparison。样本只覆盖四个任务，每组只有 10 个 seed，且 Harness 与 Original 的 caller、交易边界和回滚范围不同。因此，本文不把计数差异扩展为更宽的性能结论，也不使用 Total calls 作为跨配置的工作量指标。[TABLE:MAIN10_SUMMARY]

### 6.5 语义边界

Original 的多笔交易具有独立边界，sender 可能变化，一笔交易失败通常只回滚当前交易。Harness 在一次外层 wrapper 调用内连续执行候选函数，目标函数通常来自同一个 Harness caller，一步 revert 可能影响整个 wrapper。msg.value、payable、block.timestamp、block.number、external call、reentrancy、constructor/deployer 和 address-keyed state 也可能产生差异。

因此，Harness 下观察到的 falsified 应解释为 wrapper 模型下的反例，而不是自动转换为 Original 多交易语义下的同一反例。exercise2-access-control 对 caller 和地址映射敏感，必须保持 conditional，并在单独的 caller-controlled replay 中比较 same-caller 与 alternating-caller。现有 static gate 只能作为适用性筛查，不能替代完整 native replay。[FIG:SEMANTIC_BOUNDARY]

## 7 有效性威胁

### 7.1 Internal validity

受控合约把依赖、值、重复和排序机制有意隔离，便于解释，却简化了真实合约中的复杂交互。缓解方式是把这些结果标为 controlled mechanism evidence，不与公开任务结果 pooled，也不把它们改写为生态级效果。

另一个内部风险来自配置层次差异。Original 使用多交易模型，Harness 使用单外层 wrapper；seqLen、调用层次和目标函数执行方式并不相同。两个 SmartBugs 任务还使用 Solidity 0.4.x unchecked arithmetic，另两个任务使用 solc 0.8.20。结果只能在各自声明配置下解释。

### 7.2 External validity

公开范围只有四个 supported public tasks，不能代表真实合约生态的规模、分布或调用者语义。exercise2-access-control 保持 conditional；PUB06--PUB08 是 excluded internal candidates，均不进入 supported pooled 结果。未来需要更多来源、规模和 caller 约束不同的 public tasks，但任何扩展都应先固定 registry、纳入规则和语义门控。[TABLE:BENCHMARK_REGISTRY]

### 7.3 Construct validity

本文将 falsified、budget_exhausted、artifact complete 和 checksum pass 作为不同层次的观测。falsified 是属性层面的反例观察；budget_exhausted 是预算内未观察到反例；artifact complete 和 checksum pass 是记录完整性指标。把这些指标合并成单一的安全率或成功率，会造成构念混淆。

候选数量和 Total calls 也不直接衡量跨模型效率，因为 Original 与 Harness 的计数层次不同。公开结果只作 descriptive comparison，不进行统计优越性判断。

### 7.4 Semantic validity

Harness wrapper 与 Original multi-transaction model 在 caller、transaction atomicity、rollback scope、msg.value、区块环境、external calls 和 reentrancy 上可能不同。固定成功路径的有限一致性不能升级为完整搜索过程或失败边界一致。尤其是 access-control 任务必须进行 caller-controlled replay；static gate 不能替代 native replay。[FIG:SEMANTIC_BOUNDARY]

### 7.5 Reproducibility

provenance 链使输入、命令、环境、原始输出和派生摘要之间可以相互追踪。checksum 用于完整性检查，evidence index 用于连接正文 claim、结果表和审计文件；工件可追溯不等于独立复现已经完成。[FIG:PROVENANCE_PIPELINE]

历史随机对照结果因 provenance unresolved 保持 quarantine，不作为新的论文主张。保守处理减少了可用比较材料，但避免把来源不完整的结果当作新证据。[TABLE:CLAIM_BOUNDARY]

### 7.6 Baseline comparison limitations

本文没有完成与 SMARTIAN、MuFuzz、IR-Fuzz、Harvey、ConFuzzius 或其他工具的完整、同语义、同预算、同 benchmark 工具级比较。相关工作只用于定位，不据此进行工具排名。Original 是本文公开任务中的方法配置，不等同于所有现有 fuzzer 的统一 baseline；Full-K1 和 Full-K5 也不等同于 Original 的交易长度变体。

## 8 相关工作

相关工作的正式题名、作者、年份、venue、版本和 BibTeX 仍需人工核验；以下 marker 是待替换的引用位置，不是正式参考文献。

### 8.1 Echidna 与属性模糊测试

Property-based smart-contract fuzzing 以可执行 property 组织输入生成和反例检查，Echidna 是本文下游执行语境的候选代表。[CITE:ECHIDNA] 本文与该方向的关系是接口组合：PHS 在执行前生成候选 Harness，Echidna 继续负责参数 fuzz 和 property 执行。[CITE:ECHIDNA_DOC]

### 8.2 有状态模糊测试与交易序列生成

Stateful fuzzing 和 transaction sequence generation 关注多次调用、持久状态和调用顺序。Harvey、ConFuzzius 以及其他待核验工作可用于补充这一背景。[CITE:HARVEY] [CITE:CONFUZZIUS] 本文不声称首次提出状态依赖、交易序列或重复调用；PHS 的差异在于以显式 property 为方向，通过外部 preprocessing 组织候选序列并生成 wrapper Harness。[CITE:STATEFUL_FUZZING]

### 8.3 数据流、调用排序与序列感知变异

Static/dynamic data-flow guidance、invocation ordering、branch revisiting 和 sequence-aware mutation 提供了减少无关探索和推进目标分支的相关视角。SMARTIAN、IR-Fuzz 和 MuFuzz 的正式方法边界需要逐条核验。[CITE:SMARTIAN] [CITE:IR_FUZZ] [CITE:MUFUZZ]

PHS 与这些方向的关系主要体现在接口位置：PHS 是 fuzzer 外部的 property-directed preprocessing，输出可解释的 Top-K Harness 候选；它不是对这些工具的替代，也没有在本文中完成公平的工具级实验比较。

### 8.4 符号与学习式交易推理

符号执行辅助分析和学习式交易推理可以从约束或上下文角度帮助选择调用和参数。SmarTest、Mythril、Oyente 和 ILF 等候选工作需要核验其原始来源、方法范围和术语使用。[CITE:SMARTEST] [CITE:MYTHRIL] [CITE:OYENTE] [CITE:ILF]

本文只使用 lightweight value evidence，不将其等同于完整符号执行、精确约束求解或语言模型推理。

### 8.5 Fuzzing 基础、benchmark 与 artifact reporting

ContractFuzzer、sFuzz 和 EthPloit 可作为智能合约模糊测试与输入生成的背景方向。[CITE:CONTRACTFUZZER] [CITE:SFUZZ] [CITE:ETHPLOIT] SmartBugs、SmartBugs Curated 和 Daedaluzz 则涉及 benchmark、数据集或测试资源组织。[CITE:SMARTBUGS] [CITE:SMARTBUGS_CURATED] [CITE:DAEDALUZZ]

正式论文需要根据核验后的来源确认各项工作的准确角色，不把 benchmark 名称、任务来源和本文四个 supported public tasks 混为一谈。reproducibility 和 artifact evaluation 可为 provenance、manifest、checksum 和证据索引提供报告背景。[CITE:ARTIFACT_EVALUATION]

### 8.6 本文定位

PHS 的定位是：property-directed preprocessing、external Harness synthesis、interpretable Top-K 和 semantic boundary audit 的组合。本文不把状态依赖、交易序列、重复调用、分支重访或值引导本身宣称为首创贡献，而是研究这些线索如何在属性定向的外部 Harness 合成接口中组合并保持可审计。

## 9 结论

本文提出 PHS，一种面向有状态智能合约属性模糊测试的 Harness synthesis preprocessing。PHS 从显式 safety property 读取的状态变量出发，反向筛选相关写入，构造候选 transaction sequence，加入 bounded repeat 和 lightweight value evidence，并以可解释的 Top-K 规则生成 Solidity wrapper Harness。候选顺序由前处理组织，参数和 property 探索仍由 Echidna 完成。

Formal controlled benchmarks 对无关路径、值方向、重复访问和 reset/Top-K 障碍提供了范围内机制证据。四个 supported public tasks 的 Original、Full-K1 和 Full-K5 共完成 120 个运行，其中 118 个 falsified、2 个 budget_exhausted；120/120 个运行 artifact complete、120/120 checksum pass，parser/status mismatch、startup_error、unknown_error 和 incomplete 均为 0。[TABLE:MAIN10_SUMMARY]

这些结果只支持受控机制、运行链可审计性和四个任务范围内的 descriptive comparison。Original multi-transaction model 与 wrapper execution model 在 caller、transaction atomicity、rollback scope、value、区块环境和 external-call 语义上可能不同；exercise2-access-control 继续保持 conditional，provenance 不完整的历史控制材料继续 quarantine。[TABLE:THREATS_MITIGATION]

下一步应先完成人工引用核验、图表制作、语义审图和目标 venue 格式化，再决定是否补充 public benchmark 或 caller-controlled replay。任何扩展都应使用独立 provenance，并与当前结果分开解释。
