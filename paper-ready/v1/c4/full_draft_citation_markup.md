# 面向属性模糊测试的智能合约交易序列 Harness 合成方法

## 摘要

智能合约的属性违反通常依赖一组有序的状态转换，而不是单笔独立调用。对于以 safety property 为目标的模糊测试，若候选交易序列包含大量与目标属性无关的状态写入，搜索预算就可能被分散；另一方面，重复调用和接近 require 或比较条件的参数值也可能决定目标状态是否可达。本文提出属性定向 Harness 合成方法（Property-directed Harness Synthesis，PHS），将显式 safety property 转换为 property-directed 的候选交易序列规划，并以 Solidity wrapper Harness 的形式交给 Echidna 执行。PHS 包含属性相关状态提取、反向写入筛选、有界重复、轻量值证据和可解释的 Top-K 排序；它是 Echidna 之前的外部预处理层，不修改 Echidna core，也不替代下游模糊执行。

本文首先在 NoisyFourStep、BranchValue、RepeatedCall 和 ResetExample 四个受控机制基准上观察依赖、值、重复和排序因素。随后在四个受支持的公开任务上，采用 Original、Full-K1 和 Full-K5 三种配置、1--10 共 10 个 seed，进行 120 次运行的描述性评估。[EVIDENCE:E20_PHASE_B4_MAIN10_RUN] 结果中有 118 次 falsified 和 2 次 budget_exhausted；后者表示在给定预算内未观察到反例，不表示属性通过或合约安全。120/120 次运行具有完整工件并通过 checksum 检查，parser/status mismatch、startup_error、unknown_error 和 incomplete 均为 0。[TABLE:MAIN10_SUMMARY] 这些结果用于说明受控机制证据和有限公开任务范围内的运行记录，不支持普遍优越性、效率主张或生态级外推。由于 Solidity wrapper Harness 与 Original 多交易模型在 caller、原子性、回滚及执行上下文方面存在语义差异，二者不应默认视为等价。[FIG:SEMANTIC_BOUNDARY]

**关键词：** 智能合约；属性模糊测试；交易序列；Property-directed Harness Synthesis；Echidna；证据可追溯性

## 1 引言

智能合约的行为由持久化状态、调用者身份和一系列交易共同决定。一个安全属性可能只在若干次状态更新之后才有机会被违反：前一笔调用写入某个状态变量，下一笔调用读取该变量并改变控制流，最后一笔调用才触发属性检查。因而，单笔调用的覆盖或局部输入变异并不能充分表达所有属性触发条件。交易顺序、状态依赖和参数约束构成了一个相互关联的搜索问题。[CITE:STATEFUL_FUZZING]

Property-based smart-contract fuzzing 提供了一个直接的验证接口：研究者以 Solidity property、assertion 或其他可执行条件表达希望持续成立的行为，再由模糊测试器生成交易和参数，寻找能够违反该条件的反例。[CITE:ECHIDNA] Echidna 是本文所采用的下游执行平台。它的作用是执行 property-based fuzzing；本文关注的是在执行前如何从显式 property 中提取可解释的候选序列结构。[CITE:ECHIDNA_DOC]

在普通的多交易探索中，合约的所有可调用入口都可能进入候选集合。这样的开放搜索具有一般性，但当目标属性只依赖少量状态变量时，无关状态写入路径会增加搜索噪声。更复杂的属性还可能依赖同一函数的多次调用，或者要求输入值接近 require 条件、阈值比较或地址映射键。仅按函数名或静态可调用性组织序列，难以同时表达这些信号。本文的问题因此被限定为：给定一个显式 safety property，能否在不修改下游 fuzzer core 的前提下，生成一组更有针对性、可审计的候选 Harness，从而为后续的参数模糊提供结构化输入？

本文选择 Harness synthesis 而不是直接修改 fuzzer core，原因在于这种接口可以把方法边界显式化。PHS 负责属性相关状态分析、候选交易序列构造和排序；Echidna 仍负责对 Harness 参数进行 fuzz。这样既保留了下游执行器的能力，也使候选序列、重复上限和值线索可以被单独检查。需要强调的是，生成的 Harness 是 Solidity wrapper，可能改变 caller、交易原子性、失败回滚、msg.value、block context 以及外部调用边界。因此，Harness 执行结果与 Original 多交易执行结果之间只能进行有语境的描述性比较，不能默认视为语义等价。[FIG:PHS_OVERVIEW]

本文的证据范围也有明确界限。受控机制实验用于隔离依赖、值、重复和排序现象；公开任务评估只包含四个 registry 中受支持的任务，exercise2-access-control 因 caller 与地址键控状态语义单列为 conditional。公开评估使用三种方法配置、四个任务和十个 seed，共 120 次运行，结果以状态计数和工件完整性描述，不进行显著性检验，也不把 Total calls 转化为效率结论。[TABLE:BENCHMARK_REGISTRY]

本文贡献如下：

1. 提出属性定向 Harness 合成方法（PHS），定义一个位于 Echidna 之前的 property-directed preprocessing 接口，将属性相关状态、反向写入筛选、有界重复、轻量值证据和 Top-K 组合为可解释的候选规划流程。
2. 在受控机制基准上分别观察 Dependency、Property、Repeat、Value 和 Top-K 相关证据，说明这些机制在小型、明确构造的场景中可以被单独检查。[TABLE:CONTROLLED_MECHANISM]
3. 在四个受支持公开任务上提供 Original、Full-K1 和 Full-K5 的 120-run 描述性结果及完整工件索引，报告 118 次 falsified、2 次 budget_exhausted，以及完整性和解析状态检查。
4. 明确记录 wrapper Harness 与 Original 多交易模型的语义边界，并将 provenance、checksum、static gate 与 native replay 的差异纳入评估解释。[FIG:PROVENANCE_PIPELINE]

## 2 背景

### 2.1 属性模糊测试

Property-based fuzzing 把待验证行为写成可执行的 safety property。测试器不断生成输入、调用合约并检查 property；一旦观察到违反条件的执行，就可以报告相应的反例。该模式与只针对预定义漏洞模式的扫描不同，它允许研究者表达合约特定的不变量或业务条件。[CITE:ECHIDNA]

本文把 Echidna 视为下游执行平台。PHS 不改变 Echidna 的属性检查和参数 fuzz 机制，而是为其提供 Solidity wrapper Harness 候选。方法的输入是合约、显式 property、可调用函数以及必要的配置；输出是包含固定候选调用结构的 Harness 条目。条目中的参数仍由 Echidna fuzz，因而“固定候选顺序”并不意味着输入参数被固定。

### 2.2 状态变量、写读依赖与交易序列

智能合约状态变量在交易之间持久化。某个函数可能写入状态，后续函数读取该状态，并根据读取值进入不同分支。由此，一个 transaction sequence 可以表示为有序的交易调用列表，而不是单个函数调用。属性相关状态分析的基本问题，是判断 property 读取了哪些变量，以及哪些调用可能在此前写入这些变量。

这种分析可与数据流引导、状态反馈和序列变异等方法产生联系，但本文采用的是面向显式 property 的轻量预处理。它不试图建立完整的合约语义模型，也不把静态关系直接解释为可达性证明。[CITE:SMARTIAN] [CITE:STATEFUL_FUZZING]

### 2.3 Harness 与两种执行模型

Harness 是用于组织测试调用的程序包装层。本文生成的是 Solidity wrapper Harness：它在一个或多个 wrapper 函数中组织候选调用，并把候选序列暴露给 Echidna。与之对照的 Original multi-transaction model 让测试器按原始交易方式进行多次调用。

这两种模型在 caller、交易边界、atomicity、rollback、msg.value、区块上下文、外部调用和潜在重入交互方面可能不同。因而，wrapper execution model 的主要用途是提供一种可执行的候选入口，而不是声称对 Original 模型进行了语义保持变换。[FIG:SEMANTIC_BOUNDARY]

### 2.4 Top-K、有界重复与轻量值证据

PHS 为候选序列计算可解释分数，并保留前 K 个候选 Harness 条目。Full-K1 和 Full-K5 中的 K 表示候选 Harness 条目的数量，而不是与 Original 等价的交易长度。Top-K 是候选组织策略，不表示全局最优序列，也不提供反例必然存在的证明。

有界重复允许同一调用在候选序列中出现有限次数，用于表示某些需要重复状态更新的机制。轻量值证据则从 require、比较条件或类似约束中提取可解释的值线索，帮助候选构造靠近目标分支。二者都属于搜索规划证据，不等同于无限重复、精确约束求解或完整符号执行。[CITE:SMARTEST] [CITE:SYMBOLIC_ANALYSIS]

## 3 动机

考虑一个包含四个状态更新函数的合约。目标 property 只读取最后一个状态变量，但该变量需要先由某个准备函数写入；另外两个函数虽然也写入状态，却不会影响 property。若测试器在所有入口之间盲目排列，候选序列会包含大量无关路径。无关调用并不一定是错误，却会让有限预算更多地用于不能推进目标属性的状态变化。

NoisyFourStep 用受控方式体现这一问题：property 只依赖一条较短的写入链，其他函数形成噪声。通过从 property 读取的状态变量反向追踪潜在写入者，可以把候选集合从所有状态写入缩小到与目标属性相关的子图。该观察只说明在构造性 benchmark 中依赖信号可被隔离，并不代表公开合约生态普遍具有相同结构。[TABLE:CONTROLLED_MECHANISM]

第二个问题是“写入了相关变量”并不等于“容易抵达目标分支”。BranchValue 中，相关函数需要输入值接近 require 或比较条件。若只保留 property 相关函数而不记录值约束，序列结构虽然正确，参数仍可能长期停留在无效区域。轻量值证据为候选提供可解释的近似线索，但它不求解全部路径约束，也不保证找到满足条件的参数。

第三个问题来自重复调用。RepeatedCall 表明，某个属性可能只有在同一状态更新被调用多次之后才会改变。普通的去重策略会删除这种候选，而无界重复又会造成组合爆炸。因此，PHS 采用有界 repeat：保留有限次数的重复可能性，并把上限作为方法配置的一部分。ResetExample 进一步用于观察候选排序：当多个序列都能表示相关机制时，轻量证据和序列结构可以帮助把较有希望的候选置于 Top-K 前部。

这四类情形说明，property-directed filtering、bounded repeat、value evidence 和 Top-K 不是互相替代的步骤。它们分别处理无关路径、重复状态推进、参数接近条件和候选数量控制。本文将其组合为外部 Harness synthesis 流程，使每一步都能被解释、审计和单独评估。[FIG:SEQUENCE_PLANNING]

需要再次区分两种证据范围。NoisyFourStep、BranchValue、RepeatedCall 和 ResetExample 是 controlled benchmarks，用于观察机制；它们不代表真实生态。四个 supported public tasks 则用于描述性运行结果，数量有限，且 exercise2-access-control 保持 conditional。由此，动机支持的是一种可检查的研究问题和方法设计，不支持把 PHS 外推为通用安全检测框架。

## 4 方法

### 4.1 Overview

PHS 的输入包括 Solidity 合约、一个或多个显式 safety property、可调用函数集合、分析配置和候选数量参数 K。方法输出是一组按可解释规则排序的候选 transaction sequence，并进一步生成 Solidity wrapper Harness。下游 Echidna 对 Harness 的参数进行 fuzz，检查原有 property。[FIG:PHS_OVERVIEW]

PHS 的流程为：

1. 从 property 中提取被读取的状态变量和条件表达式；
2. 反向筛选可能写入这些状态的调用；
3. 组合满足顺序约束的候选 transaction sequence；
4. 受限地加入 bounded repeat；
5. 从 require 和比较条件提取 lightweight value evidence；
6. 计算可解释分数并保留 Top-K；
7. 为候选序列生成 Solidity wrapper Harness；
8. 将 Harness 交给 Echidna 执行，保留参数 fuzz 和属性检查边界。

该流程位于 Echidna 之前，不修改 Echidna core，也不替代 Echidna。它的目标是减少候选结构中的无关性并改善可审计性，而不是给出合约安全证明。

### 4.2 Property-related state extraction

第一步识别 property 直接读取或通过表达式间接引用的状态变量。分析器记录变量名、读取位置、涉及的比较或逻辑关系，并将其作为目标状态集合。对于 mapping、数组或结构体字段，需要保留能够影响判断的字段或访问模式；无法可靠解析的复杂表达式不应被静默当作已理解。

该步骤的结果不是完整语义依赖图，而是一个可追溯的候选入口。每个目标状态应能回指 property 中的使用位置，并在后续表格或 manifest 中记录分析配置。

### 4.3 Backward filtering of relevant writes

对每一个目标状态，PHS 反向查找可能写入它的函数或调用点。若函数直接赋值、递增、清零或通过可识别的 storage 路径更新目标状态，则进入相关写入候选集合。之后可根据调用顺序、可见性和基础签名约束移除明显不适合的候选。

反向筛选的作用是缩小候选空间，不是证明写入一定可达，也不是证明写入一定会导致 property 违反。函数间间接调用、动态 dispatch、外部合约和复杂 storage alias 可能超出轻量分析范围，因此实现需要保留未知和不确定状态，而不能把未知解释成无依赖。

### 4.4 Candidate transaction-sequence construction

分析器将相关写入调用组织为候选 transaction sequence。候选可以包含状态准备调用、改变控制流的中间调用和最终触发 property 检查的调用。顺序优先遵循显式依赖和合约中可观察的调用关系；在无法确定顺序时，使用受限组合而不是无限排列。

候选构造阶段记录每个序列的来源函数、目标状态覆盖、潜在前置条件和过滤原因。这样，Top-K 条目可以解释为“为何被保留”，而不只是一个不可追溯的编号。

### 4.5 Bounded repetition

某些状态转换要求同一个函数被调用多次，例如计数器达到阈值、累积量超过条件或重复操作触发边界。PHS 因此允许对部分调用生成有限次数的重复候选。重复上限由配置给出，且应写入生成 manifest。

有界重复只扩大候选结构的表达能力，同时控制组合规模。它不表示无限执行，也不表示重复调用必然导致 property 违反。受控 RepeatedCall 用于检查该机制是否能被观察到；其结果不能外推为所有合约都需要重复调用。

### 4.6 Lightweight value evidence

PHS 从 require、if 条件、比较表达式和可识别的常量关系中提取轻量值证据。例如，若某分支要求计数器不小于阈值，候选条目可以记录阈值方向或近似值域。该证据用于排序和生成可解释的参数提示，但实际参数仍由 Echidna fuzz。

轻量值证据不是完整符号执行，也不是精确求解器。它可能忽略跨函数算术、环境变量、外部调用返回值和复杂别名关系。因而，方法输出应写成“包含值线索的候选”，而不是“已求得满足约束的输入”。[CITE:SMARTEST] [CITE:SYMBOLIC_ANALYSIS]

### 4.7 Interpretable Top-K ranking

每个候选序列根据若干可解释因素评分，包括 property 相关状态覆盖、反向写入链长度、前置条件匹配、重复机制、值证据以及无关调用数量。评分的目的，是在候选数量有限时保留较容易说明的前 K 个条目。

Full-K1 与 Full-K5 表示生成一条或五条候选 Harness 条目；K 不是 Original 多交易模型的等价交易长度。排名也不是全局搜索最优性证明，分数高的序列仍可能在真实执行中不可达，分数低的序列也可能包含未被分析器捕获的有效路径。

### 4.8 Solidity Harness synthesis

对于每个保留候选，PHS 生成一个 Solidity wrapper Harness。wrapper 负责按固定候选结构调用合约入口，并保留可供 Echidna fuzz 的参数位置。不同候选可以对应不同 Harness 条目或 wrapper 函数，具体映射由生成配置和 manifest 记录。

PHS 输出的是测试输入结构，不是合约修复，也不是独立漏洞检测器。生成文件、分析摘要、命令和环境信息应一并保留，便于从候选回溯到 property 和证据来源。[FIG:PROVENANCE_PIPELINE]

### 4.9 Semantic boundary of generated Harness

生成 Harness 与 Original multi-transaction model 之间存在明确语义边界。wrapper 可能固定或改变 caller；多个目标调用可能被组织到同一 wrapper 执行路径；失败时的 atomicity 和 rollback 范围可能不同；msg.value、block timestamp、block number、外部调用和 reentrancy 上下文也可能不同。因而，Harness 的 falsified 结果首先是 wrapper execution model 下的 property 反例，只有在语义对齐后才能进一步讨论其与 Original 模型的关系。[FIG:SEMANTIC_BOUNDARY]

这一边界是方法的一部分，而不是附带说明。评估中必须同时报告方法配置、执行入口、caller 假设和 replay gate。现有 static gate 不能被表述为完整 native EVM replay；没有 caller-controlled replay 时，也不能把 wrapper 结果直接解释为所有真实交易环境中的结论。

## 5 实现

PHS 的实现输入包括 Solidity 源码、目标 property、可分析的函数和状态信息、候选 K、repeat bound、值证据配置以及下游 Echidna 配置。分析器负责解析 property 相关状态和写入关系；候选路径生成器负责组合、过滤和重复展开；Harness 生成器负责输出 Solidity wrapper 和候选元数据；runner 则负责在声明的执行环境中调用下游工具并收集结果。

每次运行都应记录 run_id、Git SHA、方法版本、合约、property、配置、编译器和工具版本、seed、testLimit、timeout、workers、stopOnFail、实际命令和时间范围。运行目录还应区分 manifest、command、environment、raw、parsed、summary、status 和 checksum。该结构使原始输出与派生表之间的关系可被检查。[TABLE:EXPECTED_RUN_MANIFEST]

状态分类至少包括 falsified、budget_exhausted、startup_error、unknown_error 和 incomplete。falsified 表示观察到违反 property 的反例；budget_exhausted 表示在给定预算内未观察到反例，不能翻译为“通过”或“安全”。parser/status mismatch 是解析结果与运行状态不一致的阻塞性信号，不能为了生成汇总而忽略。

可复现性设计强调 provenance 而非单一数字。输入文件和关键输出记录 SHA-256，summary 由固定规则从 parsed 数据派生，status 记录执行完整性，evidence index 连接正文 claim 与源文件。[TABLE:EVIDENCE_INDEX] 历史控制实验若 provenance 不完整，应进入 quarantine，不作为新的论文主张。类似地，匹配随机对照结果因 provenance 未解决而保持隔离。

## 6 实验评估

### 6.1 研究问题与实验对象

本文围绕四个问题展开评估：

- RQ1：property-related state extraction 和 backward filtering 是否能在受控场景中识别与目标属性相关的写入链？
- RQ2：property、value、repeat 和 Top-K 证据是否在受控机制 benchmark 中产生可观察差异？
- RQ3：在四个受支持公开任务上，Original、Full-K1 和 Full-K5 的运行状态呈现怎样的描述性分布？
- RQ4：运行工件、checksum、解析状态和语义门控是否足以支持在声明范围内审计结果？

实验对象分为两类。第一类是 Formal controlled benchmarks：NoisyFourStep、BranchValue、RepeatedCall 和 ResetExample。它们是小型、明确构造的合约，用于隔离 Dependency、Property、Repeat、Value 和 Top-K 机制。[TABLE:CONTROLLED_MECHANISM] 第二类是 supported public tasks：echidna-flags、echidna-multi、smartbugs-multifunc 和 smartbugs-onefunc。exercise2-access-control 由于 caller、msg.sender 和地址键控 mapping 语义需要额外条件说明，保持为 conditional task，不纳入四个任务的 pooled 结果。[TABLE:BENCHMARK_REGISTRY]

### 6.2 受控机制实验

NoisyFourStep 用于观察 property 相关依赖能否缩小候选写入集合。其 property 依赖一条特定状态链，而其他函数构成无关写入噪声。结果支持一种机制性解释：从 property 读取的状态反向定位写入调用，比把所有可调用入口视为同等相关更接近目标属性的结构。该证据不等同于完整可达性证明，也不代表所有合约都具有同样的依赖稀疏性。

BranchValue 用于检查值证据。仅保留 property 相关结构时，候选可能仍不能接近关键 require 或比较条件；加入 value evidence 后，目标分支的机制差异可以在受控设置中被观察。该结果支持“值线索应进入候选排序或参数提示”的设计动机，但不说明轻量规则可以替代符号执行或精确求解。

RepeatedCall 用于检查有界重复。去除重复调用的候选不能表达需要多次状态更新的机制，而包含有界重复的候选可以覆盖该结构。该结果支持 bounded repeat 作为候选构造选项，但不代表无限重复可行，也不代表重复机制在公开任务中普遍占主导。

ResetExample 用于观察候选排序和 Top-K。多个候选都可能包含部分相关调用时，属性相关状态覆盖、顺序和轻量值证据可以形成可解释的排序。Top-K 的作用是控制输出候选数量并保留多样性，而非证明保留的序列是全局最优。

### 6.3 公开任务的描述性对照

公开任务评估采用三种方法配置：Original、Full-K1 和 Full-K5。每种配置在四个 supported public tasks 上分别使用 seed 1--10，共计 3 × 4 × 10 = 120 次运行。[EVIDENCE:E20_PHASE_B4_MAIN10_RUN] 这里的 comparison 是 descriptive comparison：它用于报告不同配置下的运行状态和工件情况，不进行显著性检验，不依据总调用次数推导效率结论，也不把四个任务解释为真实生态的代表样本。[TABLE:MAIN10_SUMMARY]

120 次运行中，118 次状态为 falsified，2 次状态为 budget_exhausted。falsified 表示在对应执行模型和预算下观察到了 property 反例；budget_exhausted 仅表示在预算内没有观察到反例，可能由搜索覆盖、参数空间、语义边界或预算限制造成，不能被解释为 property passed、contract safe 或无漏洞。[TABLE:MAIN10_SUMMARY]

按 benchmark 和 method 的结果应以主实验汇总表为准，并保留 Original、Full-K1、Full-K5、四个任务和 10 个 seed 的维度。汇总表的所有主表行仍带有 conditional 可用性说明，不能改写为无条件的结论。对每个任务，正文应报告运行状态分布、工件完整性和语义注意事项；不应把某一配置在有限 seed 下的计数改写成普遍优越性。

完整性检查显示，120/120 次运行具有完整 artifact，120/120 次运行通过 checksum。parser/status mismatch 为 0，startup_error、unknown_error 和 incomplete 均为 0。[TABLE:MAIN10_SUMMARY] 这些数字说明记录链和状态解析在该批运行中保持一致；它们不证明 property 都被验证，也不消除 benchmark 范围、caller 模型和 replay 能力带来的有效性威胁。[FIG:PROVENANCE_PIPELINE]

### 6.4 结果解释与语义限制

公开任务的结果不能脱离执行模型解释。Original 使用 Original multi-transaction model；Full-K1 和 Full-K5 使用 wrapper execution model。由于 caller、atomicity、rollback、msg.value、block context、外部调用和重入边界可能不同，三种配置的状态计数不构成完全对齐的工具比较。尤其不能把 Harness 中的 falsified 自动解释为原始真实交易流程中同一语境的反例，也不能把预算耗尽自动解释为安全。

现有静态回放门控可以帮助发现部分可回放或结构性问题，但不是完整 native EVM replay。exercise2-access-control 需要 caller-controlled 条件，故不进入四个 supported public tasks 的 pooled 统计。历史随机对照结果因 provenance 不完整被隔离，不参与本文新的主张。[TABLE:CLAIM_BOUNDARY]

因此，评估支持的结论是窄的：PHS 的步骤在受控机制 benchmark 中具有可观察的机制证据；四个公开任务上存在一组 120-run 的、工件完整且状态可审计的描述性结果；方法和结果的语义边界被显式记录。评估不支持对所有合约、所有执行器或更广泛工具作普遍性能排序。

## 7 有效性威胁

### 7.1 Internal validity

内部有效性首先受到构造性 benchmark 的影响。受控合约将依赖、值、重复和排序机制隔离，便于解释，却可能把真实合约中的复杂交互简化。缓解方式是把这些结果明确称为 mechanism evidence，不将它们与公开任务结果 pooled，也不把它们改写为生态级效果。

其次，结果解析、状态分类和 artifact 派生可能引入错误。本文保留 manifest、command、environment、raw、parsed、summary、status 和 checksum，并检查 120/120 artifact complete、120/120 checksum pass、0 parser/status mismatch、0 startup_error、0 unknown_error 和 0 incomplete。上述检查降低了记录层面的风险，但不能消除分析器误判、工具版本差异或执行环境差异。

### 7.2 External validity

公开任务只有四个 supported public tasks：echidna-flags、echidna-multi、smartbugs-multifunc 和 smartbugs-onefunc。它们用于提供有限的 public-benchmark evidence，不代表真实合约生态的规模、分布或调用者语义。exercise2-access-control 因 caller 和地址键控状态条件单列为 conditional，不能并入 supported pooled 结果。[TABLE:BENCHMARK_REGISTRY]

未来需要更多公开任务、不同合约规模和更丰富的 caller 约束，以检验 PHS 在不同状态模型和属性类型下的适用范围。任何扩展都应先定义 benchmark registry、纳入规则和语义门控，再单独报告。

### 7.3 Construct validity

本文使用 falsified、budget_exhausted、artifact complete 和 checksum pass 作为不同层次的观测。falsified 是属性层面的反例观测；budget_exhausted 不是属性通过；artifact complete 和 checksum pass 是记录完整性指标。若将这些指标合并为单一“安全率”或“成功率”，就会造成构念混淆。

同样，Total calls 可能受 wrapper 结构、参数 fuzz 和工具内部执行策略影响，本文不把它作为 speedup 或效率主张的依据。公开结果采用 descriptive comparison，避免把计数差异解释为统计优越性。

### 7.4 Semantic validity

最大的语义威胁来自 Harness wrapper 与 Original 多交易模型之间的差异。wrapper 可能改变 caller、交易原子性、rollback、msg.value、block context、external calls 和 reentrancy。因而，Full-K1 和 Full-K5 的 Harness 运行是独立执行模型下的证据，不能默认替代 Original 多交易语义。[FIG:SEMANTIC_BOUNDARY]

此外，现有 replay gate 是静态门控，不是完整 native EVM replay。缺少 caller-controlled replay 时，地址相关 property、msg.sender 依赖和跨交易回滚行为仍需谨慎解释。未来应引入保持调用者和交易边界的回放设计，并把语义对齐作为单独研究问题。

### 7.5 Reproducibility

provenance 链使输入、命令、环境、原始输出和派生摘要之间可以相互追踪。checksum 用于完整性检查，evidence index 用于连接正文 claim、结果表和审计文件。其局限是：工件可追溯不等于独立复现已经完成；环境中未记录或未锁定的外部依赖仍可能影响复现。

历史随机对照结果由于 provenance unresolved 被 quarantine，不作为新论文主张。保守处理会减少可用比较材料，但可以避免把来源不完整的结果当作新的证据。

### 7.6 Baseline comparison limitations

本文没有完成与 SMARTIAN、MuFuzz、IR-Fuzz、Harvey、ConFuzzius 或其他工具的完整、同语义、同预算、同 benchmark 工具级比较。相关工作部分只进行定位，不据此给出广泛 superiority claim。Original 是本文公开任务中的方法配置，不等同于所有现有 fuzzer 的统一 baseline；Full-K1 和 Full-K5 也不等同于 Original 的交易长度变体。

这些限制意味着本文的结论应保持在 PHS 作为 Echidna 外部预处理层、受控机制证据和有限公开任务描述性运行记录的范围内。[TABLE:THREATS_MITIGATION]

## 8 相关工作

Property-based smart-contract fuzzing 以可执行 property 为目标组织输入生成和反例检查，Echidna 是本文下游执行语境的候选代表。[CITE:ECHIDNA] 本文与该方向的关系是接口组合：PHS 在执行前生成候选 Harness，Echidna 继续负责参数 fuzz 和 property 执行。本文不把 PHS 描述为替代 Echidna 的完整 fuzzer。

Stateful fuzzing 和 transaction sequence generation 关注多次调用、持久状态和调用顺序。Harvey、ConFuzzius 以及其他待核验工作可用于补充这一背景。[CITE:HARVEY] [CITE:CONFUZZIUS] 本文不声称首次提出状态依赖、交易序列或重复调用；PHS 的差异在于以显式 property 为方向，通过外部 preprocessing 组织候选序列并生成 wrapper Harness。

Static/dynamic data-flow guided fuzzing 以及 invocation ordering、branch revisiting 研究，提供了减少无关探索和推进目标分支的相关视角。SMARTIAN、IR-Fuzz 等工作需要在核验原始来源后准确描述。[CITE:SMARTIAN] [CITE:IR_FUZZ] Sequence-aware mutation 方向中的 MuFuzz 也可作为邻近工作。[CITE:MUFUZZ] PHS 与这些方法的主要区别在接口位置：PHS 是 fuzzer 外部的 property-directed preprocessing，输出可解释的 Top-K Harness 候选；它不是对这些工具的替代，也未在本文中完成公平的工具级实验比较。

符号执行辅助分析和语言模型辅助交易推理构成另一组相关方向。SmarTest、Mythril、Oyente 和 ILF 等候选工作需要人工核验其原始论文、方法范围和术语使用。[CITE:SMARTEST] [CITE:MYTHRIL] [CITE:OYENTE] [CITE:ILF] 本文只使用 lightweight value evidence，不将其等同于完整符号执行、精确约束求解或语言模型推理。

ContractFuzzer、sFuzz、EthPloit 等候选工作可以帮助补充智能合约模糊测试和输入生成的历史背景。[CITE:CONTRACTFUZZER] [CITE:SFUZZ] [CITE:ETHPLOIT] SmartBugs、SmartBugs Curated 和 Daedaluzz 则与 benchmark、数据集或测试资源组织相关。[CITE:SMARTBUGS] [CITE:SMARTBUGS_CURATED] [CITE:DAEDALUZZ] 正式论文应根据原始来源核验每项工作的准确角色，不把 benchmark 名称、任务来源和本文四个 supported public tasks 混为一谈。

最后，reproducibility 和 artifact evaluation 工作为 provenance、manifest、checksum 和证据索引提供报告背景。[CITE:ARTIFACT_EVALUATION] 本文把这些机制用于审计描述性结果，而不是将工件完整性转换为安全性结论。完整的引用、BibTeX、年份和 venue 待人工从原始来源补齐。

## 9 结论

本文提出属性定向 Harness 合成方法（PHS），把显式 safety property 转换为 property-directed 的候选 transaction sequence，并通过属性相关状态提取、反向写入筛选、有界重复、轻量值证据和可解释 Top-K 排序生成 Solidity wrapper Harness。PHS 作为 Echidna 之前的外部预处理层工作，不修改 Echidna core；参数仍由下游模糊执行。

在四个受控机制 benchmark 上，本文分别观察了依赖、值、重复和排序相关证据；在四个 supported public tasks 上，以 Original、Full-K1、Full-K5、10 个 seed 和 120 次运行给出描述性结果。结果包含 118 次 falsified 和 2 次 budget_exhausted，120/120 次 artifact complete、120/120 次 checksum pass，且 parser/status mismatch、startup_error、unknown_error 和 incomplete 均为 0。budget_exhausted 不表示 property passed 或 contract safe。

本文结论仍受公开任务数量、caller 语义、static gate 能力和 Harness/Original 执行模型差异限制。未来工作包括扩展更多 public benchmark，实现 caller-controlled replay，开展公平的外部 baseline 比较，细化 Harness 与 Original 的语义对齐，并在更大规模真实合约上评估方法。历史结果只有在 provenance 得到补全后才适合重新讨论；这些工作不应被当前有限证据提前替代。[TABLE:THREATS_MITIGATION]
