# C11 论文修改计划（针对 `c10_supervisor_review_draft.md`）

本计划只修改论文叙事和证据映射，不修改冻结结果，不新增实验。所有新增数字必须直接来自 `results/per-property-isolation/summary.json`；C10 原有数字继续以 `paper-ready/v1/review/c10_supervisor_review_draft.md`、`paper-ready/v1/b5/b5_6_paper_claims.md` 和对应冻结结果为准。

## Title

将当前的“面向显式安全属性的智能合约多交易模糊测试方法”收窄为不暗示通用 fuzzer 或普遍性能的标题。优先使用：

- **面向显式安全属性的智能合约多交易序列规划**
- **属性级状态依赖与轻量值引导的智能合约模糊测试序列生成**

标题中不要使用“通用”“高效”“state-of-the-art”“性能提升”或“优于现有工具”。

## Abstract

按以下顺序重写：

1. 一句话定义问题：legacy union-property planner 会让不属于目标 property 的状态依赖路径进入候选池。
2. 一句话定义方法：本文提出/实现的是 Echidna 前的 property-directed sequence planning 与 Harness synthesis，不是新的独立 fuzzing engine；流程包括 property-specific read-set、target functions、backward paths、bounded repetition、lightweight value ranking 和 Top-K。
3. 一句话给出新增受控结果，严格写成机制结果：在 `MultiPropertyInterference` 中，LEGACY_UNION 使用 3 个 property variables、产生 8 个候选且 7 个与 P_TARGET 无关，目标序列 rank=6；PER_PROPERTY 使用 1 个变量、产生 1 个候选、无关候选为 0，目标 rank=1，Top-1/3/5 命中。
4. 一句话概括既有 controlled/formal 包，说明它支持组件机制而非生态总体性能。
5. 一句话概括 4 个 adapted real-source candidate 的状态分类，使用“有限、描述性、受适配影响”的限定，不把 `budget_exhausted` 当安全，不把 `compile_error` 当检测失败。
6. 末句明确限制：Original 与 Harness 不是完全等价执行模型，本文不宣称真实生态普遍 superiority。

摘要中删除任何“提升整体检测率”“显著更快”“优于现有方法”等未被证据直接支持的句子。

## Introduction

建议改为四段：

1. **现象。** 用两个 property 读取不同终态变量的简短例子说明 union read-set 如何污染当前目标的候选池，并指出候选 rank/Top-K 受干扰。
2. **研究问题。** 明确本文问的是“是否可以把 property identity 贯穿 read-set、target functions、paths、ranking 和 Harness”，不是“是否发明了新的通用 fuzzing engine”。
3. **方法定位。** 把工作定位为 Echidna 前的可复现输入规划和 Harness synthesis；说明无 `--property` 的 legacy 行为仍保留，显式 `--property` 进入 per-property 模式。
4. **证据与边界。** 说明 controlled mechanism evidence、有限 adapted real-source descriptive evidence、Original/Harness 执行模型差异、seed/config/候选规模限制。此处应主动写出 controlled scenario 不能代表真实生态。

不要在 Introduction 中把 4 个 adapted candidate 写成“real-world benchmark”，不要把旧 union 行为写成错误到足以支持普遍性能结论，也不要暗示静态路径证据等于完整 fuzzing 搜索证据。

## Contributions

将当前 4 条贡献收敛为最多 3 条：

1. **Property-specific planner：** 对显式 property 独立解析 full-name/read-set，推导 target functions 和 backward dependency paths，并对 resolver ambiguity/full-signature mismatch fail closed；未指定 property 时保留 legacy union。
2. **可组合的 bounded planning：** 在 property identity 不丢失的前提下接入 bounded repetition、lightweight value evidence、Top-K 和 property-specific Harness proxy。
3. **受控且有边界的证据：** 通过 formal/controlled 组件结果和 `MultiPropertyInterference` 证明候选隔离机制；用有限 adapted real-source 记录说明可执行性和限制，明确不做跨生态 superiority 或 Original/Harness 等价 claim。

删除“提出了新的通用 fuzzing engine”“证明了整体检测率提升”“全面超过现有工作”等贡献表述。

## Method

把方法章节改成从 identity 到 Harness 的单向数据流，并在每个阶段标出 legacy/per-property 分支：

1. `resolve_property_function`：请求带 `(` 时 exact full-name；不带 `(` 时 basename；多个 basename 候选时 ambiguous/fail closed。该规则必须在三个脚本中一致。
2. `read-set -> target functions`：显式模式只使用选中 property 的 read variables；legacy 模式保留全体 property 的 union。
3. `build_edges -> build_relevant_paths`：说明写入/读取变量形成的有向依赖，以及 length/score/Top-K；不要把静态候选路径说成完整运行时可达性证明。
4. `generate_repetition_aware_sequences`：说明 selected property 的 target-specific bounded repetition、`max-function-visits` 和 `max-expansions`；不要把重复次数限制写成自动发现率提升。
5. `generate_value_guided_sequences`：说明它是后处理器，保留 `property_function`、`property_score`、`value_score`、`value_matches`、`value_conflicts`、`value_unknowns`、`value_edges` 和 `value_rank`；明确只用 lightweight literal evidence。
6. `generate_harness_from_paths`：显式模式只加载相同 property provenance、只生成一个 proxy、参数 property/error/mismatch fail closed；legacy 模式生成全部零参数 `echidna_` proxy。
7. 单独增加“Execution-model boundary”小节：比较 Original/Harness 的 caller、transaction boundary、rollback/atomicity、`msg.value`、block context 和 external-call 语义差异；明确 Harness compile smoke 不是 native replay equivalence。

## Evaluation RQs

把 C10 当前四个 RQ 收敛为三个可回答的问题：

- **RQ1（核心机制）：** 在受控的多属性干扰场景中，per-property planner 是否减少无关候选并改善预先定义目标序列的 rank/Top-K？证据是 `results/per-property-isolation/summary.json`，结论只限于 candidate isolation。
- **RQ2（组件行为）：** dependency、bounded repetition、lightweight value evidence 和 Top-K 是否按设计影响候选构造/排序？证据使用既有 formal/controlled 结果；不要把它改写成跨工具性能或真实合约检测率问题。
- **RQ3（外部边界）：** 在有限 adapted real-source pool 上，流程的运行状态、适配失败和执行模型差异是什么？答案是 descriptive，不比较不等价的 Original/Harness 安全率。

将当前 RQ 中可能暗示“哪个方法发现得更多/更快”的措辞改为“候选构造、rank、状态分类和可追溯性”。把完整 seed-by-seed RQ 表移至附录。

## Tables / Figures

正文建议安排：

- **Table 1：** 方法与 provenance schema：property function、property variables、target functions、paths、repeat/value/Top-K、Harness proxy。
- **Table 2：** formal/controlled 组件结果，按机制而不是按“总性能”汇总；图注写明 synthetic/controlled。
- **Table 3：** per-property isolation 单独成表，列出 LEGACY_UNION 与 PER_PROPERTY 的 variable count、target count、candidate count、irrelevant count/ratio、target rank、Top-1/3/5；直接复制 `summary.json`，不重新计算。
- **Table 4：** adapted real-source 状态分类：candidate、method、seed、`falsified`、`budget_exhausted`、`compile_error` 和 comparability note 分开呈现；不要将 compile_error 混入检测率。
- **Figure 1：** 一张短 pipeline：property resolver → read-set → target functions → paths → repeat/value/Top-K → selected Harness proxy，并在 legacy/per-property 分支处标注。
- **Figure 2（可选）：** 只展示 Table 3 的候选污染和目标 rank 对比；不画成真实 fuzzing performance 曲线。
- **Appendix：** 全部逐 seed 状态、完整路径 provenance、命令/环境/checksum、Harness 源码与 compile smoke 说明。

不要做 aggregated “win rate”、总调用数 speedup 图、Original/Harness 混合柱状图或跨 baseline 排名图。

## Threats to validity

将 C10 的 threats 具体改成以下类别，并把每一项与证据文件绑定：

- **Construct validity：** candidate count/rank/Top-K 是规划层指标，不等于完整 fuzzing 可达性或漏洞发现率；`value_score` 是 lightweight evidence，不是 solver 证明。
- **Internal validity：** `MultiPropertyInterference` 是预先设计的 controlled mechanism benchmark，expected sequence 和 `top_k=1000` 必须固定；不能根据结果回改 benchmark、排序或 expected sequence。
- **External validity：** adapted/public pool 只有有限 candidate，不能代表真实生态；D0 和 B5 已明确这种边界。
- **Execution-model validity：** Harness 与 Original 在 caller、交易边界、rollback/atomicity、`msg.value`、block context、external call 上可能不同；compile success 不证明语义等价。
- **Outcome censoring/classification：** `budget_exhausted` 是 right-censored 未观察到反例，`compile_error` 是工程状态；二者不能转写为 safe/detection failure。
- **Statistical/reproducibility：** 既有运行使用有限 seeds/config；报告 descriptive 状态，不做 pooled significance 或跨生态排名。
- **Baseline validity：** SMARTIAN 仅有两个简单整数目标；SMARTIAN、ConFuzzius、Harvey、MuFuzz、IR-Fuzz、SmarTest 在本轮没有一个满足完整公平 executable baseline 条件，因此放在 related work/conceptual positioning。

## Related work：必须如何处理指定工作

- **SMARTIAN：** 作为 data-flow/sequence-guided smart-contract fuzzing 的相关工作定位；指出本论文的差异是 property identity/read-set 驱动的候选规划与 Harness synthesis。不要把仓库中两个简单整数目标的材料写成公平工具级 baseline，也不做总体优越性结论。
- **ConFuzzius：** 作为约束/数据流结合的相关工作；说明本文的 value stage 只做轻量 literal evidence，不声称具备其级别的求解或符号推理能力。没有公平可执行对齐时不列入结果排名。
- **Harvey：** 作为多交易/需求驱动序列探索的相关工作；说明本文侧重显式 property 的静态候选规划，不能把 Harness sequence function 等同于 Harvey 或原生多交易的搜索语义。
- **MuFuzz：** 作为近年序列感知/变异导向工作的背景；说明本文贡献在 property-specific planning/provenance，而不是提出新的 mutation engine。不要因引用它而声称性能领先。
- **IR-Fuzz：** 按 C10/D0 的 conceptual positioning 放置，说明其与本文在 fuzzing pipeline/输入组织上的研究对象不同；没有统一 oracle、caller model、budget 和结果定义时，不做 executable comparison。
- **SmarTest：** 作为序列/语言模型导向智能合约测试的相关工作；明确本文不引入 LLM 或 symbolic execution，也没有证据支持工具级排名。
- Related work 结尾加一句：这些工作用于定位研究问题和设计空间，不是本轮可比 baseline；若未来要纳入结果，必须先满足 `paper-ready/v1/d0/experimental_weakness_review.md` 中关于 oracle、caller model、sequence budget 和 outcome definition 的公平对齐条件。

## 必须删除或降级的句子/说法

在 C10 草稿全文检索并删除或改写以下类别：

- “PHS/new method improves overall fuzzing performance” → 改为“在受控场景中改变候选构造并减少无关 property 路径”。
- “outperforms Echidna/SMARTIAN/other baselines” → 删除；改为“未进行公平工具级比较”。
- “higher detection rate/success rate on real contracts” → 若只来自有限 adapted pool，改为“范围内 observed status/descriptive evidence”，并列出 compile/budget censoring。
- “Harness is equivalent to native multi-transaction execution” → 改为“用于受控输入生成的替代执行模型，存在 caller/transaction/rollback/context 差异”。
- “budget_exhausted means safe/passed/no vulnerability” → 删除，改为“预算内未观察到反例的 right-censored 状态”。
- “compile_error is a failed detection” → 删除，改为“工程/适配不可运行状态，不进入检测结果解释”。
- “fewer Total calls means faster/speedup” → 删除；如果保留调用数，只写 descriptive workload accounting。
- “controlled benchmark demonstrates real-world generalization” → 删除，改为“controlled mechanism evidence”。
- “four public/adapted candidates represent the ecosystem” → 删除，改为“small, preregistered, scope-limited pool”。
- “provenance/checksum proves safety/reproducibility/equivalence” → 改为“支持 artifact traceability”，不扩大为安全或语义证明。

修改后用 `paper-ready/v1/c11/claim_evidence_matrix.md` 逐项反查摘要、引言、贡献、结果和 threats，确保每个正文 claim 都能落到具体路径和限定语上。
