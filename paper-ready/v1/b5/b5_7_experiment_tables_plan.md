# 论文实验表格整合计划

## 表 1：受控机制场景的主实验结果

- 表名：受控机制场景上的属性违反发现结果。
- 放置位置：实验章节主结果部分。
- 来源：results/paper-data/synthetic-six-benchmark-summary.csv，以及对应的正式分组摘要。
- 可用行：六个受控场景中预注册的 Original、Full-K1 和必要的组件配置，按既有纳入规则制表。
- 必须排除：smoke、C0、V2 开发材料、未完成运行和 Noisy random 混杂结果。
- 表注建议：该表用于验证属性相关筛选、值约束匹配和有界重复等机制在受控障碍下的作用，不代表真实生态总体表现。发现率按预先声明的合约、属性和种子分母计算。

## 表 2：公开基准的分层结果

- 表名：公开基准任务上的分层属性违反结果。
- 放置位置：实验章节公开基准小节或附录。
- 来源：results/public-benchmarks/c1/public-c1-group-summary.csv、statistics 报告和 adaptations.md。
- 可用行：五个公开任务的正式 Original、Full-K1 和 Full-K5 记录。
- 必须排除：C0、smoke、启动编排记录，以及与正式纳入规则不一致的历史记录。
- 表注建议：公开任务数量有限，且包含为属性接口和编译环境进行的适配。Full-K1 在个别任务上受 Top-K 截断影响，不能据此声称 K1 普遍稳定。

## 表 3：适配真实来源补充实验总览

- 表名：适配真实来源任务的结果与排除项总览。
- 放置位置：实验章节补充实验小节。
- 来源：paper-ready/v1/b5/b5_6_status_breakdown.tsv、paper-ready/v1/b5/b5_6_usable_subset.tsv、paper-ready/v1/b5/b5_6_excluded_engineering_rows.tsv。
- 可用行：120 条预注册结果的状态汇总，以及 80 条 usable/descriptive rows。
- 必须排除：40 条 SmartBugs Full-K1/Full-K5 compile_error 不进入比较结果列，但应在单独的工程限制列或附表中报告。
- 表注建议：四个 adapted real-source candidates 共 120 条记录，其中 80 条可用于描述性分析，40 条 compile_error 作为工程限制保留。budget_exhausted 是 right-censored，不表示安全或通过。

## 表 4：可比较 candidate × method 结果矩阵

- 表名：两个 Echidna-origin adapted real-source candidates 上的 candidate × method 结果。
- 放置位置：补充实验小节的核心比较表。
- 来源：paper-ready/v1/b5/b5_6_candidate_method_matrix.tsv。
- 可用行：仅 b5-rs-echidna-flags 和 b5-rs-echidna-multi 的 Original、Full-K1、Full-K5 六个 candidate-method cells。
- 必须排除：SmartBugs Harness compile_error cells 不得进入性能、发现率或方法比较结论。
- 表注建议：calls-to-failure、sequence-length、fuzz seconds 和 wall seconds 仅在 falsified rows 上作描述性统计。Full-K5 的 right-censored row 不纳入 falsified-only 轨迹均值和中位数。Original 与 Harness 不是语义等价的执行模型。

## 表 5：usable 与 engineering exclusion 记录说明

- 表名：论文可用记录与工程排除记录的分层说明。
- 放置位置：补充材料或实验数据审计附表。
- 来源：paper-ready/v1/b5/b5_6_usable_subset.tsv 和 paper-ready/v1/b5/b5_6_excluded_engineering_rows.tsv。
- 可用行：usable 表中的 59 条 comparable_echidna_origin、20 条 smartbugs_original_only 和 1 条 right_censored。
- 必须排除：excluded engineering 表中的全部 40 条 compile_error 不参与比较性结果。
- 表注建议：记录级表格保留原始 status、candidate、method 和属性字段。排除工程行不代表方法检测失败，保留它们是为了说明跨版本 Harness 支持的边界。

## 表 6：Threats to Validity 汇总表

- 表名：实验结论的有效性边界。
- 放置位置：Threats to Validity 小节。
- 来源：b5_6_paper_claims.md、b5_6_real_source_analysis_summary.md，以及本阶段的 threats 插入稿。
- 可用行：受控场景外部有效性、真实来源数量、源代码适配、Harness 编译限制、right-censoring、执行模型差异和未来扩展。
- 必须排除：任何将 compile_error 变成比较失败率、将 budget_exhausted 变成安全标签、或将 Total calls 变成 speedup 的派生列。
- 表注建议：所有真实来源结论均限定为 adapted real-source evidence。表格是限制说明，不是新的性能排名表。

## 推荐排版顺序

主文优先放表 1 和必要的公开基准表。真实来源表放在补充实验小节或附录中，表 3 给出整体审计，表 4 给出两个 Echidna-origin candidates 的窄范围比较，表 5 和表 6 用于复现与有效性说明。不要把四个 candidate 的 120 条 seed-level rows 排版成“大规模真实合约评估”。
