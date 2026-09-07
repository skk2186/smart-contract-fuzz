# PHS：面向有状态智能合约属性模糊测试的 Harness 合成方法

## 摘要

有状态智能合约中的安全属性往往需要一组具有特定顺序、重复访问模式或参数条件的交易才能被触发。若完全依赖随机交易序列，搜索可能被与目标属性无关的状态写入和不可行前缀分散。本文提出属性定向 Harness 合成方法（Property-directed Harness Synthesis，PHS）：从显式 safety property 读取的状态变量出发，反向筛选相关写入，构造 transaction sequence 候选，并结合 bounded repeat、轻量 value evidence 和可解释的 Top-K 排序，生成供 Echidna 继续探索参数与属性的 Solidity wrapper Harness。PHS 不修改 Echidna core，而是作为其前处理步骤。我们在针对特定障碍设计的 Formal controlled benchmarks 上考察属性过滤、值方向匹配、重复访问和 Top-K 选择；随后在四个预登记的 supported public tasks 上，对 Original、Full-K1 和 Full-K5 进行 seed 1–10 的 120-run 描述性比较。该比较包含 118 个 falsified 和 2 个 budget_exhausted，120/120 个运行具有完整产物链，120/120 通过 checksum，且未观察到 parser/status mismatch、startup_error、unknown_error 或 incomplete。结果支持受控机制证据、运行链可审计性和声明范围内的描述性观察，但不支持超出任务与执行模型的效果推断。生成的 Harness 使用 wrapper execution model，与 Original multi-transaction model 在 caller、transaction atomicity 和 rollback scope 等方面存在差异；budget_exhausted 仅表示在给定预算内没有观察到反例，不表示属性通过或合约安全。

## 关键词

智能合约；有状态模糊测试；属性模糊测试；property-directed；Harness synthesis；transaction sequence；Top-K；Echidna；语义边界；可复现性

## 1 引言

智能合约的许多安全性质只有在状态经过一系列操作后才会显现。一次调用可能只是写入前置状态，后续调用才读取并更新它；某些目标还要求同一函数重复执行，或要求输入依次满足多个 require 条件。因而，属性模糊测试面对的不是单纯的参数生成问题，而是交易顺序、状态积累和参数约束共同决定的可达性问题。

Echidna 等属性模糊测试工具以显式 safety property 作为判定接口，不断执行合约调用并寻找使属性返回假的轨迹。这种工作流能够直接表达不应发生的状态关系，但当合约包含大量无关函数、reset 路径或多步前置条件时，随机交易序列会把探索预算分散到大量低相关候选上。仅凭一般状态读写关系也难以得到完整答案：一个函数虽然写入了属性读取的变量，写入值却可能与目标方向相反；一条依赖路径虽然结构上成立，却可能在中途条件处失败；必须重复访问的函数也会被只允许单次访问的路径生成器遗漏。

本文提出属性定向 Harness 合成方法（Property-directed Harness Synthesis，PHS）。PHS 位于 Echidna 之前，将“哪些调用顺序值得优先检查”作为一个可审计的前处理问题。它从显式属性读取的状态变量出发，沿读写关系反向筛选相关写入，构造候选 transaction sequence；随后在声明的上限内加入必要的 bounded repeat，并使用简单常量写入和条件约束作为 lightweight value evidence。候选根据 Property、Repeat 和 Value 等证据进行 interpretable Top-K 排序，再被写入 Solidity wrapper Harness。生成后的候选顺序是固定的，而参数和属性探索仍交由 Echidna 完成。因此，PHS 不改变 Echidna core，也不试图取代既有属性模糊测试器。

这一设计关注的是组合方法的解释性。属性相关过滤用于去除明显无关的状态路径；bounded repeat 用于表达必须多次访问的目标；value evidence 用于区分读写关系相同但写入方向不同的候选；Top-K 用于在 Harness 大小有限时保留少量可检查的备选路径。候选的中间产物记录依赖、重复、值约束、排序和最终 Harness，使研究者能够从一条测试路径回溯到其选择依据。

本文以两类证据评价 PHS。第一类是针对单一障碍设计的 Formal controlled benchmarks，分别考察无关路径、值方向、重复访问和 reset/Top-K 的机制行为。此类合约适合验证组件是否响应预先声明的问题，但不被视为真实合约生态的代表。第二类是四个预登记的 supported public tasks。在 Original、Full-K1 和 Full-K5 三种配置下，每个任务使用 seed 1–10，共 120 个运行。该批次包含 118 个 falsified 和 2 个 budget_exhausted；120/120 个运行保留完整产物，120/120 checksum pass，parser/status mismatch、startup_error、unknown_error 和 incomplete 均为 0。这里的结果是任务级、配置级的描述性观察。

解释这些结果时必须区分 Original multi-transaction model 和 PHS 生成的 wrapper execution model。Original 由多笔独立交易组成，sender 可能变化，一笔交易失败通常只影响该笔交易；wrapper 则可能在一次外层调用中连续执行多个目标函数，目标调用通常来自同一个 Harness caller，某一步失败也可能影响整个 wrapper。因此，固定成功路径的状态一致或运行链完整都不能自动转化为两种执行模型完全相同的结论。exercise2-access-control 因 caller 和 address-keyed mapping 依赖保持 conditional，不进入四个 supported public tasks 的 pooled 结果。

本文的贡献包括：第一，提出 PHS，将 property-directed preprocessing、external Harness synthesis、bounded repeat、lightweight value evidence 和 interpretable Top-K 组织为一条可追溯流程；第二，在受控 Formal benchmarks 上给出组件层面的机制证据；第三，设计覆盖候选、生成、运行、解析、状态和 checksum 的 provenance 链；第四，在四个 supported public tasks 上给出 120-run 的描述性评价，并将 Harness 与 Original 的语义边界纳入解释框架。本文不把状态依赖、交易序列、重复调用或值引导本身宣称为新的基础问题，而是聚焦这些线索在属性定向外部 Harness 合成中的组合与审计。

## 2 背景

### 2.1 属性模糊测试与 safety property

属性模糊测试把程序行为压缩为可反复检查的属性。对智能合约而言，属性通常读取一个或多个状态变量，并在状态不满足预期关系时返回假。模糊器生成交易、参数和执行上下文，直到观察到反例，或在声明预算内没有观察到反例。

本文将 falsified 定义为在给定执行模型、输入和预算内观察到属性反例；将 budget_exhausted 定义为在预算内没有观察到反例。后者不是 property passed、contract safe 或漏洞不存在的证明。这个区分同时适用于 Original 和 Harness 结果。

### 2.2 状态读写与 transaction sequence

函数可以读取或写入状态变量。若函数 A 写入 s、函数 B 读取 s，则 A 可能是到达 B 所需状态的候选前驱。由此可以建立基础 transaction sequence，例如 register -> deposit -> withdraw。然而，读写依赖只是必要线索：写入值可能方向错误，reset 可能清除中间状态，目标也可能需要重复访问同一函数。

本文使用 bounded repeat 表示在声明的访问上限内允许函数重复出现，例如 deposit -> deposit 或 run -> run。它不是无限展开序列。value evidence 来自简单常量写入和 require 条件，用于提供局部的值方向匹配信息；它不是完整符号执行。

### 2.3 Harness 与 Top-K

Harness 是用于测试的外部合约或调用包装层。PHS 将候选 transaction sequence 写入 Solidity wrapper：候选顺序在生成阶段固定，Echidna 后续对 wrapper 参数和属性继续 fuzz。Top-K 表示写入 Harness 的候选条目数量：K1 保留一条候选，K5 保留五条候选。K1/K5 不是 Original 中等价的交易长度，也不代表相同的底层工作量。

可解释排序使研究者能够检查候选为何被保留：它是否触及属性相关状态，是否包含必要的重复，是否匹配已知的简单值条件，是否存在冲突或 unknown 条件，以及它是否位于候选池前 K 名。

### 2.4 Original 与 wrapper execution model

Original multi-transaction model 中，Echidna 探索多笔独立交易。每笔交易通常有自己的边界，sender 可能变化，某笔交易失败通常只回滚当前交易。交易间的 msg.value、区块环境和外部交互时机也可能不同。

wrapper execution model 则在一次外层 wrapper 调用中连续执行候选函数。目标调用通常由同一个 Harness 地址发起，多个调用可能共享一次 transaction atomicity；某一步 revert 可能导致整个 wrapper 回滚。当前生成器也没有通用的逐步 msg.value 或不同 sender 模拟。因此，caller、transaction atomicity、rollback scope、payable、区块环境、external call 和 reentrancy 都需要单独审计。

## 3 动机

考虑一个属性要求最终状态 target 为真。合约中有初始化函数、目标函数、无关状态写入函数和 reset 函数。只根据一般读写关系建立候选时，初始化函数和目标函数可能被保留，但无关函数也会进入候选池。NoisyFourStep 这个受控例子中，Dependency 阶段有 30 条候选，属性相关过滤后只保留 3 条，目标路径成为唯一 Top-1。这说明 property-directed filtering 可以减少明显无关路径，但不能由此推出端到端的运行效率改善。

仅有依赖关系也无法区分值方向。假设两个分支都写入属性读取的 flag，一个写入 1，一个写入 0，而后续目标需要 1。两条路径的读写图相同，BranchValue 的受控结果显示 Property-K1 可能为 0/30，加入值方向证据的 Value-K1 和 Full-K1 为 30/30。这里的 value evidence 只使用简单局部条件，不声称解决复杂算术或动态映射。

重复访问构成另一种障碍。若第一次 deposit 建立状态，第二次 deposit 才能使累计值达到目标，禁止函数重复就无法生成必要路径。RepeatedCall 的受控对照中，不允许重复的配置为 0/30，而完整方法为 30/30。bounded repeat 因此用于表达预先声明的重复需求，同时通过上限控制候选增长。

重复扩展和 reset 还可能制造较大的同分候选集合。ResetExample 表明，单靠依赖或长度不能可靠区分“建立状态后正确使用”和“建立后又被清除”的路径，简单值证据可以提供额外区分。因此，PHS 把 Property、Repeat、Value 和 Top-K 组合成一个可检查的候选规划流程。

上述例子都是 controlled benchmarks，用来隔离单个障碍，不代表真实合约生态，也不覆盖调用者、资金、时间、外部调用和重入等语义。真实任务上的 Harness 结果必须结合 Original 与 wrapper execution model 的边界解释。

## 4 方法

### 4.1 总体流程

PHS 输入 Solidity 合约及依赖、显式 Echidna safety property、编译和测试配置，以及重复上限和 Top-K 参数。输出是带有来源和证据的 transaction sequence 候选，以及由候选生成的 Solidity wrapper Harness。Echidna 继续负责参数探索和属性判定。

处理顺序为：提取属性相关状态，生成函数读写摘要，反向过滤相关写入，构造基础候选，按上限加入必要重复，提取局部值证据，进行可解释排序，选择 Top-K 并生成 Harness。

### 4.2 Property-related state extraction

分析器从 safety property 中识别直接读取的状态变量，记录属性名称、变量和可见的比较方向。随后为函数生成读取集合、写入集合、可见性、签名和简单条件摘要。复杂别名、动态索引、外部调用和环境变量若不能可靠解析，应保留 unknown 或风险标记，不能默认为不相关。

### 4.3 Backward filtering of relevant writes

给定属性读取状态，PHS 从最终读取点向前追溯可能写入这些状态的函数。若 A 写入的状态被 B 读取，或 A 的写入沿已记录依赖影响属性，则 A 可作为候选前驱。无法连接到目标属性状态的路径被过滤，能够建立前置状态的路径被保留。

过滤结果保存 retained path 数量、被移除路径和每条路径的依赖证据。在四个主要受控基准中，Dependency 候选合计 92 条，Property 阶段保留 31 条，减少 61 条。这个指标描述候选空间，不自动表示端到端运行效率。

### 4.4 Candidate transaction-sequence construction

PHS 沿过滤后的函数图，从状态建立函数扩展到属性观察点，保存函数顺序、签名、路径长度、涉及状态、依赖关系和已知失败条件。已知 require 条件用于可行性标记，无法判断的条件保留为 unknown。候选顺序由生成器固定，但函数参数不被静态分析器固定为单一值，Echidna 仍可以 fuzz wrapper 参数。

### 4.5 Bounded repetition

当目标状态需要同一函数多次访问时，PHS 在预先声明的上限内扩展重复路径，并记录重复函数、访问次数和原因。该机制能够表达 deposit -> deposit 或 init -> run -> run，但不允许无限复制，也不应在缺少证据时单纯为了增加候选数量而扩展。

### 4.6 Lightweight value evidence

分析器从常量赋值、简单算术和入口 require 中提取局部值证据。若前置函数的写入和后续函数的条件方向匹配，候选获得匹配标记；若写入方向冲突，则获得冲突标记或较低优先级。unknown 不能被改写为满足，复杂跨合约和环境值也不在该轻量证据的保证范围内。

### 4.7 Interpretable Top-K ranking

排序首先要求候选与属性相关状态相连，然后综合必要重复、值条件、已知冲突、可行性和路径信息。结果保存 display rank、并列或不确定标记，便于人工区分严格排序与同分集合。K1/K5 只是 Harness 条目数量，不是等价交易长度；Top-K 的变化只能作候选覆盖和描述性结果解释。

### 4.8 Solidity Harness synthesis

生成器为每条选中候选生成外部 Harness，并将候选函数顺序写入 wrapper。wrapper 暴露 Echidna 可调用的入口，把参数传给目标函数，并保留候选 JSON、生成状态和编译记录。固定候选顺序把部分序列搜索外置，但参数和属性探索仍由 Echidna 完成。

### 4.9 Semantic boundary

Original multi-transaction model 与 Harness wrapper execution model 可能在 msg.sender、caller alternation、transaction atomicity、rollback scope、msg.value、payable、block.timestamp、block.number、external call、reentrancy、constructor/deployer 和 address-keyed state 上不同。Harness 内部连续调用失败时，可能回滚整个 wrapper；Original 中通常只回滚当前交易。

因此，Harness falsified 的含义是在当前 wrapper 模型下观察到反例，而不是自动证明 Original 多交易模型下有完全相同的反例。固定成功路径的最终属性相关状态一致也只能支持窄条件下的可重放性。依赖 owner 或 caller 的任务需要单独的 caller-controlled replay，不能默认纳入 supported pooled 结果。

## 5 实现

实现输入包括合约、依赖、property、配置、编译器、重复上限和 Top-K。分析器依次生成读写摘要、基础依赖路径、属性相关路径、重复感知路径和值约束；Harness 生成器将选中候选转换为 Solidity wrapper。runner 负责预检、编译、执行、原始日志保存、解析和汇总。

每个运行目录保留 manifest.tsv、command.txt、environment.txt、generated、raw、parsed、summary、status 和 checksum。manifest 记录 run id、commit SHA、方法版本、benchmark、property、配置、编译器、seed、testLimit、timeout、workers 和 stopOnFail；command/environment 记录实际命令、时间和工具版本；raw 保留不可手工编辑的原始输出。

状态分类包括 falsified、budget_exhausted、startup_error、unknown_error 和 incomplete。budget_exhausted 表示预算内没有观察到反例，不等于 property passed 或 contract safe。parser/status mismatch 是阻塞项，不能在论文提升前忽略。checksum 让输入和关键输出可以逐文件复核，完整 artifact chain 只证明 provenance 可追溯，不证明安全。

历史控制实验若 provenance 不完整，则保留在 quarantine，不作为新的论文主张或 pooled 统计。其他开发材料、启动检查和无法证明完整执行的历史材料同样不应悄然进入主结果。

## 6 实验评估

### 6.1 研究问题与实验范围

RQ1 询问属性定向 sequence planning 是否能在受控障碍上产生预期候选并体现 Property、Value、Repeat 与 Top-K 的作用。RQ2 询问生成 Harness 的执行、解析和 provenance 链是否完整。RQ3 比较 Original、Full-K1 和 Full-K5 在预登记 supported public tasks 上的观察结果。RQ4 说明语义边界如何限制解释。

Formal controlled benchmarks 包括 NoisyFourStep、BranchValue、RepeatedCall 和 ResetExample，分别隔离无关路径、值方向、重复访问和 reset/Top-K 障碍。公开范围只包括 echidna-flags、echidna-multi、smartbugs-multifunc 和 smartbugs-onefunc 四个 supported public tasks。exercise2-access-control 因 caller 和 address-keyed mapping 依赖保持 conditional；内部 AlternativePath、MultiProperty 和 ThreeStep 材料不进入分母。

公开比较包括 Original、Full-K1 和 Full-K5，seed 为 1–10，每组 10 次，共 120 runs。记录配置为 testLimit 100000、timeout 30 秒、workers 1、stopOnFail true 和 property mode；工具 provenance 包括 Python 3.11.15、Slither 0.11.5、Echidna 2.3.2、相应 solc 0.8.20 或 0.4.25。Original 的 seqLen=4 与 Harness 的 seqLen=1 位于不同调用层次，不能当作等价交易长度。

### 6.2 RQ1：受控机制证据

四个主要受控基准的候选从 Dependency 合计 92 条降至 Property 的 31 条，减少 61 条，即 66.30%。NoisyFourStep 从 30 条降至 3 条，并使目标路径成为唯一 Top-1。BranchValue 中 Property-K1 为 0/30，Value-K1 与 Full-K1 为 30/30，说明值方向可以补充纯依赖关系。RepeatedCall 中不允许重复为 0/30，完整方法为 30/30，说明有界重复能够保留该受控目标需要的路径。ResetExample 表明值证据可以帮助区分 reset 干扰造成的同分候选。

这些结果支持“组件对预先声明的障碍具有可观察作用”的窄结论。受控合约规模小、障碍经过专门设计，因此结论停留在机制层面。

### 6.3 RQ2：运行链完整性

120 个预登记运行全部完成。120/120 个运行保留 manifest、command、environment、raw、parsed、summary、status 和 checksum；120/120 checksum pass；parser/status mismatch 为 0；startup_error、unknown_error 和 incomplete 均为 0。由此可以确认，在声明配置和 wrapper execution model 下，生成、编译、执行、解析、状态分类和 provenance 链是完整可审计的。

该结果只表示运行链完整，不表示 native EVM replay 已完成，也不证明 Original 与 Harness 语义等价。静态 gate 只是适用性筛查，不能替代 native replay。所有分组行的 main_table_usable 仍为 conditional。

### 6.4 RQ3：描述性比较

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

总体结果为 118 个 falsified 和 2 个 budget_exhausted。两个预算耗尽运行分别是 echidna-multi/Original/seed 1 和 echidna-multi/Full-K5/seed 7。它们都只表示在给定预算内没有观察到反例，不是属性通过。echidna-flags、smartbugs-multifunc 和 smartbugs-onefunc 上三种方法均为 10/10；差异集中在 echidna-multi 的观察状态。

因此，该表只支持四个任务、seed 1–10 范围内的 descriptive comparison。本文不报告 p-value，不将观察差异写成统计结论，不使用 Total calls 作为跨配置的工作量指标，也不将四个任务写成真实生态代表样本。

### 6.5 RQ4：语义边界

Original 的多笔交易可能由不同 sender 发起，某笔失败通常只回滚当前交易；Harness 在一次 wrapper 调用内连续执行候选函数，目标调用通常来自同一个 Harness caller，一步 revert 可能影响整个 wrapper。不同模型还可能在 msg.value、payable、区块环境、external call、reentrancy 和 address-keyed state 上不同。

exercise2-access-control 依赖 msg.sender、owner equality、caller alternation 和 address-keyed mapping，因而不能进入 supported pooled 结果，必须单独完成 caller-controlled replay。固定路径上的最终属性相关状态一致也不能证明完整搜索过程或失败边界等价。静态 gate 不是完整 native EVM replay。

综合来看，评价支持 PHS 在受控障碍上产生可解释的属性定向候选，并在四个 supported public tasks 上完成 120-run 的可审计描述性比较；它不支持安全概率、生态泛化、等价或跨模型工作量结论。

## 7 有效性威胁

内部效度受到配置不对称、任务适配和有限 seed 的影响。Original 与 Harness 使用不同调用层次，两个 SmartBugs 任务保留 Solidity 0.4.x unchecked arithmetic，另两个任务使用 solc 0.8.20。120 个运行全部保留且审计通过，降低了缺失产物和事后筛选威胁，但不能消除执行模型差异。budget_exhausted 必须保留为预算内未观察到反例。

外部效度最主要的限制是 public benchmark 只有 4 个 supported。它们规模小、属性数量有限，不能代表真实合约生态。exercise2-access-control 是 conditional，PUB06–PUB08 是 excluded 内部材料，均不进入 supported pooled。未来应优先补充不同来源、不同状态和调用者语义、更大规模的 public benchmark，而不是只增加同一任务的 seed。

构念效度方面，falsified 是当前执行模型下的反例观察，budget_exhausted 不是安全判定；observed falsification rate 只是 falsified/runs 的描述性比率。artifact completeness、checksum pass 和 parser/status agreement 衡量证据链，不是安全性。候选减少不能自动解释为模糊测试运行效率改善，Total calls 也不用于跨模型比较，因为不同方法的计数层次不同。静态 gate 不是 native replay。

语义效度方面，Harness wrapper 与 Original multi-transaction model 在 caller、transaction atomicity 和 rollback scope 上可能不同，并可能受 msg.value、区块环境、external calls、reentrancy 和 address-keyed state 影响。固定成功路径的有限一致性不能升级为完整搜索过程等价。尤其是 access-control 任务必须进行 caller-controlled replay。

可复现性方面，方法名称、方法版本、commit SHA、配置、编译器、seed、预算、命令、环境、原始日志、解析结果、状态文件和 checksum 均应保留。未来运行需使用独立目录，不覆盖冻结证据。历史控制实验若 provenance 不完整，继续 quarantine，不用于新主张或 pooled 统计。

最后，本文没有完整可比的 SMARTIAN、MuFuzz 或 IR-Fuzz 工具级实验。现有 SMARTIAN 材料只涉及两个简单整数目标，不能支持竞品排名；Original 也不是与 Harness 具有完全相同语义的等量基线。因此，本文的结论严格限制为窄定位的机制、可审计性和描述性比较。

## 8 相关工作

本节的精确论文、版本和 BibTeX 需要后续人工核验，以下只给出定位框架。

### 8.1 Echidna 与属性模糊测试

Echidna 代表以显式属性为中心的智能合约模糊测试工作流。本文将其作为后续的执行和属性判定组件，在其之前生成 property-directed Harness。本文不替代 Echidna，也不修改 Echidna core。（待补引用：[CITE-ECHIDNA-PROPERTY]）

### 8.2 有状态模糊测试与交易序列生成

Stateful smart-contract fuzzing 和 transaction sequence generation 关注跨调用状态、多交易前缀及函数顺序。本文采用这些问题场景，但不声称首次提出状态依赖或交易序列生成。本文的范围更窄：以 property 读取状态为过滤起点，将候选路径外置为可审计 Harness，并使用 bounded repeat 与 Top-K 表达受控候选。（待补引用：[CITE-STATEFUL-FUZZING-1]、[CITE-SEQUENCE-GENERATION-1]）

### 8.3 数据流引导、调用排序与序列感知变异

Static/dynamic data-flow guided fuzzing、invocation ordering、branch revisiting 和 sequence-aware mutation 都可能利用依赖、状态反馈或序列上下文。本文使用静态读写摘要和简单 value evidence，但不等于完整动态反馈；有界重复也不等于通用变异核心。本文不声称首次提出重复调用、分支重访或调用排序。（待补引用：[CITE-DATAFLOW-STATIC]、[CITE-DATAFLOW-DYNAMIC]、[CITE-ORDER-REVISIT-1]）

### 8.4 符号与语言模型辅助的交易推理

Symbolic reasoning 和 language-model assisted transaction reasoning 可以利用约束或上下文帮助选择调用和参数。本文的 value evidence 只处理简单常量与 require 条件，没有声称完整符号求解或语言模型推理能力。这些方向可以作为未来替换或扩展候选排序信号。（待补引用：[CITE-SYMBOLIC-REASONING]、[CITE-LM-REASONING]）

### 8.5 本文的关系

| 方向 | 本文关系 |
|---|---|
| Echidna/property-based fuzzing | 作为后续执行器；PHS 提供 external preprocessing |
| Stateful fuzzing | 采用跨调用状态问题，不声称首次研究 |
| Transaction sequence generation | 以属性相关状态反向过滤并输出候选 |
| Static/dynamic data-flow | 使用静态读写和局部值证据，范围较窄 |
| Invocation ordering/branch revisiting | 以 bounded repeat 和 Top-K 表达受控候选 |
| Sequence-aware mutation | 固定候选顺序，参数探索仍交给 Echidna |
| Symbolic/language-model reasoning | 当前不是完整求解或语言模型推理系统 |

PHS 与上述方向的差异组合是 property-directed preprocessing + external Harness synthesis + interpretable Top-K + semantic boundary audit。重点是组合的可解释性、产物 provenance 和语义边界，而不是对状态依赖、重复调用、交易序列、分支重访或值引导提出绝对首创主张。

## 9 结论

本文提出 PHS，一种面向有状态智能合约属性模糊测试的 transaction sequence Harness synthesis 方法。PHS 从显式 safety property 读取的状态变量出发，反向过滤相关写入，构造候选序列，加入 bounded repeat 和轻量 value evidence，并以 Top-K 规则生成 Solidity wrapper Harness。候选顺序由前处理固定，参数和属性探索仍由 Echidna 完成，因此 PHS 是 Echidna 之上的外部 preprocessing。

Formal controlled benchmarks 对无关路径、值方向、重复访问和 reset/Top-K 障碍提供了范围内机制证据。四个 supported public tasks 的 Original、Full-K1 和 Full-K5 共完成 120 个运行，其中 118 个 falsified、2 个 budget_exhausted；120/120 artifact set 完整，120/120 checksum pass，parser/status mismatch、startup_error、unknown_error 和 incomplete 均为 0。budget_exhausted 只表示在声明预算内没有观察到反例，不表示属性通过或合约安全。

这些结果不支持超出当前任务和执行模型的效果推断。Original multi-transaction model 与 wrapper execution model 在 caller、transaction atomicity、rollback scope、value、区块环境和 external-call 语义上可能不同；exercise2-access-control 继续保持 conditional，历史控制实验中 provenance 不完整的材料继续 quarantine。

未来工作包括更多 public benchmark、caller-controlled replay、更公平的外部 baseline、更精细的 Harness/Original 语义对齐，以及面向更大真实合约的规模记录。所有扩展都应保留独立 provenance，并与当前证据分开解释。
