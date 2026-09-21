# C13 Submission Readiness Audit

## 总体判断

C12 的核心 claim 已有 C11 evidence matrix 对应证据，未发现需要新增实验才能成立的核心缺口。当前阻碍是投稿文本收尾问题：删除正文中的内部阶段名、完成引用核验、落实表格/图表安排，并统一术语。因此本审计的 next decision 为 `NEEDS_MINOR_TEXT_PATCH`。

| 检查项 | 状态 | 审计判断 | 最小修改建议 | 依据 |
|---|---|---|---|---|
| Title 是否过强 | PASS | 当前标题《面向显式安全属性的智能合约多交易序列规划》没有使用通用性、效率或工具排名措辞，与 C11 推荐标题一致。 | 导师确认后固定该标题，删除其他候选标题，不再在正文中使用旧标题。 | `paper-ready/v1/c12/c12_rewritten_paper_draft.md`；`paper-ready/v1/c11/research_contract.md` |
| Abstract 是否过强 | PASS | 摘要把 union-property 干扰、方法链、per-property isolation 数字和 controlled mechanism boundary 放在一起，并明确 Harness 执行模型差异。 | 保留当前范围限定；定稿时只压缩英文术语，不增加整体性能或生态外推句。 | `paper-ready/v1/c12/c12_rewritten_paper_draft.md`；`paper-ready/v1/c11/claim_evidence_matrix.md` |
| Contributions 是否都有证据 | PASS | 三项贡献分别对应属性级候选隔离、可追溯的组合规划、证据与执行边界；C11 accepted contribution claims 均有 code audit、controlled 或 provenance 支撑。 | 不再恢复 C10 的四条贡献；可在贡献后加对应证据位置，但不增加新 claim。 | `paper-ready/v1/c11/research_contract.md`；`paper-ready/v1/c11/claim_evidence_matrix.md`；`paper-ready/v1/c12/c12_rewritten_paper_draft.md` |
| Method 是否清楚 | PASS | C12 已依次说明 resolver、selected read-set、target functions、backward paths、bounded repetition、value evidence、Top-K、property-specific proxy 和 execution-model boundary。 | 将正文中的少量英文模块名统一为一套中英术语；不需要方法重写。 | `paper-ready/v1/c12/c12_rewritten_paper_draft.md`；`paper-ready/v1/c11/paper_patch_plan.md` |
| Evaluation RQ 是否可回答 | PASS | C12 已收敛为三个 RQ：候选隔离、组件行为、adapted real-source 边界；每个 RQ 都有既有 evidence layer。 | 保留三个 RQ，删除任何恢复“整体检测效率”的旧问题；把 seed-level 细节放附录。 | `paper-ready/v1/c12/c12_rewritten_paper_draft.md`；`paper-ready/v1/c11/experiment_freeze_decision.md` |
| Results 是否越界 | NEEDS_MINOR_FIX | 核心结果口径已正确区分 controlled、adapted、`compile_error` 和 `budget_exhausted`，但正文仍有“C10 已审计”或“C10 以前”的内部阶段引用，不适合直接进入投稿正文。 | 将正文中的 C10 改为“既有冻结记录”“已有 adapted real-source records”或具体证据路径；保留 C10 只在审计说明中。 | `paper-ready/v1/c12/c12_rewritten_paper_draft.md`；`paper-ready/v1/c11/experiment_freeze_decision.md` |
| Threats 是否充分 | PASS | 已覆盖 controlled benchmark 外部有效性、Harness/Original 语义差异、right-censored budget、compile 工程状态、跨工具公平性和小规模 adapted pool。 | 只需在最终版将 threat 条目与实际表格/附录位置交叉引用。 | `paper-ready/v1/c12/c12_rewritten_paper_draft.md`；`paper-ready/v1/c11/research_contract.md` |
| Related work 是否存在过度比较 | PASS | C12 将 SMARTIAN、ConFuzzius、Harvey、MuFuzz、IR-Fuzz、SmarTest 放在 conceptual positioning，明确没有公平 executable comparison。 | 保持当前定位，不添加“领先”“替代”或工具排名句。 | `paper-ready/v1/c12/c12_rewritten_paper_draft.md`；`paper-ready/v1/c11/paper_patch_plan.md` |
| Citation 是否存在待核验项 | NEEDS_MINOR_FIX | Harvey、ConFuzzius、SMARTIAN 等已有 cite key；MuFuzz 仍需 high-confidence 复核，IR-Fuzz 和 SmarTest 的正式 key/方法描述在仓库材料中仍标为待核验。 | 定稿前逐项核验六个指定工作的原始来源和 cite key；未核验前不增加作者、年份、venue、实验数字或精确技术细节。 | `paper-ready/v1/c12/c12_rewritten_paper_draft.md`；`paper-ready/v1/c12/c12_rewrite_notes.md`；`paper-ready/v1/c11/claim_evidence_matrix.md` |
| 是否还需要新增实验 | PASS | 当前核心 claim 已有受控 isolation 数字和 C10/C11 已审计的组件、adapted 状态证据。剩余问题是外部有效性和公平 baseline，不是本阶段可通过无目标运行解决的问题。 | 不新增 benchmark、seed、baseline 或 Echidna 运行；遵循 C11 的冻结决定。 | `paper-ready/v1/c11/experiment_freeze_decision.md`；`paper-ready/v1/c11/research_contract.md`；`paper-ready/v1/c12/c12_rewrite_notes.md` |

## 审计结论

C12 可以作为导师审阅底稿，但在提交为正式投稿版本前需要完成少量文本和引用收尾。没有 major rewrite，也没有新增实验的必要。
