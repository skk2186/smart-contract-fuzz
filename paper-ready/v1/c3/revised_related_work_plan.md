# 8 Related Work 引用与定位计划（修订稿）

> 本文件只提供待核验的引用槽位，不构成已完成的文献综述。候选工作名称来自当前研究材料和任务要求；作者、年份、会议、版本、实验数字及具体技术细节均需在后续人工检索原始论文或官方材料后补入。

## 1. Echidna 与 property-based smart-contract fuzzing

- **引用槽位：** [CITE-ECHIDNA-PROPERTY]
- **候选代表工作：** Echidna。
- **需要核验的比较点：** safety property 的表达方式；交易和参数探索的职责；本文外部 preprocessing 与既有属性模糊器之间的接口。
- **本文定位：** PHS 以 Echidna 作为后续的属性执行和反例判定组件，不修改其 core，也不把 PHS 写成替代工具。
- **补引用要求：** 选择官方论文或官方文档中的准确来源，并确认版本描述是否需要单独引用。

## 2. Stateful smart-contract fuzzing

- **引用槽位：** [CITE-STATEFUL-FUZZING-1]、[CITE-STATEFUL-FUZZING-2]
- **候选代表工作：** SMARTIAN、Harvey、ConFuzzius。
- **需要核验的比较点：** 跨调用状态建模；多交易前缀或状态到达；静态与动态信息的使用；工具如何定义有效序列。
- **本文定位：** PHS 采用有状态合约中的交易序列问题作为背景，不声称首次提出状态依赖或状态序列探索；差异集中在以 property 读取状态为起点的候选过滤和外部 Harness 输出。
- **补引用要求：** 每个工作只在核验其原始来源后描述具体算法，不从工具名称推断技术细节。

## 3. Transaction sequence generation

- **引用槽位：** [CITE-SEQUENCE-GENERATION-1]、[CITE-SEQUENCE-GENERATION-2]
- **候选代表工作：** Harvey、SmarTest。
- **需要核验的比较点：** 交易序列如何生成、扩展、剪枝或选择；目标状态与序列前缀的关系；参数约束是否与调用顺序联合处理。
- **本文定位：** PHS 生成 transaction sequence 候选，并用 property-directed filtering、bounded repeat 和 Top-K 保留可检查的备选；它不是对既有序列生成方法的替代。
- **补引用要求：** 不使用未经核验的“首次”“更高覆盖”或性能数字；仅补充与方法边界直接相关的事实。

## 4. Static/dynamic data-flow guided fuzzing

- **引用槽位：** [CITE-DATAFLOW-STATIC]、[CITE-DATAFLOW-DYNAMIC]
- **候选代表工作：** SMARTIAN、ConFuzzius、IR-Fuzz。
- **需要核验的比较点：** 状态读写、数据流或依赖信息的获取方式；静态信息和运行时反馈的组合；数据流如何影响序列、参数或路径选择。
- **本文定位：** PHS 使用静态函数读写摘要，并把 property 直接读取的状态作为反向过滤起点；value evidence 只处理简单常量和条件，不等同于完整动态反馈、符号执行或跨合约数据流分析。
- **补引用要求：** 需要逐一核验工作名称与具体技术的对应关系，避免把相同术语误写成相同实现。

## 5. Invocation ordering 与 branch revisiting

- **引用槽位：** [CITE-ORDER-REVISIT-1]、[CITE-ORDER-REVISIT-2]
- **候选代表工作：** Harvey、MuFuzz、IR-Fuzz。
- **需要核验的比较点：** 调用顺序如何影响状态到达；分支或函数的重新访问如何实现；是否使用目标导向、覆盖反馈或状态反馈。
- **本文定位：** PHS 以有界重复表达预先声明的重复访问，并用可解释 Top-K 选择候选；不声称首次提出调用排序、分支重访或重复调用。
- **补引用要求：** 只在原始来源明确支持时描述某工作包含某一机制，不能通过名称或二手摘要补造结论。

## 6. Sequence-aware mutation

- **引用槽位：** [CITE-SEQUENCE-MUTATION]
- **候选代表工作：** Harvey、MuFuzz、IR-Fuzz。
- **需要核验的比较点：** 序列前缀、调用顺序和参数的联合变异；变异反馈；序列长度控制；与静态候选规划的边界。
- **本文定位：** PHS 在生成阶段固定候选 Harness 的调用顺序，把参数探索继续交给 Echidna；这一接口与修改 fuzzer 内部 sequence mutation 的工作不同，但差异需要由精确引用支撑。
- **补引用要求：** 不将“固定候选顺序”描述为一般序列变异的改进，也不从本文的受控结果推断对外部工具的效果。

## 7. Symbolic 与 language-model assisted transaction reasoning

- **引用槽位：** [CITE-SYMBOLIC-REASONING]、[CITE-LM-REASONING]
- **候选代表工作：** ConFuzzius、SmarTest。
- **需要核验的比较点：** 约束求解或语言模型如何参与函数选择、序列生成和参数推理；输入、oracle 和执行模型；静态证据与推理模块的接口。
- **本文定位：** PHS 的 lightweight value evidence 仅匹配简单写入和 require 条件，不声称完整符号求解，也不使用语言模型生成结果作为当前评价输入。符号或语言模型信号可作为未来的候选排序扩展。
- **补引用要求：** 在核验前不写年份、模型名称、训练数据、实验规模或效果数字。

## 8. 竞品与本文方法的统一差异表

| 引用方向 | PHS 应说明的差异 |
|---|---|
| Echidna/property-based fuzzing | PHS 是其前置的 external Harness synthesis preprocessing |
| Stateful fuzzing | PHS 使用有状态交易问题，但不声称首次提出状态依赖 |
| Transaction sequence generation | PHS 从 property 读取状态反向过滤，并显式保留候选 |
| Static/dynamic data-flow | PHS 使用静态读写和局部值证据，范围较窄 |
| Invocation ordering/branch revisiting | PHS 以 bounded repeat 和 interpretable Top-K 处理受控候选 |
| Sequence-aware mutation | PHS 固定候选顺序，仍将参数探索交给 Echidna |
| Symbolic/LM reasoning | PHS 当前不提供完整求解或语言模型推理 |

本文的差异组合应固定表述为：property-directed preprocessing + external Harness synthesis + interpretable Top-K + semantic boundary audit。本文不是上述方向的替代方法，不对状态依赖、交易序列、重复访问、分支重访或值引导提出绝对首创主张。

## 9. 后续 C4 引用补全任务

1. 为每个 [CITE-*] 槽位确定至少一个可核验的原始论文或官方来源，记录完整 BibTeX 和访问版本。
2. 为每个候选工作建立“原文支持的技术事实—本文对应段落—不应推断的内容”三列表。
3. 检查 Echidna、SMARTIAN、Harvey、ConFuzzius、SmarTest、MuFuzz 和 IR-Fuzz 的名称、拼写、版本与引用对象是否准确。
4. 仅用核验后的事实改写 Related Work，不将未完成的引用补全误写成实验结果。
5. 将 PHS 与各方向的差异绑定到方法边界和 semantic boundary audit，不添加未经验证的性能或优越性叙述。
6. 完成引用后重新运行 style and claim audit，确保新增引用没有带入更宽主张。
