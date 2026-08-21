# 当前阶段论文总结

更新日期：2026-08-06

## 一句话结论

目前最稳妥的论文定位是：**面向既有属性模糊器的属性定向交易序列 Harness 合成方法**。V1 已经完成受控机制验证、有限公开基准验证、随机候选池控制和 Harness 语义审计，足以支撑开题、学位论文实验章节或一篇聚焦机制的工具型短文；但当前证据还不足以支持“对真实生态普遍优于现有模糊器”或“达到 CCF-C 级别通用方法”的结论。

## 当前版本和实验批次怎么区分

| 名称 | 含义 | 当前处理 |
|---|---|---|
| V1 / Full-v1.0 | Dependency、Property、Repeat、Value 和 Top-K 的冻结方法线 | 主结果 |
| B-2 | V1 的两个扩展合成案例：AlternativePath、MultiProperty | 主文可做扩展，建议放附录或单独小节 |
| C-1 | 5 个公开基准的正式批次，含适配和统计 | 主结果，但必须披露数量少、语义条件限制 |
| C-2 | 外部工具和更广公开任务的验证阶段 | 当前没有新增 C2 候选，仍是阻塞项 |
| V2 | 原生多交易 seed、violation-boundary、ranking regression 等开发线 | 与 V1 分离，不能 pooled |
| C0 | 兼容性和路径筛查 | 不进入正式分母 |
| smoke | 启动/编译/编排检查 | 不进入实验分母 |

## 论文主证据

| 证据块 | 结果 | 可以支持 | 不能支持 |
|---|---:|---|---|
| 六个合成基准 | Full-K1 180/180；Original 171/180 | 受控障碍上属性定向候选有效 | 真实合约总体泛化、外部 SOTA 胜出 |
| 四个 Formal 候选空间 | Dependency 92 条降至 Property 31 条，减少 66.30% | 候选空间压缩和排序机制 | 路径减少必然带来 fuzzing 加速 |
| B-2 扩展 | AlternativePath、MultiProperty 各 30 次 Full-K1 均成功 | 多路径和多属性扩展可工作 | 与六个主案例完全同质、可直接 pooled 的统计结论 |
| 五个公开 C-1 | Full-K5 149/150；Original 144/150；Full-K1 120/150 | 在已筛查任务上的分层结果 | 五个任务代表真实生态、K1 普遍稳定 |
| matched-random | 随机候选 87/270；Full-K1 240/270；同 seed 配对 | 收益来自候选池内排序选择，而不只是随机抽取 | 替代 SMARTIAN、IR-Fuzz、MuFuzz 等外部基线 |
| 语义适用性 | 11 个目标中 10 supported、1 conditional；固定路径差分重放 11/11 一致 | 在调用者对齐、每步成功等窄范围内的可重放性 | Original 多交易和 wrapper 单交易完全等价 |
| SMARTIAN 外部批次 | 2 个简单整数目标，各 30 次，共 60/60 完成并发现 IntegerBug | 部署链路、日志解析和共同 oracle 的可执行性 | 广泛外部竞品排名或 C-2 泛化 |

## 方法的真实创新点

当前最值得保留的创新组合，不是“状态依赖”“重复调用”或“交易排序”本身，而是以下组合：

1. **属性定向**：从安全属性所读取的状态反向筛选候选路径，而不是只按一般读写依赖生成路径。
2. **外置、可审计的 Harness**：把候选调用序列显式生成到 Solidity Harness 中，便于检查候选内容、Top-K 和失败原因。
3. **可解释的组合排序**：Property、Repeat、Value 三类证据逐层组合，能解释为何某条路径进入 K1/K5，以及为何某些公开任务需要 K5。
4. **语义边界显式化**：单独审计 wrapper 与 Original 的调用者、交易原子性和回滚差异，而不是把 Harness 当成天然等价的执行模型。

论文中应把贡献写成“面向属性的候选 Harness 合成和可审计评估框架”，并明确承认相关思想与 SMARTIAN、MuFuzz、IR-Fuzz 等已有工作存在重叠风险。真正需要用实验支持的是组合方式、可解释性和语义边界，而不是笼统地声称首次使用状态依赖或多交易排序。

## 目前实验做到哪一步

项目已经越过“能否运行”的阶段，进入“证据是否足够支撑论文主张”的阶段：

- 方法代码、Formal、B-2、C-1 和 matched-random 已有固定入口和派生表；
- SMARTIAN 已部署并完成两个外部目标的对齐批次，但覆盖面仍很窄；
- C2 候选注册表已冻结，当前新增 C2=0，不应为了填表而把不可比结果放入主表；
- 主要剩余风险是公开任务数量、外部基线广度、规模扩展和 Harness 语义差异，而不是 seed 数量不足。

## 当前最需要避免的误读

- `budget_exhausted` 只表示在预算内没有观察到反例，不能写成“属性通过”或“合约安全”。
- 1050 次运行不是 1050 个独立合约；泛化能力主要由合约和属性多样性决定。
- Original 与 Harness 的 `Total calls` 不能直接作为等量底层工作量比较。
- `exercise2-access-control` 的 Full-K1 为 0/30、Full-K5 为 30/30，说明 Top-K 选择会改变结果，也说明 K1 并不普遍可靠。
- V2 violation-boundary 的 270/270 是 oracle-assisted 敏感性结果，不能写成端到端通用提升。
- SMARTIAN 的 60/60 只说明当前两个简单整数目标可运行并对齐，不是 C2 竞品排名。

## 继续投入是否值得

值得，但应改变投入目标：**停止重复同一受控合约和同一 seed，把时间集中在少量高信息增益的外部任务、语义对齐和规模记录上。**

### 适合立即做的工作

- 把 V1 主结果、C-1、matched-random 和语义限制写成论文初稿；
- 若目标是 CCF-C，优先补充可执行的外部工具和更多公开属性任务；
- 在较大合约上记录候选数、静态分析时间、Harness 编译时间和失败率；
- 保留所有排除、编译失败、启动失败和不可比原因，形成审计表。

### 暂时不值得做的工作

- 继续为同一四个合成案例增加 seed；
- 把 V2 和 V1 混成一个“最终方法”；
- 用不可执行或语义不一致的外部工具填充比较表；
- 继续生成新的 V2/V3/V4 快照而不冻结版本和目录。

## 推荐论文结构与对应入口

1. **方法**：[`01_METHOD/README.md`](01_METHOD/README.md) 和 `analyzer/` 的 V1 入口。
2. **受控机制结果**：[`02_MAIN_RESULTS/README.md`](02_MAIN_RESULTS/README.md)，取 `results/paper-data/` 和 `results/formal/`。
3. **公开基准结果**：[`03_PUBLIC_C1/README.md`](03_PUBLIC_C1/README.md)，取 C-1 统计和适配说明。
4. **机制与随机控制附录**：[`04_CONTROLS_AND_ABLATIONS/README.md`](04_CONTROLS_AND_ABLATIONS/README.md)。
5. **语义威胁**：[`05_SEMANTIC_AND_LIMITS/README.md`](05_SEMANTIC_AND_LIMITS/README.md)。
6. **外部基线和 C2 限制**：[`06_EXTERNAL_BASELINES/README.md`](06_EXTERNAL_BASELINES/README.md)。
7. **复现**：[`07_REPRODUCIBILITY/README.md`](07_REPRODUCIBILITY/README.md)。

详细的逐项实验口径仍以 [`docs/EXPERIMENTS.md`](../docs/EXPERIMENTS.md)、[`results/paper-data/readiness-matrix.md`](../results/paper-data/readiness-matrix.md) 和 [`docs/CCF_C_GAP_ANALYSIS.md`](../docs/CCF_C_GAP_ANALYSIS.md) 为准。
