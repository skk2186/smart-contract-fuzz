# 初稿审计报告

## 审计对象

- 初稿：paper-ready/v1/draft/c7_full_draft.md
- 写入范围：仅 docs/v1-restart 与 paper-ready/v1/draft
- 审计性质：论文整合与边界审计，不是新实验。

## 结果

| 检查项 | 结果 | 说明 |
|---|---|---|
| 必要章节是否齐全 | PASS | 含标题、摘要、关键词、引言、相关工作、背景与动机、方法、实验设计、实验结果、讨论、有效性威胁、结论和参考文献占位。 |
| 是否出现 forbidden claims | PASS | 未出现 large-scale real-world evaluation、ecosystem-wide superiority，也未声称所有真实合约全面优于 baseline。 |
| 是否出现内部阶段编号 | PASS | 初稿正文未出现 B5、B5-7、C7、V1、V2。 |
| 是否错误声称大规模真实合约实验 | PASS | 明确限定为四个 adapted real-source candidates、120 条预注册运行，未包装为大规模实验。 |
| 是否混淆 controlled evidence 与 adapted real-source evidence | PASS | 单独定义二者研究目的、分母和解释边界。 |
| 是否把 compile_error 当作性能结果 | PASS | 40 条 SmartBugs Harness compile_error 作为 engineering limitation/exclusion，未进入比较结论。 |
| 是否把 budget_exhausted 当作安全 | PASS | 明确写为 right-censored，不表示属性通过、合约安全或没有漏洞。 |
| 是否声称 Original/Harness 语义等价 | PASS | 明确写出“Original and Harness are distinct execution models”，并保留 caller、回滚和交易边界差异。 |
| 是否把 Total calls 当作 speedup | PASS | 明确禁止直接换算 speedup，仅允许同边界下的描述性轨迹指标。 |
| 是否需要补参考文献 | YES | [R1]–[R4] 均为待核验占位。 |
| 是否需要补图表 | YES | 需将正式 CSV/TSV 排版为主表、补充表和必要图示。 |
| 是否包含 exercise2 | PASS | 初稿不纳入 exercise2；当前真实来源叙事只包含四个支持的 adapted candidates。 |
| 是否保持证据边界 | PASS | 受控证据作为主机制证据，真实来源作为补充适用性证据。 |

## 数据口径复核

- B5-5R result records：120/120。
- usable/descriptive records：80。
- excluded engineering rows：40。
- comparable Echidna-origin rows：60。
- SmartBugs Original-only falsified rows：20。
- budget_exhausted：1，right-censored。
- real-source adapted candidates：4。
- exercise2：未执行。

## 审计结论

初稿结构完整，实验叙事与既有证据一致，可以进入参考文献与表格补全；当前不足属于投稿材料完善，不构成证据审计阻塞。
