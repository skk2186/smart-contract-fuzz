# Phase C2 Closeout：Paper Draft Skeleton + Core Chinese Draft

## 仓库状态

- 当前分支：develop
- 当前 HEAD：b8f24ef32e57261173874ac63ae41ab18d4b0e7f
- 最近提交：b8f24ef docs: organize V1 paper-ready evaluation evidence
- 初始 WSL Git status：clean
- 本阶段未切换分支，未 reset、checkout、clean，未自动 commit 或 push。

## 阶段边界核验

- 是否运行实验：否。
- 是否运行 Echidna：否。
- 是否运行 10 seed：否；仅读取已有 120-run 结果摘要和冻结证据。
- 是否运行 30 seed：否。
- 是否修改 results/：否。
- 是否修改 results/frozen/matched-random-v1：否。
- 是否新增 benchmark：否。
- 是否修改 benchmark source：否。
- 是否修改 analyzer 方法逻辑：否。
- 是否使用 matched-random-v1：否；其 provenance unresolved，继续保持 quarantine。
- 是否生成完整中文初稿：是，生成 full_draft_zh.md。
- 是否保留窄定位：是，正文将 V1 定位为 Echidna 之上的 property-directed Harness synthesis preprocessing。
- 是否保留 semantic caveat：是，保留 caller、transaction atomicity、rollback scope、msg.value、区块环境、external call 和 reentrancy 边界。
- 是否将 forbidden claims 作为论文主张写入：否。
- 是否保留 forbidden-claim 检查与限制说明：是；显著优越、Total calls speedup、Harness/Original 完全等价、budget_exhausted 等于通过或安全、四任务代表真实生态、普遍优于 Echidna/SMARTIAN/MuFuzz/IR-Fuzz 等边界均已保留。

## 新增文件清单

### paper-ready/v1/c2/

- title_abstract_contributions.md
- paper_outline.md
- introduction_draft.md
- background_draft.md
- motivation_draft.md
- method_draft.md
- implementation_draft.md
- evaluation_draft.md
- threats_draft.md
- related_work_positioning.md
- conclusion_draft.md
- full_draft_zh.md

### docs/v1-restart/

- PHASE_C2_DRAFT_CLOSEOUT.md

## 结果和证据口径

- 公开 supported pool 固定为 4 个任务：echidna-flags、echidna-multi、smartbugs-multifunc、smartbugs-onefunc。
- 方法固定为 Original、Full-K1、Full-K5。
- seed 范围固定为 1–10，总计 120 runs。
- 结果固定为 118 falsified、2 budget_exhausted。
- 120/120 artifact set complete，120/120 checksum pass。
- parser/status mismatch、startup_error、unknown_error、incomplete 均为 0。
- 所有公开分组行的 main_table_usable 仍为 conditional。
- exercise2-access-control 保持 conditional，不进入 supported pooled。
- B2 static gate 不被写成完整 native EVM replay。
- budget_exhausted 不被写成 property passed、contract safe 或漏洞不存在。
- Original 与 Harness 的不同执行模型和 Total calls 限制已保留。

## C3 决策

允许进入 C3，范围限于论文人工复核与修订，不等于授权新的模糊测试实验。

建议 C3 任务：

1. 研究者逐段复核 full draft 与 C1 evidence map、claim matrix、evaluation tables 和 threats 材料的对应关系；
2. 对四个 supported public tasks 的 run-level 表、原始日志、checksum 和语义审计做人工抽查；
3. 补充经过核验的 Related Work BibTeX 和精确引用，不改变当前方法与结果口径；
4. 统一术语、图表、表号和附录交叉引用，审查是否有把描述性结果写成效果主张的句子；
5. 规划后续独立实验时，优先考虑 caller-controlled conditional replay、更多 public benchmark、规模记录和可比外部 baseline。

## 阻塞项

- 更宽的真实生态泛化主张仍受 public benchmark 仅 4 个 supported 的限制；
- exercise2-access-control 仍缺 caller-controlled replay，不能进入 supported pooled；
- B2 仍是 static_gate_only，不是完整 native replay；
- 没有完整可比的 SMARTIAN/MuFuzz/IR-Fuzz 工具级对比；
- matched-random-v1 provenance unresolved，不能用于新主张；
- Harness wrapper 与 Original multi-transaction model 的语义差异仍限制等价、speedup 和跨模型解释；
- 当前证据不足以支持大型真实合约的通用可扩展性。

## 人工复核与提交

本阶段只新增论文草稿材料。请研究者先人工检查全文、表格、证据路径和语义限制，再自行选择性执行 git add、commit 和 push 到 develop；本阶段没有自动提交或推送。
