# PHASE C10 Format and Supervisor Review

## 阶段状态

PASS。已将润色后的完整论文稿整理为导师审阅版和投稿准备版，并生成最终表格包、图示提示词、附录规划、artifact/ethics 说明、参考文献审计和投稿前 checklist。

## 起始状态

- 起始分支：develop
- 起始 HEAD：af80362f0c428fa9f3ff16c2d1ffd77280813794
- 起始提交：exp: C9 full draft polish
- 起始工作区：clean

## 输入文件

- paper-ready/v1/draft/c9_polished_full_draft.md
- paper-ready/v1/draft/c9_language_audit.md
- paper-ready/v1/draft/c9_claims_checklist.md
- paper-ready/v1/draft/c9_revision_notes.md
- paper-ready/v1/draft/c9_next_decision.md
- paper-ready/v1/draft/c8_references.bib
- paper-ready/v1/draft/c8_reference_registry.tsv
- paper-ready/v1/draft/c8_references_to_verify.md
- paper-ready/v1/draft/c8_table_1_controlled_tasks.md
- paper-ready/v1/draft/c8_table_2_main_results.md
- paper-ready/v1/draft/c8_table_3_real_source_overview.md
- paper-ready/v1/draft/c8_table_4_real_source_matrix.md
- paper-ready/v1/draft/c8_table_5_threats.md
- paper-ready/v1/draft/c8_figure_plan.md

## 输出文件

导师审阅包：

- paper-ready/v1/review/c10_supervisor_review_draft.md
- paper-ready/v1/review/c10_supervisor_cover_note.md
- paper-ready/v1/review/c10_review_checklist.md

投稿准备包：

- paper-ready/v1/submission/c10_submission_ready_markdown.md
- paper-ready/v1/submission/c10_submission_checklist.md
- paper-ready/v1/submission/c10_artifact_availability_statement.md
- paper-ready/v1/submission/c10_ethics_and_limitations_note.md
- paper-ready/v1/submission/c10_final_tables.md
- paper-ready/v1/submission/c10_final_figure_prompts.md
- paper-ready/v1/submission/c10_appendix_plan.md
- paper-ready/v1/submission/c10_reference_final_audit.md
- paper-ready/v1/submission/c10_final_audit.md
- paper-ready/v1/submission/c10_next_decision.md

## 边界确认

- 是否新增实验：NO。
- 是否修改旧证据：NO。
- 是否纳入 exercise2：NO。
- C9 的 controlled evidence / adapted real-source evidence 分层保留。
- 4 candidates、120 runs、80 usable/descriptive records、40 compile_error engineering rows、right-censored 和 Original and Harness are distinct execution models 均保留。
- SmartBugs Harness compile_error 未进入 comparative outcomes。
- 不把不同执行模型的 Total calls 写成 speedup。
- high_confidence 文献仍标记为定稿前复核，unresolved 文献未进入正式 BibTeX。

## 当前仍然薄弱之处

1. 导师尚需确认 baseline 最终选择、B-2 主文/附录位置和真实来源补充证据的接受程度。
2. high_confidence 文献需要从 ACM/IEEE/DBLP 再导出核验。
3. 表格和图示目前是 Markdown/提示词材料，仍需按目标会议模板完成双栏排版和重绘。
4. artifact availability 与匿名审稿链接需要结合实际公开策略最终定稿。

## 下一步建议

Decision: READY_FOR_SUPERVISOR_REVIEW。建议先发送导师审阅包，收集对创新边界、baseline、B-2 排版位置和投稿模板的意见；当前没有新增实验的必要性。
