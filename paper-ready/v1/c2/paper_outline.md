# 论文完整结构大纲

> 工作稿定位：面向属性模糊测试的智能合约交易序列 Harness 合成方法。每节都应围绕窄定位组织，不能将外部 Harness 包装成新的 Echidna 替代品。

## 1. Introduction

- **本节目标：** 说明有状态智能合约的多交易触发困难，提出属性定向 Harness synthesis preprocessing 的问题，并给出明确的研究边界与贡献。
- **应该写什么：** 状态依赖、交易顺序、重复调用和参数约束如何扩大搜索空间；Echidna 的 property-based fuzzing 位置；为什么从显式 safety property 出发；为什么把工作放在 fuzzer core 之外；本文的受控与有限公开评价范围。
- **使用哪些证据：** `paper-ready/00_PROJECT_SUMMARY.md`；C1 `paper_decision.md`；C1 claim matrix 中 C01–C04；Formal 机制材料。
- **禁止写什么：** 首次提出状态依赖、首次提出交易序列或重复调用；新的通用模糊测试器；显著优于或普遍优于现有工具；夸大公开任务规模。
- **建议篇幅：** 1200–1800 字。

## 2. Background

- **本节目标：** 统一解释属性模糊测试、状态读写、交易序列、Harness 与两种执行模型的基本概念。
- **应该写什么：** safety property 的判定方式；状态变量的写读依赖；transaction sequence、bounded repeat、value evidence、Top-K；Original multi-transaction model 与 wrapper execution model 的区别。
- **使用哪些证据：** `docs/START_HERE.md`；`docs/v1-restart/SEMANTIC_BOUNDARY_AUDIT.md`；`paper-ready/v1/native_replay_gate.tsv`。
- **禁止写什么：** 把背景概念写成本文独创；过多公式；默认 Harness 与 Original 语义等价。
- **建议篇幅：** 1000–1500 字。

## 3. Motivation

- **本节目标：** 用简单、可检查的例子展示仅依赖状态读写为何不足，以及四类组件分别解决什么障碍。
- **应该写什么：** NoisyFourStep 的无关路径；BranchValue 的值方向；RepeatedCall 的重复访问；ResetExample 的并列候选和 Top-K；明确这些是 controlled benchmarks。
- **使用哪些证据：** `docs/START_HERE.md`；C1 `evaluation_section_draft.md` 的 RQ1 段落；Formal 候选统计。
- **禁止写什么：** 把合成例子说成真实生态样本；把候选减少自动说成端到端加速；把单个例子说成普遍规律。
- **建议篇幅：** 1000–1500 字。

## 4. Method

- **本节目标：** 完整描述 V1 的输入、分析、候选构造、排序与 Harness 生成，并准确界定它是 Echidna 前处理。
- **应该写什么：** property-related state extraction；backward filtering；candidate transaction sequence；bounded repetition；lightweight value evidence；interpretable Top-K；Solidity Harness synthesis；固定候选顺序与仍由 Echidna fuzz 的参数；K1/K5 的含义。
- **使用哪些证据：** `paper-ready/00_PROJECT_SUMMARY.md`；C1 方法定位；`docs/v1-restart/SEMANTIC_BOUNDARY_AUDIT.md`；`analyzer/` 方法入口（仅作实现对应，不改代码）。
- **禁止写什么：** 改写 Echidna core；声称替代 Echidna；把 K1/K5 写成与 Original 等价的交易长度；忽略 caller、atomicity、rollback、value/block/external-call 差异。
- **建议篇幅：** 1800–2500 字。

## 5. Implementation

- **本节目标：** 说明实现管线和可复现记录如何把方法输出变成可审计运行。
- **应该写什么：** 输入、静态分析器、路径生成、Harness 生成、runner、状态分类、运行目录协议、checksum、quarantine 与 parser/status reconciliation。
- **使用哪些证据：** `docs/V1_EXPERIMENT_WORKFLOW.md`；`paper-ready/v1/evidence_index.tsv`；`docs/v1-restart/PAPER_EVIDENCE_LOCK.md`；B4 run closeout。
- **禁止写什么：** 把运行链完整写成安全证明；把 `budget_exhausted` 写成通过；使用 `matched-random-v1`；掩盖 parser/status mismatch 的阻塞含义。
- **建议篇幅：** 800–1200 字。

## 6. Evaluation

- **本节目标：** 以 RQ1–RQ4 组织受控机制、公开任务、运行链和语义边界评价。
- **应该写什么：** Formal controlled benchmarks；四个 supported public tasks；Original/Full-K1/Full-K5；seed 1–10；120 runs；任务/方法描述性表；118/2 状态解释；120/120 完整和 checksum；semantic caveat；不使用 Total calls speedup。
- **使用哪些证据：** C1 `evaluation_tables.md`、`evaluation_section_draft.md`；`main10_results_summary.tsv/md`；`public_benchmark_registry.tsv`；`native_replay_gate.tsv`；B4 run/closeout。
- **禁止写什么：** 显著性、p-value、superiority、speedup；把 `main_table_usable=conditional` 改成 yes；把四个任务说成生态代表；纳入 exercise2 或 excluded tasks。
- **建议篇幅：** 2500–3500 字。

## 7. Threats to Validity

- **本节目标：** 让读者清楚结果的内部、外部、构念、语义和复现边界。
- **应该写什么：** 任务少、seed 少、配置不同、任务适配、static gate、wrapper 语义、指标构念、外部 baseline 缺失、matched-random quarantine。
- **使用哪些证据：** C1 `threats_to_validity_draft.md`；`SEMANTIC_BOUNDARY_AUDIT.md`；`PAPER_EVIDENCE_LOCK.md`；`claim_evidence_matrix.tsv`。
- **禁止写什么：** 用产物完整掩盖语义风险；把 4 个任务外推到生态；将没有做的工具级比较写成结果。
- **建议篇幅：** 1500–2200 字。

## 8. Related Work

- **本节目标：** 提供不编造文献细节的定位框架，并说明本文与既有方向的关系。
- **应该写什么：** Echidna/property-based fuzzing；stateful fuzzing；transaction sequence generation；static/dynamic data-flow guidance；invocation ordering/branch revisiting；sequence-aware mutation；symbolic/language-model assisted reasoning；本文的组合差异。
- **使用哪些证据：** `paper-ready/00_PROJECT_SUMMARY.md` 的方法定位和外部基线边界；仓库中已出现的工作名称。
- **禁止写什么：** 编造论文、年份、数据或精确机制；声称首次提出状态依赖、重复调用或值引导；把本文写成替代既有工具。
- **建议篇幅：** 1200–1800 字，后续补精确引用和 BibTeX。

## 9. Conclusion

- **本节目标：** 总结窄范围贡献、证据和限制，提出可执行的后续研究。
- **应该写什么：** 方法是 Echidna 前处理；受控机制证据；四任务 120-run 描述性结果；完整 provenance；语义 caveat；更多 public benchmark、caller-controlled replay、外部 baseline、语义对齐和规模扩展。
- **使用哪些证据：** C1 `paper_decision.md`；C1 Evaluation/Threats 草稿；B4 summary。
- **禁止写什么：** 用结论升级为通用安全检测器、显著优势、speedup 或完全等价。
- **建议篇幅：** 500–800 字。

## 推荐附录

1. 运行级 manifest、状态与 checksum 索引；
2. Formal controlled benchmark 的候选路径和组件对照；
3. 公开任务来源、适配和编译器配置；
4. Harness/Original 语义差异的固定路径复核；
5. excluded、conditional 与 quarantine 项清单。
