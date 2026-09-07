# 1 引言（修订稿）

智能合约的许多安全性质只有在状态经过一系列操作后才会显现。一次调用可能只是写入前置状态，后续调用才读取并更新它；某些目标还要求同一函数重复执行，或要求输入依次满足多个 require 条件。因而，属性模糊测试面对的不是单纯的参数生成问题，而是交易顺序、状态积累和参数约束共同决定的可达性问题。

Echidna 等属性模糊测试工具以显式 safety property 作为判定接口，不断执行合约调用并寻找使属性返回假的轨迹。这种工作流能够直接表达“不应发生”的状态关系，但当合约包含大量无关函数、reset 路径或多步前置条件时，随机交易序列会把探索预算分散到大量低相关候选上。仅凭一般状态读写关系也难以得到完整答案：一个函数虽然写入了属性读取的变量，写入值却可能与目标方向相反；一条依赖路径虽然结构上成立，却可能在中途条件处失败；必须重复访问的函数也会被只允许单次访问的路径生成器遗漏。

本文提出属性定向 Harness 合成方法（Property-directed Harness Synthesis，PHS）。PHS 位于 Echidna 之前，将“哪些调用顺序值得优先检查”作为一个可审计的前处理问题。它从显式属性读取的状态变量出发，沿读写关系反向筛选相关写入，构造候选 transaction sequence；随后在声明的上限内加入必要的 bounded repeat，并使用简单常量写入和条件约束作为 lightweight value evidence。候选根据 Property、Repeat 和 Value 等证据进行 interpretable Top-K 排序，再被写入 Solidity wrapper Harness。生成后的候选顺序是固定的，而参数和属性探索仍交由 Echidna 完成。因此，PHS 不改变 Echidna core，也不试图取代既有属性模糊测试器。

这一设计关注的是组合方法的解释性。属性相关过滤用于去除明显无关的状态路径；bounded repeat 用于表达必须多次访问的目标；value evidence 用于区分读写关系相同但写入方向不同的候选；Top-K 用于在 Harness 大小有限时保留少量可检查的备选路径。候选的中间产物记录依赖、重复、值约束、排序和最终 Harness，使研究者能够从一条测试路径回溯到其选择依据。

本文以两类证据评价 PHS。第一类是针对单一障碍设计的 Formal controlled benchmarks，分别考察无关路径、值方向、重复访问和 reset/Top-K 的机制行为。此类合约适合验证组件是否响应预先声明的问题，但不被视为真实合约生态的代表。第二类是四个预登记的 supported public tasks。在 Original、Full-K1 和 Full-K5 三种配置下，每个任务使用 seed 1–10，共 120 个运行。该批次包含 118 个 falsified 和 2 个 budget_exhausted；120/120 个运行保留完整产物，120/120 checksum pass，parser/status mismatch、startup_error、unknown_error 和 incomplete 均为 0。这里的结果是任务级、配置级的描述性观察。

解释这些结果时必须区分 Original multi-transaction model 和 PHS 生成的 wrapper execution model。Original 由多笔独立交易组成，sender 可能变化，一笔交易失败通常只影响该笔交易；wrapper 则可能在一次外层调用中连续执行多个目标函数，目标调用通常来自同一个 Harness caller，某一步失败也可能影响整个 wrapper。因此，固定成功路径的状态一致或运行链完整都不能自动转化为两种执行模型完全相同的结论。exercise2-access-control 因 caller 和 address-keyed mapping 依赖保持 conditional，不进入四个 supported public tasks 的 pooled 结果。

本文的贡献包括：第一，提出 PHS，将 property-directed preprocessing、external Harness synthesis、bounded repeat、lightweight value evidence 和 interpretable Top-K 组织为一条可追溯流程；第二，在受控 Formal benchmarks 上给出组件层面的机制证据；第三，设计覆盖候选、生成、运行、解析、状态和 checksum 的 provenance 链；第四，在四个 supported public tasks 上给出 120-run 的描述性评价，并将 Harness 与 Original 的语义边界纳入解释框架。本文不把状态依赖、交易序列、重复调用或值引导本身宣称为新的基础问题，而是聚焦这些线索在属性定向外部 Harness 合成中的组合与审计。
