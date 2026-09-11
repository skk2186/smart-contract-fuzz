# 论文表格占位与数据来源

本文件只规划论文排版所需表格，不新增实验，也不把工程失败记录转化为比较结果。

## 表 1：受控场景任务概览

- 放置位置：实验设计或主实验设置。
- 内容：六个受控场景、目标属性、预设路径障碍、方法组件映射和运行分母。
- 数据来源：results/paper-data/synthetic-six-benchmark-summary.csv 及正式分组摘要。
- machine-readable：YES，当前存在 CSV；需在 references/tables audit 中确认最终纳入行。
- 可用行：正式 Original、Full-K1、Full-K5 及预先允许的组件配置。
- 必须排除：smoke、C0、开发材料、未完成运行和 Noisy random 混杂结果。
- 表注：该表是 controlled evidence 的机制任务概览，不代表真实生态分布。

## 表 2：主实验结果

- 放置位置：实验结果主小节。
- 内容：受控场景的属性违反计数、发现率、分母以及必要的轨迹统计。
- 数据来源：results/paper-data/synthetic-six-benchmark-summary.csv 与对应正式运行摘要。
- machine-readable：YES，当前存在 CSV。
- 可用行：按冻结白名单纳入的六个受控场景。
- 必须排除：历史 pilot、smoke、开发材料、未完成运行、matched-random quarantine。
- 表注：Full-K1 180/180 与 Original 171/180 的主结果必须标明相同受控分母和执行配置；不得将其外推为全部合约上的优越性。

## 表 3：真实来源 adapted candidates 概览

- 放置位置：实验结果中的补充实验小节或附录。
- 内容：四个 adapted real-source candidates、来源类型、方法覆盖、状态分布、usable 与 excluded 记录。
- 数据来源：paper-ready/v1/b5/b5_6_status_breakdown.tsv、paper-ready/v1/b5/b5_6_usable_subset.tsv、paper-ready/v1/b5/b5_6_excluded_engineering_rows.tsv。
- machine-readable：YES，当前存在 TSV。
- 可用行：120/120 记录的总状态审计，以及 80 条 usable/descriptive rows。
- 必须排除：40 条 SmartBugs Harness compile_error 不进入比较结果列，但应在工程限制栏完整报告。
- 表注：真实来源证据必须标记为 adapted real-source evidence；budget_exhausted 是 right-censored，不是安全或通过。

## 表 4：真实来源 candidate × method 矩阵

- 放置位置：补充实验的窄范围比较小节。
- 内容：candidate × method 的 rows、status summary、falsified、budget_exhausted、compile_error 和 falsified-only 轨迹统计。
- 数据来源：paper-ready/v1/b5/b5_6_candidate_method_matrix.tsv。
- machine-readable：YES，当前存在 TSV。
- 可用行：只比较 b5-rs-echidna-flags 和 b5-rs-echidna-multi 的 Original、Full-K1、Full-K5 六个 cells。
- 必须排除：SmartBugs Harness compile_error cells 不进入发现率、性能或方法比较。
- 表注：calls-to-failure、sequence-length、fuzz seconds 和 wall seconds 仅对 falsified rows 作描述性统计；Original 与 Harness 不视为语义等价执行模型；不能用 Total calls 直接声称 speedup。

## 表 5：威胁有效性与缓解措施

- 放置位置：Threats to Validity 小节。
- 内容：受控场景外部有效性、candidate 数量有限、源代码适配、人工属性接口、Solidity 0.4.25 import-path compile_error、right-censoring、执行模型差异、版本和复杂类型覆盖不足，以及对应缓解方式。
- 数据来源：paper-ready/v1/b5/b5_7_threats_to_validity_insert.md、b5_6_paper_claims.md、docs/v1-restart/SEMANTIC_BOUNDARY_AUDIT.md、docs/v1-restart/PAPER_EVIDENCE_LOCK.md。
- machine-readable：NO，当前为结构化 Markdown；表格可在排版阶段由条目重排。
- 可用行：所有限制和缓解措施。
- 必须排除：任何把 compile_error 解释为检测失败、把 budget_exhausted 解释为安全、或把不同 execution model 的调用数解释为 speedup 的行。
- 表注：限制表用于界定主张范围，不是新的性能排名。

## 排版原则

主文优先放表 1 和表 2；真实来源补充实验放表 3 和表 4；表 5 放在有效性威胁章节。所有记录级明细可以放在附录或数据仓库入口，不能把 120 条运行排版成大规模真实合约评估。
