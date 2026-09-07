# C4 人工检查清单

本清单用于在补引用、制图表和进入 C5 正文精修前逐项复核。当前阶段只生成计划与占位，不执行实验。

## 引用核验

- [ ] 每个 citation_slots.tsv 条目已找到原始论文、官方文档、artifact repository 或 benchmark repository。
- [ ] 已核验正式题名、作者、年份、venue、DOI/URL 和版本。
- [ ] 已确认每条引用确实支持对应 claim，而不是仅名称相似。
- [ ] TODO_VERIFY 与 NOT_FOUND_LOCAL 已全部处理，未把占位条目直接当正式引用。
- [ ] references_todo.bib 已由人工核验后的 BibTeX 替换。
- [ ] Related Work 未声称首次提出状态依赖、交易序列、重复调用或值引导。
- [ ] 尚未对 SMARTIAN、MuFuzz、IR-Fuzz 等作未经执行的工具级排名。

## 图表制作

- [ ] Figure 1 PHS 方法总览图准确表示 Echidna 仍是下游执行平台。
- [ ] Figure 2 明确区分 property-directed planning、bounded repeat、value evidence 和 Top-K。
- [ ] Figure 3 标出 caller、atomicity、rollback、msg.value、block context 等语义差异。
- [ ] Figure 4 展示 manifest 到 checksum 的 provenance 链，并标明 quarantine。
- [ ] Table 1 分开四个 supported public tasks 与 exercise2-access-control conditional task。
- [ ] Table 2 只呈现 controlled mechanism evidence，不加入生态级外推。
- [ ] Table 3 保持 Original / Full-K1 / Full-K5、4 tasks、10 seeds、120 runs。
- [ ] Table 4 保留 allowed vs forbidden claims 的边界。
- [ ] Table 5 同时写 threat、mitigation 和 remaining limitation。
- [ ] Appendix A1--A3 的字段均有真实源文件支持，未展开不存在的 run-level 数据。
- [ ] 所有图表编号、表注、数据来源和正文交叉引用一致。

## 证据与数字

- [ ] 120 runs、118 falsified、2 budget_exhausted 在摘要、正文、表格和附录一致。
- [ ] 120/120 artifact complete、120/120 checksum pass、0 parser/status mismatch 一致。
- [ ] 0 startup_error、0 unknown_error、0 incomplete 的状态说明一致。
- [ ] budget_exhausted 从未写成 property passed、通过、合约安全或无漏洞。
- [ ] 没有使用 Total calls 形成 speedup 或加速主张。
- [ ] main_table_usable=conditional 未被改成 yes。
- [ ] matched-random-v1 仍处于 provenance quarantine，不进入新的主表或主张。
- [ ] B2/static gate 没有被写成完整 native EVM replay。

## 范围与语义

- [ ] public benchmark 仍明确只有四个 supported public tasks。
- [ ] exercise2-access-control 仍单列为 conditional，未并入 supported pooled。
- [ ] Original multi-transaction model 与 wrapper execution model 的语义差异在 Method、Evaluation 和 Threats 中均有说明。
- [ ] PHS 仍被描述为外部 property-directed preprocessing，不是新的完整 fuzzer。
- [ ] Full-K1/Full-K5 的 K 被解释为候选 Harness 条目数量，不是 Original 等价交易长度。
- [ ] 论文正文不出现内部阶段编号、代理名称或流程提示词。

## 进入 C5 的判断

- [ ] 需要 B5 补 benchmark：是 / 否 / 待讨论；若需要，先单独形成研究问题和纳入规则。
- [ ] 需要 exercise2 caller-controlled appendix：是 / 否 / 待讨论；若需要，必须保持与 supported pooled 分离。
- [ ] 所有正式引用已经人工核验：是 / 否。
- [ ] 图表已按真实字段制作并人工检查：是 / 否。
- [ ] 可以进入 C5：是 / 否；理由：____________________________。

未完成任何一项引用或语义核验时，不应把本目录材料视为最终论文参考文献表或投稿版图表。
