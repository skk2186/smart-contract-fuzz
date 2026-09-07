# C4R Evidence Crosswalk Repair Closeout

## 基线核验

- 当前分支：develop
- 当前 HEAD：8889665597b24bc91657b386e50091d750ae1bac
- 最新提交：8889665 docs: prepare V1 paper references and figure plan
- 初始 git status --short：为空；开始 C4R 时工作区干净。

## 修复内容

- 修复文件：paper-ready/v1/c4/evidence_crosswalk.tsv
- 替换内容：将两处 E06_PHASE05_METHOD_POSITIONING 替换为 E06_PHASE04_METHOD_POSITIONING。
- 错误 ID 是否已消除：是；C4 目录中不再出现 E06_PHASE05_METHOD_POSITIONING。
- 正确 ID 是否存在：是；E06_PHASE04_METHOD_POSITIONING 在 evidence_index.tsv 中真实存在，并在 evidence_crosswalk.tsv 中用于 Introduction method positioning 和 Method PHS workflow 两条记录。
- 其他 C4 文件是否存在错误 ID：否。
- 是否修改 citation_slots.tsv：否；TODO_VERIFY / NOT_FOUND_LOCAL 状态保持不变。
- 是否修改 references_todo.bib：否；所有 TODO_ 占位条目及 TODO_VERIFY note 保持不变。

## 一致性检查

- evidence_crosswalk.tsv 中所有 E* evidence_id 是否存在于 evidence_index.tsv：是，C4R E-ID CHECK 通过。
- C* claim boundary 标记的处理：C01_CLAIM_BOUNDARY 与 C04_CLAIM_BOUNDARY 不作为 evidence_index.tsv 的 evidence_id；它们是 claim_evidence_matrix.tsv 的 claim-boundary 引用标记。检查时按 C01、C04 前缀映射到 claim_evidence_matrix.tsv，并保留其 claim boundary 语义。
- 结果数字是否改变：否；B4 的 120 runs、118 falsified、2 budget_exhausted 及完整性计数未修改。
- results/frozen/matched-random-v1 是否修改：否。

## 范围检查

- 是否运行实验：否。
- 是否运行 Echidna：否。
- 是否运行 10 seed 或 30 seed：否。
- 是否新增 benchmark：否。
- 是否修改 benchmark source 或 analyzer：否。
- 是否创建新分支：否。
- 是否自动 commit 或 push：否。

## 结论

C4 evidence crosswalk 的 evidence ID 拼写和跨文件引用关系已修复并通过只读一致性检查。C4R 不改变实验结果、引用占位或论文主张范围。

是否允许进入 C5：是。C5 可继续进行正式引用核验、图表制作、正文交叉引用和终稿审校。

## 阻塞项

1. references_todo.bib 仍需由研究者根据原始来源人工替换，当前不能视为最终参考文献表。
2. C4 图表计划仍需在后续阶段依据真实字段制作和人工复核。
3. Harness/Original 语义对齐、caller-controlled replay 和更广泛 baseline 仍是已有研究限制，不由本次 ID 修复解决。
