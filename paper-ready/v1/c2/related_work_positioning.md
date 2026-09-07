# 8 Related Work 定位草稿

> 本节是定位框架，不是完整文献综述。下列方向的精确论文、版本、数据集和 BibTeX 需要后续人工核验与补充；本文不在没有核实的情况下编造引用。

## 8.1 Echidna 与 property-based smart-contract fuzzing

Echidna 代表了以显式属性为中心的智能合约模糊测试工作流：研究者给出合约、可检查的 safety property 和测试配置，工具探索输入与交易并寻找反例。本文把 Echidna 作为后续执行与属性判定组件，关注的是在其之前根据 property 规划候选 transaction sequence 并生成外部 Solidity Harness。本文不是 Echidna 的替代实现，也不修改其 core。

后续应补充 Echidna 的正式论文或官方文档引用，并精确区分属性表示、交易生成和本文外置 preprocessing 的职责边界。（待补引用）

## 8.2 Stateful smart-contract fuzzing

有状态智能合约模糊测试关注跨调用状态积累、交易顺序和多步触发条件。本文与该方向的问题对象一致，但不声称首次提出状态依赖或状态序列探索。本文选择一个较窄的工程位置：从显式 property 读取的状态出发，过滤相关写入，并把候选顺序显式输出为 Harness，供既有属性模糊器继续探索。

后续需要人工补充能够准确代表 stateful fuzzing 的论文，并避免把一般的状态依赖问题误写成本文独创。（待补引用）

## 8.3 Transaction sequence generation 与 invocation ordering

交易序列生成、函数调用排序和 invocation ordering 研究如何构造更可能到达目标状态的多调用路径。本文使用 transaction sequence、bounded repeat 和 Top-K，但这些概念本身不是新的。本文的差异在于把 property-directed filtering、外部 Harness synthesis、可解释的组合排序和语义边界审计放在同一条可追溯流水线上。

本文不声称首次提出交易排序、重复调用或分支重访；应在正式版本中通过精确引用说明与既有 sequence generation、invocation ordering 和 branch revisiting 工作的重叠与区别。（待补引用）

## 8.4 Static/dynamic data-flow guided fuzzing

静态或动态数据流引导模糊测试通常利用读写关系、依赖、覆盖反馈或状态变化来指导输入和调用选择。本文同样使用状态读写摘要，但把属性直接读取的状态作为反向过滤起点，并把简单值约束作为局部 value evidence。该设计是外部的、可检查的候选规划，不等于完整动态数据流反馈，也不等于符号执行。

应后续核验 SMARTIAN、MuFuzz、IR-Fuzz 及相关工作的原始论文和工具说明，具体比较它们的数据流、序列和反馈机制；当前材料不支持工具级性能排名。（待补引用）

## 8.5 Sequence-aware mutation 与 branch revisiting

序列感知变异关注如何在多调用上下文中修改前缀、顺序或参数；branch revisiting 关注重新访问能改变状态的分支。本文的 bounded repeat 与 candidate sequence construction 可以与这些问题对照，但仅在预声明的上限内生成重复，并不改变 Echidna 的通用变异核心。ResetExample 和 RepeatedCall 的结果用于说明受控障碍，而不是宣称覆盖该方向的全部技术。

正式论文需要选择可核验的代表性工作，描述共同点与差异，不应把重复调用或分支重访写成首次提出。（待补引用）

## 8.6 Symbolic 与 language-model assisted transaction reasoning

符号方法和语言模型辅助方法可能利用约束、调用图、自然语言意图或合约上下文来推理交易顺序和参数。本文只使用简单常量写入与 require 条件作为 lightweight value evidence，没有声称拥有完整符号求解能力，也没有使用语言模型生成结果作为实验输入。两者都可以被视为未来可替换或可组合的候选规划信号。

后续相关工作应补充原始论文和准确的系统边界；不能将本文的局部值匹配扩大为符号执行或语言模型推理贡献。（待补引用）

## 8.7 本文的定位差异

本文不是替代上述方法，也不是一个新的通用智能合约模糊测试器。更准确的差异表述如下：

| 方向 | 既有问题关注点 | 本文的关系 |
|---|---|---|
| Echidna/property-based fuzzing | 以 safety property 驱动反例搜索 | 作为后续执行器；本文提供外部 preprocessing |
| Stateful fuzzing | 跨调用状态与多交易触发 | 采用其问题场景，不声称首次研究 |
| Sequence generation/order | 产生或排序调用序列 | 以属性相关状态反向过滤并输出候选 |
| Static/dynamic data-flow | 依赖、覆盖和状态反馈 | 使用静态读写与局部值证据，范围更窄 |
| Invocation ordering/branch revisiting | 选择调用顺序或重新访问分支 | 以 bounded repeat 和 Top-K 表达受控候选 |
| Sequence-aware mutation | 对序列和前缀进行变异 | 固定候选顺序，仍把参数探索交给 Echidna |
| Symbolic/LM reasoning | 约束或上下文驱动的交易推理 | 当前不是完整求解或语言模型推理系统 |

本文的组合差异是 property-directed preprocessing + external Harness synthesis + interpretable Top-K + semantic boundary audit。贡献重点是组合方式的可解释性、产物 provenance 和语义边界，而不是对状态依赖、重复调用、交易序列、分支重访或值引导提出绝对首创主张。
