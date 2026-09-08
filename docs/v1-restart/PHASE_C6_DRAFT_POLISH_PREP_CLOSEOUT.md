# PHASE C6 Draft Polish Preparation Closeout

## 基线

- 当前分支：`develop`
- 当前 HEAD：`cbaabc5e83e4dce603f4951f452c82ac3667786d`
- 最新提交：`cbaabc5 docs: audit V1 paper references tables and claims`
- 初始 WSL `git status --short`：为空，工作区干净。
- 基线在 Ubuntu-20.04 WSL 仓库 `/home/skk/research/smart-contract-fuzz` 中核验。

## 执行边界

- 是否运行实验：否。
- 是否运行 Echidna：否。
- 是否运行 10 seed：否。
- 是否运行 30 seed：否。
- 是否修改 `results/` 或 `results/frozen/`：否。
- 是否修改 `matched-random-v1`：否。
- 是否新增 benchmark：否。
- 是否修改 benchmark source：否。
- 是否修改 analyzer 方法逻辑：否。
- 是否改变 B4 结果或数字：否。
- 是否创建新分支：否。
- 是否自动 commit：否。
- 是否自动 push：否。

## C6 产物

- 是否生成 cleaned draft：是，`paper-ready/v1/c6/cleaned_draft_with_markers.md`。
- 是否生成 citation mapping template：是，`paper-ready/v1/c6/citation_bibtex_mapping_template.tsv`；verified 字段全部留空，状态保持 `TODO_VERIFY`。
- 是否生成 figure/table checklist：是，`paper-ready/v1/c6/figure_table_production_checklist.md`。
- 是否生成 polish issue list：是，`paper-ready/v1/c6/polish_issue_list.tsv`。
- 是否生成 target venue checklist：是，`paper-ready/v1/c6/target_venue_readiness_checklist.md`。
- 是否生成 C6 decision：是，`paper-ready/v1/c6/c6_decision.md`。
- 是否生成 C6 closeout：是，本文件。
- 是否生成正式 `references.bib`：否；仓库没有 verified references，未伪造或改名 `references_todo.bib`。
- 是否生成图片或 PPT：否。

## 结果和主张边界

- B4 数字保持：120 runs、118 falsified、2 budget_exhausted、120/120 artifact complete、120/120 checksum pass、0 parser/status mismatch、0 startup_error、0 unknown_error、0 incomplete。
- `main_table_usable=conditional` 保持不变。
- cleaned draft 保留 citation markers、figure/table markers、`budget_exhausted` 的正确含义、Original/Harness 语义边界、四个 supported public tasks、exercise2 conditional 和历史 provenance quarantine。
- 未把 citation marker 或 TODO BibTeX 当正式引用。

## 阶段决策

- 是否可以进入 C7：**是**，C7 做正文精修、人工引用替换、图表制作和 venue 格式化。
- 是否可以最终投稿：**否**。
- 主要阻塞项：
  1. 28 个 citation slots 尚无 verified references；
  2. Figure 1--4 尚未生成并人工审图；
  3. Table 1--6 尚未按目标 venue 定稿；
  4. 目标 venue、英文版、匿名化和最终格式尚未确定；
  5. 四个 supported tasks 和 wrapper 语义仍限制外部效度与跨模型解释。

## 下一步建议

当前最短路径是先完成人工引用核验、核心图表和目标 venue 格式，再进行窄定位投稿尝试。若时间允许，B5 补 2--4 个 public benchmark 比直接扩展当前任务 seed 更有价值；不建议现在直接做 30 seed。完成检查后，由用户自行执行精确路径的 `git add`、`git commit` 和 `git push` 到 `develop`。
