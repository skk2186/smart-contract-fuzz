# 6 实验评估（修订稿）

## 6.1 研究问题与评价设计

评价围绕四个问题展开：

- **RQ1：** PHS 的属性定向序列规划能否在受控障碍上产生预期候选，并体现 Property、Value、Repeat 与 Top-K 的作用？
- **RQ2：** PHS 生成的 Harness 能否在声明的 wrapper execution model 下完成公开属性任务的生成、执行、解析和 provenance 留存？
- **RQ3：** 在预登记的 supported public tasks 上，Original、Full-K1 和 Full-K5 的观察结果如何？
- **RQ4：** 哪些执行语义限制了这些结果的解释？

前两个问题关注机制和运行链，第三个问题给出范围内比较，第四个问题说明从结果到结论之间的边界。这样的设计将“候选是否可解释”和“运行是否可追溯”与“某一配置观察到多少反例”分开报告。

## 6.2 实验对象与配置

机制实验使用四个 Formal controlled benchmarks：NoisyFourStep、BranchValue、RepeatedCall 和 ResetExample。它们分别构造无关路径、值方向冲突、必须重复调用以及 reset/Top-K 并列候选等障碍。由于障碍被有意隔离，这些合约用于验证机制行为，不用于代表真实合约生态。

公开评价纳入四个预登记的 supported public tasks：echidna-flags、echidna-multi、smartbugs-multifunc 和 smartbugs-onefunc。exercise2-access-control 由于依赖 msg.sender、owner equality、caller alternation 和 address-keyed mapping，保持 conditional，不进入 supported pooled 结果。其他内部候选不进入公开任务分母。

公开比较包含 Original、Full-K1 和 Full-K5 三种方法；每个任务使用 seed 1–10，每种方法 10 次，共 4 × 3 × 10 = 120 runs。Original 使用多交易配置，Harness 配置使用固定候选的 wrapper；记录的 testLimit 为 100000，timeout 为 30 秒，workers 为 1，stopOnFail 为 true，运行模式为 property。工具记录包括 Python 3.11.15、Slither 0.11.5、Echidna 2.3.2、相应的 solc 0.8.20 或 0.4.25，以及方法版本 Full-v1.0.1-compat。

Original 的 seqLen=4 与 Harness 的 seqLen=1 位于不同调用层次。前者表示 Echidna 的多交易搜索，后者表示一次外层 wrapper 调用，wrapper 内可能包含多个目标函数调用。因此，这些配置不构成等价的交易长度或等量工作定义。

## 6.3 指标和状态解释

每次运行使用互斥状态分类。falsified 表示在相应执行模型、输入和预算内观察到属性反例；budget_exhausted 表示在声明预算内没有观察到反例；startup_error、unknown_error 和 incomplete 分别表示启动、未知错误和不完整运行。按任务和方法报告 runs、falsified、budget_exhausted 及 observed falsification rate，其中 observed falsification rate 为 falsified/runs。

该比率是给定任务、配置和 seed 范围内的描述性统计，不是安全概率、属性通过率或跨生态泛化估计。尤其是，budget_exhausted 不能被解释为 property passed、contract safe 或漏洞不存在。artifact completeness、checksum pass 和 parser/status agreement 衡量结果链是否完整，不衡量合约安全性。

## 6.4 RQ1：受控机制结果

四个主要受控基准的候选路径从 Dependency 阶段合计 92 条减少到 Property 阶段的 31 条，减少 61 条，即 66.30%。NoisyFourStep 的候选从 30 条缩减到 3 条，目标路径成为唯一 Top-1。这说明从属性读取状态反向筛选相关写入，能够去除部分明显无关路径，但候选数量本身不能代表完整的模糊测试工作量。

BranchValue 中，Property-K1 为 0/30，而 Value-K1 和 Full-K1 均为 30/30，表明简单值方向证据可以区分读写结构相同但状态方向不同的路径。RepeatedCall 中，不允许重复访问的配置为 0/30，完整方法为 30/30，说明 bounded repeat 能够覆盖该受控目标所需的重复调用。ResetExample 则显示，reset 干扰会扩大同分候选集合，局部值证据可以为 Top-K 选择提供额外信息。

这些观察支持 PHS 组件对预先声明障碍的方向性作用。由于基准经过专门设计，结论限于机制层面，不外推到一般合约或工具性能排序。

## 6.5 RQ2：运行链完整性

四个 supported public tasks 的 120 个预登记运行全部完成。120/120 个运行具有完整的 manifest、command、environment、raw、parsed、summary、status 和 checksum 产物；120/120 checksum pass；parser/status mismatch 为 0；startup_error、unknown_error 和 incomplete 均为 0。

这说明，在声明配置和 wrapper execution model 下，PHS 的生成、编译、执行、解析、状态分类和 provenance 链条是可审计的。该结论只涉及运行链的完整性，不等于完整 native EVM replay，不等于 Original 与 Harness 的语义一致，也不等于属性通过或合约安全。所有结果分组的 main_table_usable=conditional，后续使用仍需结合任务级语义复核。

## 6.6 RQ3：描述性比较

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

总体共有 118 个 falsified 和 2 个 budget_exhausted。两个 budget_exhausted 分别出现在 echidna-multi/Original/seed 1 和 echidna-multi/Full-K5/seed 7。它们只表示在各自执行模型和预算内没有观察到反例。echidna-flags、smartbugs-multifunc 和 smartbugs-onefunc 的三种配置均为 10/10；差异集中在 echidna-multi 的观察状态上。

因此，本表应被读作四个任务、三种配置和 10 个 seed 下的 descriptive comparison。它可以说明三种配置在当前任务上都产生了可分类的观察结果，也可以展示个别任务组的计数差异；但样本只有四个任务，每组只有 10 个 seed，且 Harness 与 Original 的调用者、交易边界和回滚范围不同。本文不使用 Total calls 作为跨配置的工作量指标，也不把观察到的计数差异扩展为更宽的性能结论。

## 6.7 RQ4：语义边界

Original multi-transaction model 中，多笔交易具有独立边界，sender 可能变化，一笔交易失败通常只回滚当前交易。wrapper execution model 中，候选调用在一次外层调用内连续执行，目标函数通常看到同一个 Harness caller，某一步 revert 可能影响整个 wrapper。msg.value、payable 行为、block.timestamp、block.number、external call、reentrancy、constructor/deployer 和 address-keyed state 也可能产生差异。

因此，Harness 下观察到的 falsified 应解释为 wrapper 模型下的反例，而不是自动转换为 Original 多交易语义下的同一反例。exercise2-access-control 对 caller 和地址映射敏感，必须保持 conditional，并在单独的 caller-controlled replay 中比较 same-caller 与 alternating-caller。静态 gate 只能作为适用性筛查，不能替代完整 native replay。

## 6.8 小结

RQ1 的结果表明，PHS 的组件在受控障碍上呈现预期的方向性行为；RQ2 表明，四个 supported public tasks 的 120 个运行具有完整可审计的产物链；RQ3 给出了 118 falsified 与 2 budget_exhausted 的任务级描述性比较；RQ4 说明这些结果必须在 wrapper 与多交易模型的语义边界内解释。由此形成的是窄定位、可追溯的机制和运行证据，而不是对真实生态、不同执行模型或未完成外部基线的广泛结论。
