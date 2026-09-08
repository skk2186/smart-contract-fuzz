# C5 Citation Gap Report

## 当前引用状态

本审计基于 `paper-ready/v1/c4/citation_slots.tsv`、`references_todo.bib`、Related Work 修订计划、术语表、C4 citation markup 和 evidence crosswalk。仓库检索只发现 `paper-ready/v1/c4/references_todo.bib`，没有发现人工核验的 `references.bib`、`references_verified.bib` 或其他 verified reference 文件。

C4 共列出 28 个 citation slots。当前没有任何 slot 可以标记为 `VERIFIED_LOCAL`；C5 checklist 全部保留为 `TODO_VERIFY`。关键状态如下：

- Echidna 原始论文和官方文档仍需核验（CIT-001--002）。
- Harvey、ConFuzzius、SMARTIAN、IR-Fuzz、MuFuzz、SmarTest 等相关工作仍只有候选名称和 claim boundary，没有正式书目信息（CIT-003--010、CIT-013、CIT-027）。
- Mythril、Oyente、ILF、ContractFuzzer、sFuzz、EthPloit 仍需确认原始论文、官方文档或适当来源（CIT-011--017）。
- SmartBugs、SmartBugs Curated、Daedaluzz 需要核验 benchmark/dataset 角色、版本、许可证和本文任务映射（CIT-018--020、CIT-023）。
- artifact/reproducibility 指南、Echidna artifact repository、native replay 资料和 controlled benchmark 设计来源仍需人工选择与核验（CIT-021--022、CIT-024--026、CIT-028）。

## 投稿前必须补

以下内容会直接影响终稿是否能对外提交：

1. 至少为正文已经使用的 Echidna、property-based fuzzing、stateful fuzzing 和 transaction-sequence claims 补正式来源。
2. 为 Related Work 中实际点名的 SMARTIAN、IR-Fuzz、MuFuzz、Harvey、ConFuzzius、SmarTest、Mythril、Oyente、ILF、ContractFuzzer、sFuzz 和 EthPloit 逐项确认引用是否真的支持对应句子。
3. 为 SmartBugs/SmartBugs Curated 以及四个 supported public tasks 的 provenance 说明补正式 benchmark 来源；不要用任务名代替来源。
4. 为 artifact/provenance 报告原则和 native replay/static gate 区分补适合目标 venue 的正式指南或官方来源。
5. 建立正式 BibTeX 与 citation slot 的一一映射，并清理 C4 markup 中 `CITE:ECHIDNA_DOC`、`CITE:SYMBOLIC_ANALYSIS` 等尚未和 slot/key 对齐的语义标记。

没有完成这些步骤前，论文不能作为最终投稿版本。

## 可选补强

以下引用可在版面有限时缩减，但若保留对应段落，则仍需核验：

- Daedaluzz 作为 benchmark generation 方向的背景；
- Mythril/Oyente 作为历史符号分析背景；
- artifact evaluation 的次级指南；
- controlled benchmark design 的方法学依据；
- native replay 的官方工具或规范说明。

“可选”只表示可以删去对应背景句，不表示可以保留未经核验的事实句。

## Related Work 分节缺口

| 小节 | 现有缺口 | 投稿前处理 |
|---|---|---|
| Echidna 与属性模糊测试 | 缺原始论文/官方文档；需要确认 property、assertion 和执行模型措辞 | 补 CIT-001、CIT-002；保留 PHS 是外部 preprocessing 的定位 |
| 有状态模糊测试与交易序列 | Harvey、ConFuzzius 的正式题名和可支持表述未核验 | 补 CIT-003、CIT-004、CIT-026；不写首次提出 |
| 数据流、调用排序、分支重访 | SMARTIAN、IR-Fuzz 以及 Harvey 的术语边界未核验 | 补 CIT-005--008；不写工具级比较 |
| 序列感知变异 | MuFuzz 的正式来源和与 PHS 的接口差异未核验 | 补 CIT-009、CIT-027；写成邻近方向 |
| 符号与语言模型辅助 | SmarTest、Mythril、Oyente、ILF 的抽象层次未核验 | 补 CIT-010--014；不要把轻量 value evidence 等同完整求解 |
| 智能合约 fuzzing/input generation | ContractFuzzer、sFuzz、EthPloit 的角色未核验 | 补 CIT-015--017；删除不必要的背景句也可 |
| benchmark/dataset | SmartBugs、SmartBugs Curated、Daedaluzz 与本文任务映射未核验 | 补 CIT-018--020、CIT-023；区分 source、registry 和结果 |
| reproducibility/artifact | 指南和工具仓库引用未核验 | 补 CIT-021、CIT-022、CIT-028 |

## 必须加引用或明确本地证据的句子类型

- “Echidna 代表 property-based smart-contract fuzzing”以及对其输入、property 和执行模型的概括。
- “已有 stateful fuzzing/work 处理多交易、状态推进、数据流、调用顺序或 sequence-aware mutation”的方向性句子。
- 对 SMARTIAN、IR-Fuzz、MuFuzz、SmarTest、ILF 等工作方法边界的具体描述。
- SmartBugs、SmartBugs Curated 和 Daedaluzz 的 benchmark/dataset 身份、版本和任务来源。
- provenance/checksum/artifact evaluation 是何种可复现性实践的背景句。
- native replay、static gate 与调用者/交易语义的规范性说明。

下列内容主要由本地证据支持，不应被引用替代：120-run 的计数、118 falsified、2 budget_exhausted、120/120 artifact/checksum、四个 supported tasks、exercise2 的 conditional 分类和 `main_table_usable=conditional`。这些应继续引用本地表格、evidence index 或表注。

## 无正式引用时不能保留的写法

- 带有作者、年份、venue、DOI、URL、具体实验数字或精确工具差异的相关工作句子。
- “某工作首次提出”“某工作保证”“某工作显著改善”之类超出候选槽位的断言。
- 把 SmartBugs 全部资源等同于本文四个 supported public tasks。
- 把 static gate 写成 native EVM replay，或把 artifact completeness 写成安全性/独立复现证明。
- 把 SMARTIAN、MuFuzz、IR-Fuzz 等候选工作写成 PHS 已经击败或替代的工具。

## 为什么 `references_todo.bib` 不是正式 references

该文件明确写着 `Placeholder bibliography for C4`，条目使用 `TODO_*` key，title 和 note 中保留 `TODO VERIFY`，没有作者、年份、venue、DOI、URL 或经核验版本。它只能作为人工待办清单，不能证明任何候选工作的正式身份，也不能支撑论文引用。

当前尚不能生成正式 `references.bib`。在人工逐条核验完成、slot/key 映射建立并复查 claim support 之前，必须保留 `TODO_VERIFY` 状态。

## 结论

C5 可以生成引用核验包并进入正文精修，但正式引用是最终投稿的硬阻塞项。引用缺口不改变 B4 数字、不要求本阶段补实验，也不能通过把 citation slot 或 TODO BibTeX 当作正式文献来“填平”。
