# PHS 修订稿风格与主张审计

审计对象：paper-ready/v1/c3/revised_full_draft_zh.md

| issue_id | severity | location | problem | recommended_fix |
|---|---|---|---|---|
| C3-A01 | PASS | 全文 | 未将 V1 作为论文正文的方法名称；方法首次出现已写为“属性定向 Harness 合成方法（Property-directed Harness Synthesis，PHS）”，后续使用 PHS。 | 无。 |
| C3-A02 | PASS | 全文 | 未出现 B1、B2、B3、B4、C1、C2、C3 等流程编号。公开任务和受控实验使用论文语境下的自然描述。 | 无。 |
| C3-A03 | PASS | 全文 | 未出现 Codex、ChatGPT、提示词等过程词。 | 无。 |
| C3-A04 | PASS | 摘要、引言、实验评估、结论 | 未把观察结果写成显著优于或普遍优于其他方法；比较被表述为范围内 descriptive comparison。 | 无。 |
| C3-A05 | PASS | 动机、方法、实验评估、有效性威胁 | 未把候选数量变化或调用计数写成 speedup/加速结果主张；明确不使用 Total calls 作为跨模型工作量指标。 | 无。 |
| C3-A06 | PASS | 背景、方法、实验评估、有效性威胁 | 未把 Harness wrapper 与 Original multi-transaction model 写成完全等价；保留 caller、transaction atomicity 和 rollback scope 差异。 | 无。 |
| C3-A07 | PASS | 摘要、背景、实现、实验评估、结论 | budget_exhausted 被定义为预算内未观察到反例，没有被写成 property passed、contract safe 或漏洞不存在。 | 无。 |
| C3-A08 | PASS | 摘要、实验评估、有效性威胁 | 四个 supported public tasks 被明确限定为任务级样本，没有被描述为真实生态代表。 | 无。 |
| C3-A09 | PASS | 引言、实验评估、有效性威胁 | exercise2-access-control 被保持为 conditional，未并入 supported pooled 结果。 | 无。 |
| C3-A10 | PASS | 实现、实验评估、有效性威胁、结论 | 历史控制实验因 provenance 不完整保持 quarantine，没有被用作新的论文主张。 | 无。 |
| C3-A11 | PASS | 实验评估与结果表 | 120 runs、118 falsified、2 budget_exhausted、120/120 artifact、120/120 checksum、0 parser/status mismatch 及其他零错误计数与冻结摘要一致。 | 无。 |
| C3-A12 | INFO | 背景、方法、相关工作 | PHS、property-directed、Harness、Top-K、Original 等中英术语按研究语境保留，未将同义词随意混用；仍需在终稿建立正式术语表。 | C4 补充术语表，并统一图表和引用中的大小写与连字符。 |
| C3-A13 | INFO | 实现、实验评估 | manifest、command、environment、raw、parsed、summary、status、checksum 等产物名被保留，因为它们解释 provenance；这些是复现设计而非阶段流程叙述。 | C4 视版面需要将目录产物细节移至复现小节或附录。 |
| C3-A14 | PASS | 章节结构 | 正文按问题、方法、实验和局限组织，没有使用阶段 closeout 作为章节叙事。 | 无。 |

## 审计结论

修订后的完整初稿通过本轮去内部化和主张边界检查。保留的英文术语、状态名、方法名和产物名属于论文技术内容；尚未补入任何未经核验的文献事实。C4 仍需完成引用、术语表、图表和逐条证据交叉检查。
