# PHASE C9 Full Draft Polish

## 阶段状态

PASS。已基于 C8 带引用、表格和图表占位的论文副本完成全文学术润色，生成可供格式化和导师审阅的完整中文稿。起始工作区 clean，本阶段未运行任何实验。

## 起始状态

- 起始分支：develop
- 起始 HEAD：8c7e446bd5e7103ef396a5154ccf4c1ede38c8db
- 起始提交：exp: C8 references and tables
- 起始工作区：clean

## 输入文件

- paper-ready/v1/draft/c8_full_draft_tables_refs.md
- paper-ready/v1/draft/c8_full_draft_with_refs.md
- paper-ready/v1/draft/c8_reference_registry.tsv
- paper-ready/v1/draft/c8_references.bib
- paper-ready/v1/draft/c8_references_to_verify.md
- paper-ready/v1/draft/c8_table_1_controlled_tasks.md
- paper-ready/v1/draft/c8_table_2_main_results.md
- paper-ready/v1/draft/c8_table_3_real_source_overview.md
- paper-ready/v1/draft/c8_table_4_real_source_matrix.md
- paper-ready/v1/draft/c8_table_5_threats.md
- paper-ready/v1/draft/c8_figure_plan.md
- paper-ready/v1/draft/c8_audit.md
- paper-ready/v1/draft/c8_next_decision.md

## 输出文件

- paper-ready/v1/draft/c9_polished_full_draft.md
- paper-ready/v1/draft/c9_language_audit.md
- paper-ready/v1/draft/c9_claims_checklist.md
- paper-ready/v1/draft/c9_revision_notes.md
- paper-ready/v1/draft/c9_next_decision.md

## 边界与润色重点

- 是否新增实验：NO。
- 是否修改旧证据：NO。
- 是否纳入 exercise2：NO。
- C8 的 citation keys、verified/high_confidence/unresolved 区分和表格边界均保留。
- 保留 controlled evidence 为主机制证据、adapted real-source evidence 为补充证据的分层。
- 保留 4 candidates、120 runs、80 usable/descriptive records、40 compile_error engineering rows、right-censored 及 Original and Harness are distinct execution models。
- 统一使用显式安全属性、属性相关变量、状态读写依赖、条件约束匹配、状态值方向匹配、有界重复和 Top-K 候选序列等术语。
- 压缩工程流水线式表述，强化问题—方法—证据—边界的论证关系，并补足表图引用位置。

## 当前仍然薄弱之处

1. 正文仍依赖 Markdown 表图占位，最终投稿需要按会议模板完成双栏排版和图表重绘。
2. registry 中 2 条 high_confidence 文献仍需在定稿前用 ACM/IEEE/DBLP 正式导出复核，1 条 unresolved 文献不进入正式 BibTeX。
3. 受控摘要没有 seed-level calls-to-failure，相关表格继续保留缺失标记。
4. B-2 扩展的独立环境快照不完整，最终需要研究者确定其放置于主文还是附录。

## 下一步建议

Decision: GO_TO_C10_FORMAT_AND_SUPERVISOR_REVIEW。建议进入格式化、图表重绘、参考文献官方导出和导师审阅；当前没有证据理由要求立即增加真实来源数量。
