# C12 重写说明

## 相比 C10 的核心叙事变化

1. **研究对象收窄。** C10 的标题和摘要仍容易让读者把工作理解成一种完整的多交易模糊测试方法。C12 将对象改写为 Echidna 之前的 property-directed transaction-sequence planning 与 Harness synthesis，核心问题变成“union-property 候选污染是否可以通过 property identity 隔离”。
2. **per-property isolation 前置。** C12 在摘要、问题定义、RQ1、结果和结论中都单独呈现 `MultiPropertyInterference` 的机器可读结果，而不是把它藏在一般的多属性背景中。
3. **legacy 与新模式分开。** C12 明确写出无 `--property` 继续采用 legacy union，显式 `--property` 才进入新规划模式，避免用新 schema 重新解释旧实验。
4. **方法链条改为 provenance 链。** C10 主要按 dependency/property/repeat/value/Top-K 介绍组件；C12 增加 resolver、selected read-set、target functions、path-level `property_function` 和 Harness fail-closed 校验，使 property identity 成为贯穿流程的控制变量。
5. **实验从四个 RQ 收敛为三个。** RQ1 关注多属性候选干扰，RQ2 关注组件是否按设计改变候选构造和排序，RQ3 关注有限 adapted real-source pool 的状态与边界。没有把“整体检测效率”作为单独 RQ。
6. **执行模型和状态分类进入正文主线。** C12 在方法、实验口径、结果、讨论和 threats 中分别解释 Original/Harness 的差异、`budget_exhausted` 的 right-censored 含义和 `compile_error` 的工程含义。

## 删除或降级的 claim

- 删除把本文描述成通用 fuzzing engine 或生态级方法的表述，改为前置的 candidate planning/Harness synthesis。
- 删除把 controlled scenario 结果外推到真实合约总体的表述，改为 controlled mechanism evidence。
- 删除跨 Echidna、SMARTIAN、MuFuzz、IR-Fuzz 等工具的未经执行排名，只保留 conceptual positioning。
- 将 adapted real-source 结果降级为有限 pool 上的 descriptive evidence，明确 4 candidates、120 runs、79 falsified、1 budget_exhausted 和 40 compile_error 的分层。
- 将 `budget_exhausted` 从任何“通过/安全”含义中移除，改成 right-censored observation。
- 将 `compile_error` 从检测结果中移除，改成构建、导入或 Harness 适配的 engineering status。
- 删除跨 Original 与 Harness 的直接速度、调用量或安全率比较；保留 execution-model boundary。
- 将 lightweight value stage 限定为 constant write/require 的 match、conflict、unknown 证据，不再暗示 solver、symbolic execution、mapping 或复杂算术能力。
- 将贡献从 C10 的四条收敛为 C11 规定的三条。

## 进入正文的实验

- 六个既有 controlled/formal 场景，作为 RQ2 的组件机制证据；正文只报告 C10 已审计的范围，并把结果解释为受控障碍下的观察。
- `results/per-property-isolation/summary.json`，作为 RQ1 的独立结果表，完整保留变量数、target 数、candidate 数、无关候选、ratio、target rank 和 Top-1/3/5。
- 四个 adapted real-source candidates 的汇总状态，作为 RQ3 的小型外部边界检查：120 条预注册记录、80 条 usable/descriptive records、40 条 compile rows，以及 79/1/40 的状态分层。
- 两个 Echidna-origin candidates 的有限可比子集和 SmartBugs Original-only/Harness compile limitation 的解释，但不把它们合并成统一 detection metric。

## 只进入附录的内容

- 逐 candidate、逐 method、逐 seed 的完整状态表；
- 完整 path JSON、property provenance、value edges、repeat expansion 和 Top-K 输入；
- manifest、command、environment、checksum、raw/parsed/status 等复现材料；
- Harness 源码、导入路径和 compile smoke 日志；
- SmartBugs 40 条 engineering rows 的逐条错误信息；
- 两个 Echidna-origin subset 的完整轨迹指标；
- 受控场景的完整候选列表和路径排序细节。

这些内容是复现和审计证据，不应占据正文主结果表，也不应被重新组合成跨模型性能排名。

## 仍需导师确认的事项

1. 最终标题在“多交易序列规划”和“属性级状态依赖与轻量值引导”两个候选之间如何选择。
2. 六场景 controlled package 与 per-property isolation 表在正文中的版面比例，以及 adapted real-source 汇总是否保留为正文短表或移到附录。
3. C10 已有 cite key 的最终格式，以及 IR-Fuzz、SmarTest、MuFuzz 的正式书目信息和方法描述是否已经完成 registry 核验。
4. CCF-C 模板对中文草稿、表格宽度、双栏图注、匿名化和参考文献格式的具体要求。
5. C12 是否将“property-directed sequence planning”固定译为“属性定向交易序列规划”，避免与 Harness synthesis 混称。

## 是否建议继续实验

遵循 C11 的冻结决策：**不建议继续新增实验。**

当前缺少的是更广泛外部有效性或公平第二 baseline，而不是 per-property isolation 核心机制的最小证据。新增运行只有在导师或审稿意见提出一个现有文件无法回答的具体 RQ，并且能够预先固定 oracle、caller model、transaction budget、状态分类和 provenance 时才有理由启动。本阶段只进行正文收敛，不新增 benchmark、seed、baseline，也不修改 `results/` 下的既有结果。
