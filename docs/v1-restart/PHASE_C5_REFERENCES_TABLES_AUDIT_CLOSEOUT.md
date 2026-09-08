# PHASE C5 References, Tables and Evidence Audit Closeout

## 基线

- 当前分支：`develop`
- 当前 HEAD：`4a09224327f19b20f742fb9b6f7e144d426f5639`
- 最新提交：`4a09224 docs: repair V1 paper evidence crosswalk ids`
- 初始 WSL `git status --short`：为空，工作区干净。
- 初始状态核验在 Ubuntu-20.04 WSL 仓库 `/home/skk/research/smart-contract-fuzz` 中完成；未采用 Windows 挂载视角的冲突状态。

## 本阶段执行边界

- 是否运行实验：否。
- 是否运行 Echidna：否。
- 是否运行 10 seed：否。
- 是否运行 30 seed：否。
- 是否修改 `results/` 或 `results/frozen/`：否。
- 是否修改 `results/frozen/matched-random-v1`：否。
- 是否新增 benchmark：否。
- 是否修改 benchmark source：否。
- 是否修改 analyzer 方法逻辑：否。
- 是否修改 B4 结果或数字：否。
- 是否创建新分支：否。
- 是否自动 commit：否。
- 是否自动 push：否。
- 是否新增辅助脚本：否；本阶段直接生成 C5 审计和排版输入文件，没有新增 `analyzer/build_c5_audit_pack.py`。

## 引用与图表结果

- 是否发现 verified references：否。
- 仓库中发现的引用文件：仅 `paper-ready/v1/c4/references_todo.bib`；它仍是 `TODO_VERIFY` 占位，未被认定为正式 references。
- 是否生成 reference checklist：是，`paper-ready/v1/c5/verified_reference_checklist.tsv`。
- 是否生成 citation gap report：是，`paper-ready/v1/c5/citation_gap_report.md`。
- 是否生成 final table drafts：是，`paper-ready/v1/c5/final_table_drafts.md`，包含 Table 1--6。
- 是否生成 figure input specs：是，`paper-ready/v1/c5/figure_input_specs.md`，包含 Figure 1--4 及可选 Figure 5 说明；未生成图片或 PPT。
- 是否生成 draft evidence audit：是，`paper-ready/v1/c5/draft_evidence_audit.md`。
- 是否生成 forbidden claim scan：是，`paper-ready/v1/c5/forbidden_claim_scan.md`；结论为 `PASS`，未发现禁用内容作为 C3/C4 正文正向主张。
- 是否生成 C5 decision：是，`paper-ready/v1/c5/c5_decision.md`。

## 结果边界复核

- B4 仍按已有证据解释：120 runs、118 falsified、2 budget_exhausted、120/120 artifact complete、120/120 checksum pass、0 parser/status mismatch、0 startup_error、0 unknown_error、0 incomplete。
- Table 3 保留 `main_table_usable=conditional`。
- `budget_exhausted` 保留“在预算内未观察到反例”的注释，不写成通过、安全或无漏洞。
- Original multi-transaction model 与 wrapper execution model 的 caller、atomicity、rollback、value/context 和 external-call 边界在 Figure 3、Table 6 和 evidence audit 中保留。
- exercise2-access-control 继续是 conditional；matched-random-v1 继续 quarantine；V2 和 excluded internal candidates 未进入 C5 表格。

## 阶段决策

- 是否允许进入 C6：**是**。
- 是否允许最终投稿：**否**。
- 主要阻塞项：
  1. 28 个 citation slots 尚无 verified BibTeX；必须人工核验原始来源、官方文档、benchmark repository 或 artifact guidance。
  2. Figure 1--4 尚需正式制作和人工审图。
  3. Table 1--6 尚需按目标 venue 排版，并完成正文、图表、citation marker 和 evidence id 的最终交叉引用。
  4. Related Work 中 SMARTIAN、MuFuzz、IR-Fuzz 等只能保持相关方向定位，不能变成未执行的工具级排名。

## 下一步

进入 C6 时优先处理正式引用、图表制作和逐节文字精修。是否补 B5 benchmark 由目标会议和时间决定，但不属于 C5 前置条件；当前不建议直接做 30 seed。完成人工检查后，由用户自行执行精确路径的 `git add`、`git commit` 和 `git push` 到 `develop`。
