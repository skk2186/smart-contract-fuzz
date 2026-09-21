# C11 研究契约：论文收敛边界

## Paper target

本文面向 CCF-C 级别的“小创新、闭环、可复现”目标，研究一种位于 Echidna 之前的属性定向交易序列规划与 Harness 生成流程：给定一个显式 Echidna safety property，先从该 property 的 read-set 推导写入函数和有界状态依赖路径，再进行重复次数约束、轻量值证据排序和 Top-K 选择。论文的可核验目标是说明“属性级规划能够在受控多属性干扰场景中减少跨属性候选污染，并保留明确的 provenance 与执行边界”；论文不把该流程表述为新的通用 fuzzing engine，不把小规模适配真实源代码结果表述为生态泛化，也不把 Harness 执行模型表述为与原生 Echidna 多交易执行完全等价。

## Problem statement

当前 legacy planner 会把同一合约全部显式 `echidna_` property 的读取变量做 union，再用这个 union 推导 target functions 和候选路径。多个属性读取不同终态变量时，属于其他属性的状态依赖路径可能进入当前目标 property 的候选池，并在 Top-K 中占据位置。其结果是：候选序列的生成对象与当前要评估的 property 之间缺少明确的 property identity，后续 Harness 还可能暴露全部 `echidna_` proxy，使得针对 P1 生成的序列被 P2 的失败所干扰。

## Gap statement

已有 V1 材料已经覆盖 property/dependency/repeat/value/Top-K/Harness 的组件和运行证据，但 C11 需要把“多个 property 的 union 行为”和“单一 property 的独立规划”明确区分，并使 property identity 从 resolver、read-set、target functions、paths、value-guided 后处理一直传递到 Harness。现有受控结果能够检验这种候选隔离机制；它不能填补真实生态泛化、跨工具公平比较或原生与 Harness 语义等价方面的证据缺口。该边界与 `paper-ready/v1/d0/experimental_weakness_review.md`、`paper-ready/v1/b5/b5_cvenue_sufficiency_review.md` 和 `paper-ready/v1/review/c10_supervisor_review_draft.md` 的审计结论一致。

## Method statement

1. `analyzer/generate_property_sequences.py` 保留无 `--property` 时的 legacy union 行为；显式 `--property` 时，先解析一个确实存在的 `echidna_` property，再只使用该 property 的 read-set，推导 target functions、dependency edges 和 relevant paths。带 `(` 的 requested name 只做 exact full-name match；不带 `(` 时才允许 basename match，多个候选时 fail closed。
2. `analyzer/generate_repetition_aware_sequences.py` 在显式 property 模式下只对选中 property 的变量和写入函数做 bounded repetition，同时保留 `--max-function-visits`、`--max-expansions` 及既有排序限制；无 `--property` 时继续使用 legacy union 语义。
3. `analyzer/generate_value_guided_sequences.py` 作为后处理排序器运行 lightweight value evidence，只计算已有的 match/conflict/unknown 证据，不引入 SMT、符号执行、mapping 推理、跨合约推理或复杂算术推理。它保留输入路径中的 `property_function`，并输出 property/value 分项分数和 `value_rank`。
4. `analyzer/generate_harness_from_paths.py` 在显式 property 模式下只加载匹配该 property 的 contract/path provenance，只生成一个目标 property proxy；property 不存在、完整签名不匹配、路径 provenance 不匹配或 property 带参数时 fail closed。无 `--property` 时保留 legacy 的全部零参数 `echidna_` proxy 行为。
5. 评估分为三层：已有 formal/controlled 组件证据；`results/per-property-isolation/summary.json` 的单一受控多属性隔离证据；已有少量 public/adapted real-source 记录的描述性可执行性证据。三层不得 pooled 成“真实合约总体性能提升”。

## Accepted contribution claims

1. **属性级候选隔离机制。** 对显式目标 property 独立使用 read-set、target functions 和 backward dependency paths，能够在受控多属性干扰场景中降低无关候选污染，并改善该场景中预先定义目标序列的候选排名。
2. **可组合且可追溯的序列规划实现。** bounded repetition、轻量 value-guided ranking 和 Top-K 可以在保持 `property_function` provenance 的条件下接入规划流程，同时保留未指定 property 时的 legacy union 接口。
3. **诚实的执行与证据边界。** 论文明确区分原生 Echidna 多交易与生成 Harness 的执行模型，区分 `falsified`、`budget_exhausted` 和 `compile_error`，并把 controlled 与小规模 adapted real-source 结果分别解释为机制证据和范围内描述性证据。

## Forbidden claims

以下说法在当前证据下不能出现，除非未来有全新的、预注册且语义可比的证据；本阶段不新增这些证据：

- “该方法在真实合约生态中普遍优于 Echidna、SMARTIAN 或其他 baseline。”
- “per-property planning 提升了所有合约上的 fuzzing 性能、检测率或安全性。”
- “`MultiPropertyInterference.sol` 证明了真实生态中的泛化能力。”
- “Original 与 Harness 是完全等价的 Echidna 多交易执行，或可以直接比较安全率。”
- “`budget_exhausted` 表示 property safe、通过或没有漏洞。”
- “`compile_error` 表示检测失败、没有漏洞或方法性能差。”
- “Total calls 更少因此更快，或可以直接宣称 speedup。”
- “checksum、artifact completeness 或 static gate 证明了安全性、独立复现或语义等价。”
- “四个 adapted/public candidate 足以代表真实合约总体。”
- “已有窄范围 SMARTIAN 材料构成公平的第二个工具级 baseline。”
- “该工作实现了 SMT、symbolic execution、mapping inference、跨合约推理或复杂算术推理。”

## Scope boundary

- `results/per-property-isolation/summary.json` 是一个受控机制结果：它支持“属性级规划减少跨属性候选干扰”，不支持真实合约总体性能、漏洞发现率、速度或安全性结论。
- 现有 public/adapted real-source 证据来自有限候选和有限 seed/config；`paper-ready/v1/review/c10_supervisor_review_draft.md` 与 `paper-ready/v1/b5/b5_6_paper_claims.md` 已明确其为范围内描述性结果。
- `budget_exhausted` 只表示在给定预算、seed 和配置内没有观察到反例，是 right-censored observation；不能改写为 safe。
- `compile_error` 是工程/适配状态；不能进入检测成功率的分母或分子，除非另行定义并报告工程可运行性指标。
- Harness proxy 会改变调用者、交易边界、回滚/atomicity、`msg.value`、block context 和外部调用语义。生成 Harness 的 compile smoke 或 proxy 存在，不证明与原生多交易执行等价。
- 当前 Harness 显式模式只支持无参数 property；带参数 property 必须报错，不能 silent fallback 到另一个 property。
- 当前 claim 只覆盖静态规划和已有 lightweight value evidence；不延伸到 solver、symbolic execution、mapping 或跨合约语义。
- 结果解释必须遵守冻结边界：不修改 `results/formal/`、`results/formal-b2/`、`results/public-benchmarks/c1/`、`results/paper-data/` 中已有冻结证据，也不以新代码重新解释旧日志。

## Final recommended titles

1. **面向显式安全属性的智能合约多交易序列规划**
2. **属性级状态依赖与轻量值引导的智能合约模糊测试序列生成**
