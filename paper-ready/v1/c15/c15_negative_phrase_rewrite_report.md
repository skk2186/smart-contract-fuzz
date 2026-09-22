# C15 否定句式替换报告

本报告记录正文边界句式的正向化处理；改写保留事实、数字、适用范围和 claim 层级。

| 原句 | 问题类型 | 修改后句子 | 是否改变 claim | 证据来源 |
|---|---|---|---|---|
| 但不代表真实合约生态的整体性能 | 外推边界 | 该结果定位为受控机制证据，真实合约生态层面的效果需要独立外部有效性研究。 | no | results/per-property-isolation/summary.json；C11 claim evidence matrix |
| 不能按同一执行模型解释 | 执行模型 | Harness 与 Original 对应两类执行模型，本文分别报告各自的适用范围和解释口径。 | no | paper-ready/00_PROJECT_SUMMARY.md；C11 research contract |
| 测试面对的不是一次函数调用 | 动机表达 | 智能合约测试围绕交易序列驱动的持久状态演化展开。 | no | C14 supervisor draft |
| 不是重新实现一个独立的通用 fuzzing engine | 范围表达 | 底层 fuzzing engine 继续承担参数与执行探索，本文聚焦候选构造和 provenance。 | no | C11 research contract |
| 不等同于 SMT solver、symbolic execution、mapping inference | 能力边界 | 轻量值证据与这些复杂推理机制处于不同处理层次。 | no | C11 claim evidence matrix |
| 不声称首次提出状态依赖等能力 | 创新表述 | 贡献聚焦 property identity 对多属性候选混杂的控制及其向 Harness 的传递。 | no | C11 research contract |
| 不能在后处理时混入其他 property | provenance | 后处理与 proxy 生成沿用路径中的 property_function，保持 property 路径隔离。 | no | analyzer/generate_value_guided_sequences.py |
| 静态 path 不是运行时可达性证明 | 指标边界 | 静态 path 表示候选结构，运行时可达性还取决于参数、调用者、资金、环境和 revert 行为。 | no | C11 claim evidence matrix |
| 不能作为 detection failure | 状态分类 | compile_error 归类为 engineering status，并在运行状态统计中独立呈现。 | no | C11 claim evidence matrix |
| 不能互相替代 | 证据层级 | 候选指标、动态属性违反和工程状态分别回答规划、运行观察和适配问题。 | no | C11 claim evidence matrix |
| 不能写成 property safe 或 pass | budget 状态 | budget_exhausted 记录为预算内未观察到反例的 right-censored observation。 | no | summary.json；FREEZE_STATUS.md |
| 不支持方法排序 | adapted pool | 有限适配任务数字用于描述运行状态；方法排序需要同口径协议。 | no | C11 experiment freeze decision |
| 不能代表真实合约多样性 | controlled 外部有效性 | 受控合约用于解释指定障碍；真实合约多样性需要独立外部有效性研究。 | no | paper-ready/00_PROJECT_SUMMARY.md |
| 不应进入属性通过分母 | 统计口径 | right-censored observation 与属性违反和工程状态分开列示。 | no | C11 claim evidence matrix |
| 不能升级为公平 baseline | 跨工具边界 | 跨工具性能结论需要同 oracle、caller、budget、seed 和 outcome definition 的独立协议。 | no | C11 research contract |
| 不建议继续实验 | 决策语气 | 当前证据适合进入导师审阅；新增实验仅在核心 claim 出现证据缺口时重新评估。 | no | C13 next decision；C14 patch notes |

## 检查范围

已检查：但不代表、不能作为、不等同、不能、不是、不支持、不应、不主张、不负责、不进入、不替代、不推出、不改变、不修改、不新增、不建议。审计文件保留这些原始词组用于记录替换依据；C15 正文采用正向的适用范围和证据分类表述。
