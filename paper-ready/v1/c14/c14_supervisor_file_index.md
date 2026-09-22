# C14 导师审阅文件索引

建议按以下顺序发送，先看论文主体，再看证据边界和审计依据：

1. **paper-ready/v1/c14/c14_supervisor_draft.md**
   - 本轮面向导师审阅的论文正文版本；已去除内部工作流痕迹，保留核心方法、三项 RQ、per-property isolation 结果和执行模型边界。
2. **paper-ready/v1/c13/c13_supervisor_cover_note.md**
   - 用一句话定位论文，说明停止新增实验的理由、核心创新、主要证据、边界和希望导师确认的问题。
3. **paper-ready/v1/c13/c13_next_decision.md**
   - 给出上一轮审计结论及其依据，帮助导师快速判断稿件是否进入审阅而不是继续扩展实验。
4. **paper-ready/v1/c13/c13_minimal_patch_list.md**
   - 列出交导师前的 P0/P1/P2 最小修改项，可用于逐项核对文字、引用、表格和术语。
5. **paper-ready/v1/c11/claim_evidence_matrix.md**
   - 将每个论文 claim 映射到具体证据文件、证据类型、强度和可出现位置，是审阅稿的证据边界索引。
6. **results/per-property-isolation/summary.json**
   - 提供 per-property isolation 的机器可读原始汇总，核对 property variables、target functions、candidate count、irrelevant candidates、target rank 和 Top-K 命中情况。

建议导师先确认主叙事和标题，再核对 claim-evidence 映射，最后检查 summary.json 与正文表格中的数字是否逐项一致。
