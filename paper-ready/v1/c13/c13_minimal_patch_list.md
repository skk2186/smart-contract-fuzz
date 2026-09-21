# C13 Minimal Patch List

以下修改不超过交导师前的最小收尾范围，不涉及新实验或结果重算。

| 优先级 | 最小修改 | 具体操作 | 完成条件 |
|---|---|---|---|
| P0 | 移除正文内部阶段引用 | 将 C12 正文第 97、161、203 行的“C10 以前”“C10 已审计”改为“legacy runner”“既有冻结记录”“已有 adapted real-source records”。C10 只留在 C13/C12 notes 等内部审计材料中。 | 投稿正文不依赖阶段编号才能理解。 |
| P0 | 完成引用和 cite key 核验 | 逐项核验 Harvey、ConFuzzius、SMARTIAN、MuFuzz、IR-Fuzz、SmarTest 的原始来源、正式 cite key 和可支持表述。MuFuzz 属于 high-confidence 复核项；IR-Fuzz、SmarTest 目前仍有待核验项。 | 未核验项不写作者、年份、venue、实验数字或超出 C12 的技术细节。 |
| P0 | 固定最终标题 | 采用《面向显式安全属性的智能合约多交易序列规划》，删除草稿中未选的标题候选和任何暗示通用性、效率或工具排名的标题。 | 标题、摘要、贡献和结论使用同一研究定位。 |
| P1 | 落实表格和图表安排 | 将 per-property isolation 表固定为正文核心表；为 controlled package 和 adapted status 分别指定正文表或附录表。若不生成 pipeline/rank 图，则删除图表承诺；若保留，则补齐 caption、编号和数据来源。 | 表号、图号、正文交叉引用和附录位置一致。 |
| P1 | 核验六项 related work 表述 | SMARTIAN、ConFuzzius、Harvey、MuFuzz、IR-Fuzz、SmarTest 只能保留 conceptual positioning；逐句检查是否超出已核验文献和 C11 的边界。 | 不出现未执行的公平比较、替代关系或工具排名。 |
| P1 | 统一中文术语 | 固定“属性定向交易序列规划”“property-specific/per-property”“原生多交易/Original”“Harness 执行模型”“适配真实来源”“预算内未观察到反例”等术语，避免同一概念多种译法。 | 摘要、方法、实验、threats、结论术语一致。 |
| P1 | 处理“禁止扩大解释清单” | 导师确认投稿正文是否保留第 9 节。建议将必要边界合并进结果口径和 threats，完整清单保留在 C11/C13 审计材料或附录，避免正文重复。 | 最终正文保留边界事实，但不出现审计工作流口吻。 |
| P2 | 降低英文词法噪声 | 可将两处 `speedup` 改成“不直接推出加速结论”；对 `candidate count`、`target rank`、`right-censored` 等必要术语只保留一次中英定义。 | 危险词扫描仍为空或只剩明确的术语定义。 |
| P2 | 补正文证据交叉引用 | 在 RQ1 表、controlled 结果和 adapted status 表旁补具体结果文件或附录入口；不新增数字。 | 每个正文结果可回到 C11 matrix 和既有结果文件。 |

## 修改边界

以上 9 条足以处理 C12 的投稿前文字、引用和版式问题。它们不要求新增 benchmark、seed、baseline、Echidna run，也不允许修改 `results/` 下已有结果。
