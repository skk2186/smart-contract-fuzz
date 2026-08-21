# 论文证据冻结矩阵

更新日期：2026-08-06

这份矩阵是当前阶段的出口记录。它把已完成证据、允许的论文主张和仍然阻塞 CCF-C 类完整论文的事项分开；不新增实验分母，也不把 V1、matched-random 和 V2 混成一个方法版本。

## 证据状态

| 证据块 | 当前结果 | 状态 | 可以支持的主张 | 仍然不能支持 |
|---|---:|---|---|---|
| V1 Formal + B-2 | Formal Full-K1 180/180；Original 171/180 | ready | 受控多步机制中，属性定向候选能提高运行级反例发现率 | 普遍优于现有模糊器、等价交易语义 |
| V1 C-1 | Full-K5 149/150；Original 144/150；exercise2 的 Full-K1 为 0/30 | conditional | 在 5 个已筛查公开任务上报告分层结果 | 5 个任务代表真实生态、K1 对所有公开任务稳定 |
| Harness 语义审计 | 11 个目标：10 supported、1 conditional；固定路径差分重放 11/11 通过 | conditional | 在固定参数、调用者关系对齐、每步成功的窄语义范围内可重放 | Original 多交易与 wrapper 单交易完全等价 |
| matched-random Top-1 | 随机 87/270；Full-K1 240/270；同 seed 配对 | ready-appendix | 收益来自候选池内的排序选择，而非仅来自随机抽取 | 替代外部 SOTA、覆盖所有候选生成机制 |
| V2 native neutral | 210/270 = 77.78% | ready-appendix | 原生多交易 seed 在不实例化已知违反值时的路径引导效果 | 与 V1 主结果直接 pooled |
| V2 violation boundary | 270/270 = 100% | sensitivity-only | 属性违反边界值实例化会显著改变发现率 | 普遍的端到端优越性；这是 oracle-assisted 条件 |
| C2 公开候选 | 5 行全部 legacy_reference，新增 C2=0 | blocked | 已冻结候选纳入/排除流程 | 外部生态泛化 |
| 外部基线 | SMARTIAN 已部署；2 个整数目标各 30 次，共 60/60 发现对齐的 IntegerBug | conditional | 外部工具部署、共同 oracle 和日志链路可执行 | 广泛外部 SOTA 排名、跨工具速度比较 |
| 可扩展性 | 4 个小型合约有完整开销测量；11 个本地目标有规模 proxy 表 | incomplete | 小型任务开销与当前数据集规模起点 | 真实大型合约可扩展性 |

## 当前论文定位

最稳妥的定位是：

> 面向既有属性模糊器的属性定向交易序列 Harness 合成方法。方法利用静态状态依赖、简单值约束和有界重复访问生成可解释的候选序列，并通过外置 Harness 缩小顺序搜索空间。

这一定义不把“状态依赖”“重复调用”或“交易排序”单独宣称为新颖点；真正需要强调的是属性定向、外置可审计 Harness，以及明确的语义适用范围。

## Go / No-Go

### 现在可以做

- 写开题报告、学位论文实验章节或工具型短文；
- 以 V1 为主表，matched-random 和 V2 为附录/消融；
- 明确报告 exercise2 的 conditional 语义和所有目标的 atomicity caveat；
- 把外部基线和 C2 扩充记录为限制，而不是伪造负结果。

### 现在不应做

- 继续重复同一合约和同一 seed；
- 把 V2 violation-boundary 270/270 写成普遍性能提升；
- 把 matched-random 当作 SMARTIAN、IR-Fuzz、MuFuzz 等外部基线；
- 把 `budget_exhausted` 写成属性通过或合约安全；
- 把 wrapper 单交易语义与 Original 多交易语义称为等价。

### CCF-C 完整论文仍需满足的三个出口条件

1. 将已可执行的 SMARTIAN 从当前 2 个简单整数目标扩展到更多共同属性预言机、调用者和交易模型可对齐的任务；
2. 新增公开属性任务按冻结规则达到可解释的规模，且保留所有排除、编译和启动失败；
3. 在更大合约上报告候选增长、分析时间、Harness 编译时间和失败率。

在这三个条件满足前，继续增加相同受控合约的运行次数不会实质降低主要审稿风险。

## 可复核入口

- V1 主数据入口：[`dataset-whitelist.csv`](dataset-whitelist.csv)
- matched-random：[`analysis.md`](../matched-random-v1/analysis.md)
- V2 消融：[`v2-native-ablation.md`](v2-native-ablation.md)
- 语义审计：[`static-audit-report.md`](../semantic-applicability/v1/static-audit-report.md)
- 外部基线审计：[`baseline-feasibility-report-v7.md`](../public-benchmarks/c2-screening/baseline-feasibility-report-v7.md)
- SMARTIAN 正式批次：[`smartian-formal-20260806/README.md`](../public-benchmarks/c2-screening/smartian-formal-20260806/README.md)
