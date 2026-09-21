# C13 Supervisor Cover Note

## 当前论文一句话定位

本文研究的是一种位于 Echidna 属性模糊测试之前的属性定向多交易序列规划与 Harness synthesis 流程：对每个显式安全 property 独立使用 read-set、target functions、backward dependency paths、bounded repetition、lightweight value ranking 和 Top-K，并保留 property provenance。

## 当前不再继续实验的理由

C11 已将实验冻结决策定为不继续新增实验，C12 也已按该决策完成正文重写。现有材料已经能够回答核心机制问题：在受控多属性干扰场景中，property-specific planning 是否减少无关候选并改善目标序列 rank。当前缺口主要是更广泛的外部有效性、更多公平 executable baseline 和引用/版式收尾，它们不是通过无目标增加 seed 或运行次数即可诚实解决的问题。继续实验还会引入新的方法版本、运行配置和结果边界，反而增加 V1 证据的解释负担。

## 当前最核心创新点

最需要导师确认的创新点是 **property identity 参与候选规划，而不是只作为结果标签**。显式 property 决定 read-set、target functions、依赖路径、重复扩展、value-guided ranking、Top-K 和 Harness proxy；这使多 property 合约中的跨属性候选污染可以被单独定义和度量。legacy union 行为仍保留，per-property 是通过显式 `--property` 进入的新模式。

## 当前主要证据

- `results/per-property-isolation/summary.json`：在 `MultiPropertyInterference` 中，LEGACY_UNION 使用 3 个 property variables、3 个 target functions，得到 8 个候选，其中 7 个无关，ratio 为 0.875，目标 rank 为 6，Top-1/3/5 均未命中；PER_PROPERTY 使用 1 个变量、1 个 target function，得到 1 个候选，无关候选为 0，目标 rank 为 1，Top-1/3/5 均命中。
- C10 已审计的六个 controlled scenarios：Full-K1 在 180 次运行中观察到 180 次属性违反，Original 观察到 171 次。该证据用于组件机制解释，不用于生态级排序。
- C10 已审计的 adapted real-source records：4 个 candidate、120 条预注册运行、79 条 `falsified`、1 条 `budget_exhausted`、40 条 `compile_error`。这些记录用于说明运行状态和适配边界。
- `analyzer/generate_property_sequences.py`、`analyzer/generate_repetition_aware_sequences.py`、`analyzer/generate_value_guided_sequences.py` 和 `analyzer/generate_harness_from_paths.py` 的代码边界已由 C11/C12 归纳，包含 full-name resolver、property provenance、bounded controls、lightweight value evidence 和目标 proxy。

## 当前主要边界

- `MultiPropertyInterference` 是 controlled mechanism benchmark，只支持“属性级规划减少跨属性候选干扰”，不能支持真实生态泛化或整体性能结论。
- `candidate count`、`target rank` 和 Top-K hit 是规划层指标，不是动态漏洞发现率。
- `budget_exhausted` 是预算内未观察到反例的 right-censored 状态，不表示 property safe 或 test pass。
- `compile_error` 是构建、导入或 Harness 适配的工程状态，不是 detection failure。
- Original Echidna 多交易和 Harness 在 caller、transaction boundary、rollback/atomicity、`msg.value`、block context 和 external-call behavior 上可能不同，不能按同一 execution model 解释。
- 当前没有对 SMARTIAN、ConFuzzius、Harvey、MuFuzz、IR-Fuzz 或 SmarTest 做同 oracle、同 caller、同 budget 的公平工具级比较。
- 4 个 adapted real-source candidates 不能代表真实合约生态。

## 希望导师确认的 5 个问题

1. 标题是否最终采用 **《面向显式安全属性的智能合约多交易序列规划》**，而不再使用暗示通用性或效率的标题。
2. `MultiPropertyInterference` 表格是否作为正文主机制结果保留，六场景 controlled package 与 adapted real-source 汇总如何分配正文和附录版面。
3. Harvey、ConFuzzius、SMARTIAN、MuFuzz、IR-Fuzz、SmarTest 的正式引用、cite key 和方法描述是否已完成 citation registry 核验。
4. C12 的三项贡献和三个 RQ 是否符合 CCF-C 的创新闭环要求，尤其是把贡献定位为 candidate planning/Harness synthesis，而不是新的通用 fuzzer。
5. C12 文末的“禁止扩大解释清单”是否从投稿正文移入附录或审计材料，并将其中必要的语义边界合并到 threats 与结果口径。

## 建议导师优先看的文件顺序

1. `paper-ready/v1/c13/c13_next_decision.md`
2. `paper-ready/v1/c13/c13_submission_readiness_audit.md`
3. `paper-ready/v1/c12/c12_rewritten_paper_draft.md`
4. `paper-ready/v1/c13/c13_minimal_patch_list.md`
5. `paper-ready/v1/c11/claim_evidence_matrix.md`
6. `results/per-property-isolation/summary.json`
7. `paper-ready/v1/c12/c12_rewrite_notes.md`
8. `paper-ready/v1/c11/research_contract.md` 与 `paper-ready/v1/c11/experiment_freeze_decision.md`

本审计包只支持导师审阅前的判断，不改变 C12 正文或任何冻结实验结果。
