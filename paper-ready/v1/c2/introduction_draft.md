# 1 Introduction（中文草稿）

智能合约的安全行为通常不是由单次函数调用决定的。一个属性可能只在一组状态更新按特定顺序完成、某个函数被重复调用、或中间参数满足若干 `require` 条件之后才会被违反。例如，合约可能需要先注册、再存款、再授权，最后执行提款；也可能需要先建立计数器，再重复调用同一入口，使一个算术状态进入危险区域。对这类问题而言，模糊测试不仅要寻找参数，还要寻找能够到达目标状态的交易序列。

属性模糊测试为这一问题提供了清晰的判定接口。研究者可以用一个显式的 safety property 描述不应发生的状态，例如某个余额关系、计数器不变量或状态标志组合。模糊器则不断生成输入和调用，尝试使属性返回假。Echidna 是这一工作流中的代表性属性模糊器：它能够在智能合约上执行交易序列并围绕属性寻找反例。本文不试图重新实现或替代 Echidna，而是研究一个位于其前面的候选序列规划步骤。

完全依赖随机交易序列时，搜索空间容易被与目标属性无关的路径稀释。合约中的函数可能写入错误状态、重置已经建立的状态，或者产生看似相关但实际无法满足后续条件的分支。只知道“某函数写入了某变量、另一函数读取了该变量”仍然不够：写入的值方向可能不对，正确路径可能需要同一函数出现两次，或者某些路径虽然满足变量依赖，却会在中间的 `require` 处失败。因此，问题不只是生成更长的序列，而是从属性所关心的状态出发，筛选更有解释性的候选路径。

本文研究一种面向属性的 transaction sequence Harness synthesis 方法。方法首先从显式 safety property 中提取被读取的状态变量，再根据状态读写关系反向筛选相关写入；在需要时，它允许有限次数的重复访问，并使用简单的常量写入和条件约束作为轻量 value evidence。候选路径随后依据 Property、Repeat、Value 等证据进行可解释排序，只保留 Top-K 条目并生成 Solidity wrapper Harness。生成的 Harness 将候选函数顺序固定下来，Echidna 仍然负责对 wrapper 参数和属性进行模糊探索。这样，方法把“哪些顺序值得尝试”的一部分工作外置为可审计的前处理，而不改变既有 fuzzer core。

这一设计的目标是机制可解释性，而不是宽泛的工具排名。我们在为特定障碍设计的 Formal controlled benchmarks 上分别考察属性过滤、值方向匹配、有界重复和 Top-K 选择。例如，NoisyFourStep 用无关状态路径展示属性过滤的作用，BranchValue 用相同依赖但不同值方向的分支展示 value evidence，RepeatedCall 检查重复访问是否能保留必要路径，ResetExample 则说明并列候选下的排序需要额外证据。这些合约有意隔离单一障碍，适合回答机制是否能够处理预先声明的问题，但不能代表真实合约生态。

为了检查实现链能否在公开属性任务上运行，我们进一步使用四个预登记的 supported public tasks，对 Original、Full-K1 和 Full-K5 进行 seed 1–10 的描述性比较，共 120 个运行。该批次有 118 个 `falsified` 和 2 个 `budget_exhausted`；所有运行均保留完整 artifact set，checksum 全部通过，且没有 parser/status mismatch、startup error、unknown error 或 incomplete run。这些数字用于说明在声明范围内的运行结果和可追溯性，不用于推断统计显著性、速度优势或生态泛化。特别是，`budget_exhausted` 只表示在给定预算内没有观察到反例，不表示 property passed 或合约安全。

本文还把 Harness 的语义边界作为评价对象的一部分。Original 是由多笔独立交易组成的执行模型，调用者可能在交易之间变化，单笔交易失败通常只影响该笔交易。生成的 Harness 则把候选顺序放进一次外部 wrapper 调用，目标函数通常看到同一个 Harness caller，多个调用可能共享一次交易的 atomicity，某一步失败也可能影响整个 wrapper。因而，Harness 结果必须在 wrapper execution model 下解释，不能写成与 Original 完全等价，也不能用不同层次的 `Total calls` 直接构造 speedup。`exercise2-access-control` 因 `msg.sender`、address-keyed mapping 和 caller alternation 保持 conditional，不进入四任务的 supported pooled 结果。

本文的贡献可以概括为四点：第一，给出位于 Echidna 之前的 property-directed Harness synthesis preprocessing 流程；第二，在受控 Formal benchmarks 上提供 Property、Value、Repeat 和 Top-K 的机制证据；第三，建立候选、Harness、运行状态和 checksum 均可检查的 provenance 链；第四，在四个 supported public tasks 上报告范围受限的 120-run 描述性结果，并显式审计 Harness/Original 的语义边界。本文不声称首次提出状态依赖、交易序列、重复调用或值引导，也不把 V1 描述为新的通用智能合约模糊测试器。
