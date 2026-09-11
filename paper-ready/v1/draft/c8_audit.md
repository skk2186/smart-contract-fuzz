# C8 论文材料审计

| 检查项 | 结果 | 说明 |
|---|---|---|
| 带引用初稿仍有 [R1]–[R4] | NO | 已替换为 cite key |
| 带表图初稿仍有 [R1]–[R4] | NO | 已替换为 cite key |
| 最终论文副本有 REF-TODO | NO | unresolved 条目放独立清单 |
| 未核验文献进入正式 BibTeX | NO | 仅 10 verified + 2 high_confidence |
| 真实来源被写成大规模实验 | NO | 明确为 4 candidates 的 adapted real-source evidence |
| controlled/adapted evidence 混淆 | NO | 正文和表格分层 |
| budget_exhausted 写成安全 | NO | 统一为 right-censored |
| Original/Harness 写成语义等价 | NO | 明确 distinct execution models |
| compile_error 纳入比较 | NO | 40 条为 excluded engineering rows |
| 主实验表分母需要人工复核 | NO（行级）；YES（最终分组） | 12 行均为 Full-v1.0、每行 30 次；B-2 排版位置仍需研究者确认 |

真实来源记录为 120 条，其中 80 条 usable/descriptive、40 条 excluded engineering；Echidna-origin comparable 为 60 条，SmartBugs Original-only 为 20 条，right-censored 为 1 条，Harness compile_error 为 40 条。exercise2 未执行且未进入 supported pool。
