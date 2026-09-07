# Related Work 修订计划

## 使用原则

本计划把 C3 的定位框架细化为可执行的引用补全任务。当前仓库没有发现本地 .bib 或其他已核验的 references 文件，也没有进行联网检索。因此，文中只能先使用 citation slot；references_todo.bib 只是占位文件，不能直接作为终稿参考文献表。后续必须从原始论文、官方文档或正式 benchmark/artifact 仓库逐条核验题名、作者、年份、发表 venue、DOI、版本与稳定链接。

Related Work 的中心定位是：PHS 是 property-directed preprocessing、external Harness synthesis、interpretable Top-K 和 semantic boundary audit 的组合式方法。它不是对现有智能合约模糊测试器、符号分析器或学习式序列生成器的替代品。

## 1. Echidna 与 property-based smart-contract fuzzing

- 待补引用：CIT-001、CIT-002；占位键 TODO_ECHIDNA。
- 与 PHS 的关系：Echidna 是 PHS 假定的下游执行平台。PHS 负责从 safety property 出发整理候选交易序列并生成 wrapper Harness，Echidna 仍负责参数模糊与属性执行。
- 可以写：Echidna 提供 property-based smart-contract fuzzing 的执行语境；本文把 PHS 放在 fuzzer core 之前。
- 禁止写：PHS 替代 Echidna；PHS 是新的完整模糊测试器；PHS 已经在工具级别击败 Echidna。
- 人工核验：Echidna 官方文档和原始论文的正式引用方式；本文对 property、assertion、constructor、调用者和执行模型的描述是否与版本一致。
- 段落组织：先介绍 property-based fuzzing，再说明本文的输入输出边界，最后明确 PHS 与 Echidna 的组合关系。

## 2. Stateful smart-contract fuzzing

- 待补引用：CIT-003、CIT-026；候选工作包括 Harvey、ConFuzzius，以及需要核验的综述或原始工作。
- 与 PHS 的关系：已有 stateful fuzzing 工作为状态依赖和多交易执行提供背景；PHS 不声称首次提出这些概念，而是把 property 相关状态信号用于外部候选 Harness 预处理。
- 可以写：状态依赖使得单笔调用不足以表达部分属性触发条件，已有研究从不同层面处理状态推进。
- 禁止写：本文首次提出状态依赖；本文首次提出状态机或交易序列；所有 stateful fuzzing 都使用同一种调用模型。
- 人工核验：Harvey、ConFuzzius 的正式题名与原始来源；各工作是否可准确支持 stateful、multi-transaction、data-flow 这些词。
- 段落组织：以“状态是执行语境的一部分”为共同问题，再按反馈引导、数据流引导和符号/学习辅助方法区分，不做未经设计的排名。

## 3. Transaction sequence generation

- 待补引用：CIT-004、CIT-007、CIT-017；候选工作包括 Harvey、ConFuzzius、EthPloit。
- 与 PHS 的关系：PHS 只构造和排序候选 transaction sequence，并将其编译进外部 Solidity wrapper Harness；它不宣称发明交易序列生成。
- 可以写：交易序列生成需要同时处理调用顺序、状态推进和输入参数；PHS 关注 property-directed 的候选缩减。
- 禁止写：PHS 是第一个交易序列生成方法；Top-K 序列就是最优序列；K1/K5 等价于 Original 中的交易长度。
- 人工核验：候选工作实际生成的是调用序列、输入、状态迁移还是测试计划；是否适合与 Harness synthesis 做接口层面的比较。
- 段落组织：先定义 transaction sequence，再说明本文只对候选结构做预处理，最后引出与 Original multi-transaction model 的区别。

## 4. Static/dynamic data-flow guidance

- 待补引用：CIT-005、CIT-006、CIT-026；候选工作包括 SMARTIAN、IR-Fuzz。
- 与 PHS 的关系：PHS 使用轻量、可解释的属性相关状态和写读关系作为预处理线索；它与静态/动态数据流引导相邻，但不声称实现了对方完整的分析机制。
- 可以写：数据流信息可以帮助筛选潜在相关调用；PHS 将这种筛选限定在显式 property 相关的候选规划中。
- 禁止写：PHS 包含 SMARTIAN 或 IR-Fuzz 的全部能力；PHS 已经与它们完成公平工具级比较；数据流筛选必然提高漏洞检测率。
- 人工核验：各原始工作对静态、动态和中间表示信息的精确定义；哪些比较点是方法接口相同、哪些需要重新实现。
- 段落组织：描述共同的“减少无关探索”动机，再强调 PHS 的输出是外部 Harness 和可解释排序，而非完整 fuzzer 替换。

## 5. Invocation ordering 与 branch revisiting

- 待补引用：CIT-007、CIT-008；优先核验 Harvey 及其他确实讨论调用顺序或分支重访的原始工作。
- 与 PHS 的关系：PHS 的 backward filtering 和 Top-K ranking 体现对调用顺序的显式规划；它不声称首次处理 branch revisiting。
- 可以写：目标属性可能需要先执行状态准备调用，调用顺序会影响可达性；相关研究从反馈、分支或状态角度处理探索。
- 禁止写：PHS 保证找到所有分支；Top-K 保证全局最优顺序；本文首次提出分支重访。
- 人工核验：原文是否使用 invocation ordering、branch revisiting 或等价术语；避免把不同工作中的局部技术合并成一个未经证实的共同机制。
- 段落组织：把顺序规划作为问题维度说明，再将 PHS 的静态候选排序与动态反馈式策略区分开。

## 6. Sequence-aware mutation

- 待补引用：CIT-009、CIT-027；候选工作包括 MuFuzz、Harvey。
- 与 PHS 的关系：sequence-aware mutation 多在 fuzzer 执行或变异循环内工作；PHS 是 fuzzer 外部的预处理层，固定候选 Harness 条目顺序但保留 Echidna 对参数的 fuzz。
- 可以写：序列级变异和 property-directed Harness planning 可以互补，前者可继续探索，后者可提供可解释的候选起点。
- 禁止写：PHS 已经取代序列变异；Full-K5 是五步序列的等价实现；PHS 在所有序列任务上优于 MuFuzz。
- 人工核验：MuFuzz 的正式引用和其序列变异接口；比较时需说明 caller、rollback、atomicity 等语义是否一致。
- 段落组织：先区分“执行期变异”和“执行前规划”，再说明二者可在未来实验中组合。

## 7. Symbolic-execution-assisted smart-contract analysis

- 待补引用：CIT-010、CIT-011、CIT-012；候选工作包括 SmarTest、Mythril、Oyente。
- 与 PHS 的关系：符号执行和约束分析能够提供更强的路径或输入推理；PHS 目前只使用 lightweight value evidence，不把自身描述为完整符号求解器。
- 可以写：符号执行辅助方法与 PHS 在“利用约束缩小搜索”这一动机上相关，但抽象层次、输出和执行集成方式不同。
- 禁止写：PHS 具有完整符号执行能力；轻量值证据等同精确约束求解；PHS 已经优于 Mythril/Oyente/SmarTest。
- 人工核验：候选工作正式题名、版本、输入输出和可引用来源；SmarTest 的语言模型与符号执行关系是否应分在同一段。
- 段落组织：先放符号/约束方法，再说明 PHS 的轻量化与可解释性取舍，最后指出二者可互补。

## 8. Language-model-assisted transaction reasoning

- 待补引用：CIT-013、CIT-014；候选工作包括 SmarTest、ILF。
- 与 PHS 的关系：语言模型或学习式方法可能参与输入、序列或路径推理；PHS 使用显式规则和可解释排名，不依赖语言模型作为论文方法前提。
- 可以写：学习式 transaction reasoning 是可能的相关方向，本文暂不与其进行结果比较。
- 禁止写：PHS 等同语言模型推理；PHS 已经代表智能化交易生成；未经核验的工作细节、训练数据或效果数字。
- 人工核验：ILF、SmarTest 的正式引用及 language-model-assisted 是否准确；不得把普通机器学习引导和语言模型辅助混称。
- 段落组织：单独说明学习式路径与规则式预处理的接口差异，避免把“智能”作为未经定义的性能主张。

## 9. Smart-contract benchmark 与 dataset

- 待补引用：CIT-018、CIT-019、CIT-020、CIT-023；候选工作包括 SmartBugs、SmartBugs Curated、Daedaluzz。
- 与 PHS 的关系：benchmark 工作支持数据来源和评估边界的说明；本文只报告 registry 中四个 supported public tasks，exercise2-access-control 单列为 conditional。
- 可以写：公开基准的版本、任务定义和纳入规则需要显式记录；受控 benchmark 与公开任务承担不同的证据角色。
- 禁止写：四个任务代表真实生态；SmartBugs 全部任务都已评估；conditional task 可以无条件并入 pooled 结果。
- 人工核验：实际使用任务与仓库版本、许可证、原始来源、属性定义、caller 语义；Daedaluzz 是否应作为 benchmark 生成工作而非数据集工作引用。
- 段落组织：先介绍 benchmark provenance，再区分 controlled mechanism benchmarks、supported public tasks 和 conditional task。

## 10. Reproducibility 与 artifact evaluation

- 待补引用：CIT-021、CIT-022、CIT-028；优先选择目标投稿 venue 的 artifact/reproducibility 指南和实际工具仓库。
- 与 PHS 的关系：provenance、manifest、command、environment、raw、parsed、summary、status 与 checksum 用于审计描述性结果，不能转化为安全性或优越性结论。
- 可以写：完整证据链使已报告范围内的运行记录可追溯；checksum 用于完整性检查。
- 禁止写：artifact complete 等于独立复现；checksum pass 等于 property passed；零解析错误消除了所有内部有效性威胁。
- 人工核验：选用哪一份正式指南；仓库归档、版本和复现实验入口是否稳定；是否需要单独引用数据和代码 artifact。
- 段落组织：在 Related Work 末段或 Evaluation protocol 前简短说明，并在正文中链接 Table 3、Appendix A1--A3。

## 11. 后续人工核验清单

1. 为每个 citation_slots.tsv 条目找到原始论文、官方文档或正式仓库。
2. 逐条填写作者、题名、年份、venue、DOI/URL 和版本；禁止从搜索摘要直接复制未经确认的字段。
3. 用核验后的 BibTeX 替换 references_todo.bib，保留 key 与正文 citation slot 的映射记录。
4. 检查每个引用是否真的支持对应句子，而不是只因为工作名称相近。
5. 特别核验 Harvey、SMARTIAN、ConFuzzius、SmarTest、MuFuzz、IR-Fuzz 的方法边界。
6. 确认 SmartBugs、SmartBugs Curated、Daedaluzz 的数据集或 benchmark 角色，不将任务来源与本文结果混为一谈。
7. 在 C5 中把 slot 标记转换为正式引用格式，并复查“不首次提出”和“不广泛优于”的边界句。
8. 只有完成上述人工核验后，才把占位 BibTeX 作为正式参考文献表的候选来源。
