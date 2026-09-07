# C1 论文决策

## 明确判断

可以进入论文初稿，但投稿主张必须窄。

现有证据足以形成一版聚焦机制的 Evaluation：V1 作为面向 Echidna 的 property-directed Harness synthesis preprocessing，在受控 Formal benchmarks 上展示组件作用，并在四个预登记 supported public tasks 上完成 120 个运行的可审计描述性比较。现有材料不足以支撑“真实生态普遍有效”“显著优于 Original”或“普遍优于现有模糊器”等宽主张。

## 当前不建议再做什么

- 不建议现在直接补 30 seed。当前主要风险是 public benchmark 数量、执行语义和外部基线广度，而不是同一任务的 seed 数量。
- 不建议现在硬做 SMARTIAN、MuFuzz、IR-Fuzz 工具级对比。若执行模型、任务、预算和 oracle 不可比，新增数字会扩大而不是消除解释风险。
- 不建议恢复或使用 matched-random-v1 作为新控制证据；其 provenance unresolved，必须保持 quarantine。
- 不建议把 exercise2-access-control、PUB06–PUB08 或任何 V2 材料并入当前 supported pooled 表。
- 不建议把 budget_exhausted 改写为 property passed、contract safe 或漏洞不存在。
- 不建议用 Total calls 声称 speedup，也不建议把 Harness 与 Original 写成完全等价。

## 如果补强，最小补强是什么

优先补 2–4 个 public benchmark，覆盖不同的调用者、状态映射、资金/时间依赖和合约规模，并沿用独立 provenance、预登记和语义筛查流程。相比盲目扩展同一批任务的 seed，这能直接改善外部效度。

第二优先级是补 exercise2-access-control 的 caller-controlled appendix：至少比较 same-caller 与 alternating-caller，记录每步交易边界、失败和回滚范围、属性相关最终状态及 trace。即使完成，也应作为 conditional 案例报告，不能自动进入 supported pooled 主表。

只有在上述语义和任务覆盖风险得到缓解后，才考虑增加 seed 或建立可比的外部基线。任何补强都应作为独立预登记实验，不覆盖当前 V1 结果。

## 当前投稿定位

建议定位为：面向既有属性模糊器的属性定向交易序列 Harness 合成方法及其受控、有限公开基准评价。更适合机制聚焦的工具型短文、学位论文实验章节或窄定位投稿尝试；不应包装成新的通用智能合约模糊器或完整的竞品排名研究。

## 推荐标题

Property-Directed Harness Synthesis for Stateful Smart-Contract Fuzzing: Controlled Mechanism Evidence and a Bounded Public-Benchmark Study

中文工作标题：

面向有状态智能合约模糊测试的属性定向 Harness 合成：受控机制证据与有限公开基准研究

## 推荐贡献点

1. 提出一个位于 Echidna 之前的外部 Harness synthesis preprocessing 流程，将属性相关过滤、有界重复和值约束组合为可审计的候选路径生成过程。
2. 在专门设计的受控 Formal benchmarks 上分别展示 Property、Value、Repeat 和 Top-K 对相应障碍的作用，明确每项机制的适用范围。
3. 建立从预登记、生成 Harness、运行、解析、状态分类到 checksum 的可追溯评估链，并把 wrapper 与 Original 的语义边界作为评价对象显式审计。
4. 在四个 supported public tasks 上给出 120-run、三方法、seed 1–10 的描述性结果，并保留 conditional、excluded 和 quarantine 项，不用不可比材料填充分母。

## 推荐摘要主张

可以主张：该方法将属性读取的状态依赖用于候选交易序列规划，并以外部 Solidity Harness 的形式交给既有属性模糊器继续探索。在受控 Formal benchmarks 上，属性过滤、值匹配和有界重复分别解决了预先声明的路径干扰、值方向和重复访问障碍。在四个预登记 supported public tasks、三种方法和 seed 1–10 的 120 个运行中，运行产物和状态 provenance 全部完整，观察到 118 个 falsified 和 2 个 budget_exhausted。结果是范围内描述性证据；Harness 采用 wrapper 执行模型，不等价于 Original 的多交易语义。

摘要中不应把 118/120 写成安全检测率、属性通过率、显著优势或真实生态泛化率，也不应暗示四个任务足以代表公开基准总体。

## 推荐实验主张

正文可以围绕以下句式展开：

- 在受控 Formal benchmarks 上，V1 能生成与显式安全属性相关、可检查的候选路径，并观察到各组件对其目标障碍的方向性作用。
- 在四个预登记 supported public tasks 上，Original、Full-K1 和 Full-K5 都能在当前实验范围内产生可分类的结果；主运行的 provenance 完整性为 120/120，checksum 通过为 120/120。
- Full-K1 和 Full-K5 在多数任务组中观察到 falsified，但这只是描述性比较，不能解释为显著优于 Original。
- 公开结果必须结合 wrapper caller、transaction atomicity、rollback scope 和其他环境差异解释；exercise2-access-control 继续保持 conditional。

## 不推荐主张

不推荐写入论文或摘要：

- Full-K1/Full-K5 显著优于 Original；
- Total calls 证明 speedup；
- Harness 与 Original 完全等价；
- budget_exhausted 代表 property passed、contract safe 或没有漏洞；
- 四个 supported public tasks 代表真实合约生态；
- V1 普遍优于 Echidna、SMARTIAN、MuFuzz 或 IR-Fuzz；
- matched-random-v1 可作为新的控制主张；
- exercise2-access-control 可以进入 supported pooled；
- 当前证据已经证明大型真实合约上的通用可扩展性。

## 进入下一阶段的条件

允许进入 C2 论文初稿准备，条件是正文、图表和摘要都遵守上述窄定位，保留主表 conditional 标记，并在 Threats to Validity 中明确四个 supported public tasks、B2 static gate、wrapper 语义差异、matched-random quarantine 和外部基线限制。若要扩大主张，应先完成更多 public benchmark 或 caller-controlled conditional appendix，而不是直接扩展到 30 seed。
