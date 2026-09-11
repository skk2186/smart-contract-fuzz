# PHASE_C7_DRAFT_INTEGRATION

## 阶段状态

PASS（论文初稿整合材料已生成，待进入参考文献与表格补全）。

## 起始审计

- 起始分支：develop
- 起始 HEAD：c506cb32cebfe0d9334a298a5c2b0f89e8b84bd0
- 起始工作区：clean
- 上一提交：exp: B5-7 paper integration
- 本阶段未创建分支、未创建 PR。

## 输入文件

1. paper-ready/v1/b5/b5_7_experiment_section_insert.md
2. paper-ready/v1/b5/b5_7_experiment_tables_plan.md
3. paper-ready/v1/b5/b5_7_claim_boundary.md
4. paper-ready/v1/b5/b5_7_abstract_results_paragraph.md
5. paper-ready/v1/b5/b5_7_threats_to_validity_insert.md
6. paper-ready/v1/b5/b5_7_decision.md
7. paper-ready/v1/b5/b5_6_real_source_analysis_summary.md
8. paper-ready/v1/b5/b5_6_paper_claims.md
9. docs/v1-restart/SEMANTIC_BOUNDARY_AUDIT.md
10. docs/v1-restart/PAPER_EVIDENCE_LOCK.md

上述材料均在开始审计时确认存在且可读。B5-5R 原始结果和 B5-6 派生分析仅作读取来源，未被修改。

## 证据摘要

本次整合保留以下已核验口径：

- adapted real-source evidence：120/120 result records；
- 四个真实来源 adapted candidates；
- 80 条 usable 或 descriptive records；
- 40 条 SmartBugs Harness compile_error engineering rows，排除出 comparative outcomes；
- 两个 Echidna-origin candidates、60 条 comparable rows；
- SmartBugs Original-only 20 条 falsified rows；
- 1 条 budget_exhausted，解释为 right-censored；
- controlled evidence 是主机制证据，真实来源材料是补充适用性证据；
- Original 与 Harness 的执行模型及语义边界被保留，未声称语义等价；
- exercise2 未执行且未纳入 supported pool。

## 生成文件

- paper-ready/v1/draft/c7_full_draft.md
- paper-ready/v1/draft/c7_draft_audit.md
- paper-ready/v1/draft/c7_table_placeholders.md
- paper-ready/v1/draft/c7_next_decision.md
- docs/v1-restart/PHASE_C7_DRAFT_INTEGRATION.md

## 边界执行情况

- 是否新增实验：NO。
- 是否运行 Echidna formal fuzzing：NO。
- 是否重跑 B5-5R：NO。
- 是否修改旧证据：NO。
- 是否修改 B5-4 frozen preregistration：NO。
- 是否修改 B5-5 blocked artifact：NO。
- 是否修改 B5-5R raw result TSV：NO。
- 是否修改 B5-6 分析输入：NO。
- 是否修改 B4、B5-2、B5-Min、frozen evidence、matched-random evidence 或 legacy evidence：NO。
- 是否纳入 exercise2：NO。
- 是否保留 B5-7 结论边界：YES。
- 真实来源正文是否标记为 adapted real-source evidence：YES。
- 是否声称大规模真实合约评估或生态级优越性：NO。

## 初稿最薄弱之处

1. 相关工作仍使用 [R1]–[R4] 占位，尚未完成真实文献核验。
2. 表格内容已经给出来源和纳入/排除规则，但主文排版所需的最终 LaTeX/投稿模板表格尚未生成。
3. 受控场景的逐任务数值和图形化展示仍需从正式 machine-readable 结果表重排，并由研究者确认分母和统计检验口径。
4. 真实来源 adapted source 的逐任务适配差异需要在附录中补充源文件、属性接口和编译器说明。
5. 当前初稿是论文叙事底稿，尚未完成术语统一、英文摘要和引用格式审校。

## 下一步建议

进入参考文献与表格补全工作：先核验 [R1]–[R4]，再从正式 CSV/TSV 生成论文表格和必要图示；同时由研究者复核真实来源适配说明和表注，保持受控证据与 adapted real-source evidence 的分层。
