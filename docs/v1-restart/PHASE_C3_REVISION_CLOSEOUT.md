# Phase C3 Closeout：Paper Draft Revision Pass

## 仓库状态

- 当前分支：develop
- 当前 HEAD：6308c7991816ba069e88277ff569cd802d712ba8
- 最近提交：6308c79 docs: draft V1 paper core sections
- 初始 WSL Git status：clean
- 本阶段未切换分支，未 reset、checkout、clean，未自动 commit 或 push。

## 阶段边界核验

- 是否运行实验：否。
- 是否运行 Echidna：否。
- 是否运行 10 seed：否。
- 是否运行 30 seed：否。
- 是否修改 results/ 或 frozen results：否。
- 是否修改 results/frozen/matched-random-v1：否。
- 是否新增 benchmark：否。
- 是否修改 B4 实验结果：否；120 runs、118 falsified、2 budget_exhausted 等口径保持不变。
- 是否使用 matched-random-v1 作为新主张：否；历史控制材料仍按 provenance 不完整处理。
- 是否统一方法名：是；论文正文统一使用 PHS 或“属性定向 Harness 合成方法”，首次出现给出 Property-directed Harness Synthesis 全称。
- 是否去除论文正文内部阶段痕迹：是；修订后的完整正文不出现 B1/B2/B3/B4/C1/C2/C3、Codex、ChatGPT 或提示词等流程词。
- 是否修正 C2 closeout 歧义：是；已拆分为“是否将 forbidden claims 作为论文主张写入：否”和“是否保留 forbidden-claim 检查与限制说明：是”。
- 是否生成 revised full draft：是。
- 是否生成 claim/style audit：是，已生成 style_and_claim_audit.md。
- 是否保留 semantic caveat：是；保留 caller、transaction atomicity、rollback scope、msg.value、区块环境、external call、reentrancy 和 address-keyed state 边界。
- 是否保留窄定位：是；PHS 被定位为 Echidna 之前的 external Harness synthesis preprocessing。
- 是否保留 forbidden-claim 限制：是；未将显著优越、跨模型加速、完全等价、属性通过、合约安全、生态代表性或工具普遍优越写成论文主张。

## 新增文件清单

### paper-ready/v1/c3/

- revised_title_abstract_contributions.md
- revised_full_draft_zh.md
- revised_introduction.md
- revised_evaluation.md
- revised_related_work_plan.md
- style_and_claim_audit.md
- c3_revision_notes.md

### docs/v1-restart/

- PHASE_C3_REVISION_CLOSEOUT.md

## 修订结果摘要

- 论文方法名称由内部版本代号改为 PHS。
- 引言强化了研究问题、方法直觉、证据范围和贡献叙事。
- Evaluation 以 RQ1–RQ4 组织机制、运行链、描述性比较和语义解释。
- 完整中文稿按“引言—背景—动机—方法—实现—实验评估—有效性威胁—相关工作—结论”组织。
- Related Work 只加入待补引用槽位和核验计划，没有编造论文事实。
- 风格与主张审计确认关键内部阶段词已从修订完整正文移除，必要技术术语和产物名被保留为论文内容。

## C4 决策

允许进入 C4，范围限于引用、图表、术语和证据交叉引用的人工补全，不等于授权新的模糊测试实验。

建议 C4 任务：

1. 逐个核验并填充 Related Work 的 citation slots，补充准确 BibTeX；
2. 建立 PHS、property-directed、transaction sequence、Harness synthesis、wrapper execution model 和 Original multi-transaction model 的术语表；
3. 将冻结表格转为最终论文图表和附录，保持 main_table_usable=conditional；
4. 对四个 supported public tasks 的 run-level 表、原始日志、status 和 checksum 做人工抽查；
5. 对正文每个数字和主张建立 evidence map，确保引用与范围一致；
6. 继续保持新实验、benchmark 扩展和外部工具比较的独立预登记边界。

## 阻塞项

- Related Work 的精确论文引用和 BibTeX 尚未补全；
- public benchmark 只有 4 个 supported，不能支撑真实生态泛化；
- exercise2-access-control 仍需 caller-controlled replay，不能进入 supported pooled；
- 静态 gate 不是完整 native EVM replay；
- 没有完整可比的 SMARTIAN、MuFuzz、IR-Fuzz 工具级比较；
- Harness wrapper 与 Original multi-transaction model 的语义差异仍限制等价和跨模型解释；
- provenance 不完整的历史控制实验不能用于新主张；
- 当前证据不足以支持大型真实合约的通用可扩展性。
