# 实验设置与结果

## 研究目标与实验分工

本文研究面向显式安全属性的交易序列生成问题。方法首先根据安全属性读取的状态变量筛选状态依赖路径，再结合 require 条件、状态值写入方向和有界重复访问对候选路径进行约束与排序，最后将排名靠前的路径生成到可审计的 Harness 中。实验中的 Original 表示原始交易序列执行方式，Full-K1 和 Full-K5 分别表示使用前 1 条和前 5 条候选路径的完整方法配置。

实验由两类证据组成。第一类是 controlled evidence，用于在受控障碍下检验属性相关筛选、值约束匹配和有界重复等机制。第二类是 adapted real-source evidence，用于考察这些机制在少量经过编译器与属性接口适配的真实来源任务上的适用边界。两类证据使用不同的研究目的和分母，不合并为单一总体结果。

## 数据集与任务来源

受控实验由六个针对特定路径障碍设计的合约场景组成，分别覆盖无关状态路径、状态值方向、重复调用、多路径和多属性等问题。每个配置使用 30 个随机种子。该部分的结果用于回答方法机制是否能够在明确障碍下生成有效触发序列，而不是用来近似真实生态中的合约分布。

补充实验选取四个预先登记的 adapted real-source candidates，来源包括 Echidna-origin targets 和 SmartBugs targets。对每个候选分别运行 Original、Full-K1 和 Full-K5，每个 candidate-method 单元使用 10 个种子，共 120 条预注册运行。所有运行沿用声明的预算设置，即 testLimit=100000、timeout=30 秒、单 worker 且 stopOnFail=false。真实来源任务的纳入、属性接口和编译器适配均应与对应的来源说明一并披露。

## 受控证据与真实来源证据的关系

受控结果承担主要机制论证，因为每个场景针对一个可解释障碍设计，能够将观察到的变化与相应方法组件联系起来。适配真实来源结果承担外部有效性补充作用，关注的是方法能否在不同来源任务上运行并观测到属性违反，而不是重新估计受控实验中的机制效应。因而，真实来源结果不应被表述为大规模真实合约扫描，也不应与受控场景的发现率直接合并。

## 适配真实来源结果

在四个 adapted real-source candidates 上，共保留 120/120 条结果记录，其中 79 条为 falsified，1 条为 budget_exhausted，40 条为 compile_error。80 条记录可用于论文中的描述性分析或子集说明。两个 Echidna-origin candidates 共包含 60 条记录，Original、Full-K1 和 Full-K5 均有可解析的非 compile_error 结果。其中 Original 观察到 20/20 条属性违反，Full-K1 观察到 20/20 条属性违反，Full-K5 观察到 19/20 条属性违反，另有 1 条记录为 right-censored。该结果支持如下较窄的表述：在这两个 adapted real-source candidates 上，Full-K1 和 Full-K5 保持了观测属性违反的能力。

SmartBugs 的 Original-only 子集包含 20 条 falsified 记录，可用于说明这些 adapted targets 能够运行并观测到属性违反。对应的 SmartBugs Full-K1 和 Full-K5 共 40 条 compile_error 记录，反映 Solidity 0.4.25 下 Harness 生成或导入路径的工程限制。这些记录不参与 Original 与 Harness 的比较，也不被解释为检测失败、失败发现率或性能结果。

对于 falsified 记录，calls-to-failure 和 sequence-length 可作为发现轨迹复杂度的描述性指标。由于 Original 与 Harness 的调用者、交易原子性和回滚边界可能不同，且每次外层调用包含的目标函数调用数不同，因此不能将 Total calls 直接转换为 speedup。budget_exhausted 仅表示在声明预算内未观测到反例，属于 right-censored 观察，不能解释为属性通过或合约安全。

## 表格引用与结果解释

表 X 汇总受控场景中的机制结果，表 Y 汇总四个 adapted real-source candidates 的状态分布和 candidate-method 矩阵，表 Z 单独列出 usable rows 与 excluded engineering rows。真实来源矩阵的比较性结论只引用两个 Echidna-origin candidates。SmartBugs Original-only 结果放在补充描述中，40 条 Harness compile_error 作为工程局限和 Threats to Validity 的证据保留。

综上，实验结果表明，所提出的属性定向路径生成方法在受控场景中能够针对预设障碍生成有效触发序列，并且在两个 Echidna-origin adapted real-source candidates 上保持可观测的属性违反能力。后一个结论是适用性补充，而不是对所有真实合约、所有编译器版本或整个合约生态的性能优越性结论。
