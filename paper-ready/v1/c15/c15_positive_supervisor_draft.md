# 面向显式安全属性的智能合约多交易序列规划

## 摘要

智能合约中的安全属性描述一系列交易后需要避免的持久状态条件。对于包含多个显式 `echidna_` property 的合约，若规划器先把所有 property 的读取变量合并，再统一生成交易序列，属于其他 property 的状态依赖路径就可能进入当前目标的候选池，并占据有限的 Top-K 位置。本文研究一种位于属性模糊测试器之前的 property-directed transaction-sequence planning 与 Harness synthesis 流程。该流程以目标 property 的 read-set 为起点，依次推导 property-specific target functions 和 backward dependency paths，再进行 bounded repetition、lightweight value ranking 和 Top-K 选择，并生成只暴露目标 property 的 Harness proxy。对于 `MultiPropertyInterference` 中预先定义的目标序列 `prepareTarget() -> triggerTarget()`，LEGACY_UNION 使用 3 个 property variables 和 3 个 target functions，生成 8 个候选，其中 7 个与目标 property 无关，irrelevant candidate ratio 为 0.875，目标序列 rank 为 6，Top-1/3/5 均为 false；PER_PROPERTY 使用 1 个 property variable 和 1 个 target function，生成 1 个候选，无关候选为 0，ratio 为 0，目标 rank 为 1，Top-1/3/5 均命中。该结果定位为受控机制证据，适用于解释属性级候选隔离现象；真实合约生态层面的效果需要独立外部有效性研究。已有适配真实来源记录用于说明运行状态和工程边界；其中 `budget_exhausted` 是预算内未观察到反例的 right-censored 状态，`compile_error` 是工程状态。生成的 Harness 与 Original Echidna 多交易执行对应两类执行模型，本文分别报告其调用者、交易边界和回滚语义，以及各自的适用范围。

**关键词：** 智能合约；显式安全属性；多交易序列；属性定向规划；状态依赖；Harness

## 1 引言

智能合约测试围绕交易序列驱动的持久状态演化展开。一个安全属性可能只读取最终状态中的一个余额、标志位或计数器，但达到该状态往往需要先调用准备函数，再调用改变状态或触发边界的函数。参数搜索的有效性建立在正确状态前缀之上。

多 property 合约进一步引入了一个容易被隐藏的规划问题。设 `echidna_balance_safe()` 读取 `balance`，`echidna_owner_safe()` 读取 `owner`。如果规划器把两者的读取变量合并为 `{balance, owner}`，那么写入 `owner` 的函数可能被当作 `balance` 属性的候选前缀。候选路径仍然可能满足一般读写依赖，但它们与当前被评估的 property 没有直接关系。当候选需要经过排序并截断为 Top-K 时，跨 property 路径会占用真正目标路径的位置。

本文把研究问题限定为：能否把显式 property identity 贯穿读取集合、目标函数、依赖路径、重复扩展、值证据排序和 Harness 生成，使每个 property 获得独立的交易序列规划。这个问题聚焦候选构造和 provenance，底层 fuzzing engine 继续承担参数与执行探索。property 未指定时继续保留 legacy union 接口，历史 runner 由此延续原有语义；新实验通过显式 `--property` 进入 per-property 模式。

本文的贡献有三点：

1. **属性级候选隔离。** 对显式目标 property 独立解析 full-name 和 read-set，沿写入目标状态的函数构建 backward dependency paths，并在受控多属性干扰场景中度量无关候选、目标 rank 和 Top-K 命中。
2. **可组合且可追溯的规划流程。** 在 property identity 不丢失的前提下接入 bounded repetition、lightweight value evidence、Top-K 和 property-specific Harness proxy，同时保留无 `--property` 时的 legacy union 行为。
3. **有边界的证据解释。** 将 controlled mechanism evidence、有限适配真实来源证据、`budget_exhausted` 和 `compile_error` 分层报告，并明确 Harness 与 Original 的执行模型差异。

## 2 相关工作

### 2.1 Stateful smart-contract fuzzing

智能合约模糊测试需要同时处理参数、调用顺序和持久状态。Echidna-style property testing 以显式属性描述需要避免的状态条件，底层测试器继续搜索能够使属性失败的输入与交易。本文沿用这种属性接口，将研究对象放在属性模糊测试之前的候选序列规划；底层测试器继续负责输入与交易搜索。相关的智能合约模糊测试工作包括 ContractFuzzer、sFuzz、ILF 和 Echidna 的方法线 [@jiang2018contractfuzzer; @nguyen2020sfuzz; @he2019ilf; @grieco2020echidna]。

Harvey 将有状态合约测试中的调用顺序和状态推进作为重要的搜索对象；ConFuzzius 则代表了数据依赖与混合分析结合的方向 [@wustholz2020harvey; @torres2021confuzzius]。本文与这些方向共享多交易状态测试的背景。本文首先生成与显式 property 绑定的候选路径，并把它们外置为可检查的序列或 Harness；完整搜索过程由各工具自身的执行框架承担。

### 2.2 数据流、状态依赖与序列引导

SMARTIAN 代表静态与动态数据流辅助的智能合约模糊测试方向 [@choi2021smartian]。IR-Fuzz 以及其他中间表示或数据流引导方法属于相邻的输入组织方向。MuFuzz 关注序列感知的变异和 seed 组织，是另一个与多交易测试相关的邻近方向。本文与这些工作共享“利用状态或序列结构减少无关探索”的研究空间。本文的切入点是显式 property read-set 驱动的外部 preprocessing：读集合决定目标函数，目标函数决定依赖候选，候选再进入有界重复和值证据环节。跨工具排名需要同 property oracle、同 caller model、同预算和同结果定义的 executable comparison；本文将这些工作用于概念定位。

### 2.3 约束与学习辅助的交易推理

约束分析、符号执行和学习辅助的交易序列推理提供了与本文不同的搜索路径。SmarTest 可作为此类方向的 conceptual positioning。本文的 value stage 只读取已有的常量写入、简单 requirement 和比较关系，输出 match、conflict、unknown 等轻量证据；其处理范围聚焦轻量值证据，与 SMT solver、symbolic execution、mapping inference 和语言模型交易推理处于不同层次。SmarTest 的正式书目信息和具体方法边界由仓库 citation registry 在定稿前核验；所有新增事实和实验数字均以核验结果为准。

### 2.4 本文的定位

本文的方法位于“显式安全属性”和“交易序列候选规划”交叉处。贡献聚焦 property identity 对多属性候选混杂的控制作用，以及该 identity 向后续 Harness 的传递。相关工作在本文中承担概念定位；跨工具比较需要独立且可复现的 executable protocol。

## 3 问题定义与设计目标

### 3.1 显式属性与交易序列

设合约状态为 `s`，显式安全属性为 `P(s)`。测试器的目标是寻找交易序列 `T = (t_1, ..., t_n)` 及其参数，使执行后的状态满足 `P(s_n) = false`。规划器的职责是根据函数状态读写和 property identity 产生候选序列；属性证明与输入空间的完整穷举属于下游测试任务。

对合约函数 `f`，记 `R(f)` 为读取的状态变量集合，`W(f)` 为写入的状态变量集合。对 property `P_i`，记 `R(P_i)` 为该 property 自身的 read-set。legacy union 模式使用

`R_union = union_i R(P_i)`。

显式 per-property 模式使用

`R_selected = R(P_i)`。

两种模式的差别发生在候选规划过程中，历史结果继续按照原有输入语义解释。`R_union` 保留旧接口的兼容性，`R_selected` 为新实验提供 property-specific provenance。

### 3.2 多属性候选干扰

若两个 property 读取互不相同的终态变量，union 模式会把两个变量都传给 target-function discovery。写入非目标变量的函数因此可能形成合法的依赖边，并在路径排序后进入 Top-K。该现象不一定导致动态执行失败，但会改变候选池的组成和目标路径的 rank。本文用 `MultiPropertyInterference` 隔离这一机制：目标 property、两个 distractor property 以及它们的状态依赖链彼此独立，预先定义的目标序列为 `prepareTarget() -> triggerTarget()`。

### 3.3 设计目标

方法设计遵循三个目标：

- **身份一致。** 从 resolver 到 Harness 的每条路径都保存 `property_function`，后处理与 proxy 生成沿用路径中的 property_function，保持其他 property 的路径隔离。
- **兼容可见。** 无 `--property` 时继续输出 legacy union 语义；显式 property 是新行为入口，不改写历史 runner 的默认接口。
- **证据可分层。** 静态 candidate count、target rank 和 Top-K hit 是规划指标；动态 `falsified`、`budget_exhausted` 和工程 `compile_error` 采用不同状态口径。

## 4 方法

### 4.1 流程概览

给定 Solidity 源代码、读写分析结果和显式 property，流程依次执行：

1. 解析一个明确的 property function；
2. 得到该 property 的 read-set；
3. 发现写入 read-set 的 target functions；
4. 从函数写读关系构建 backward dependency paths；
5. 在 repetition-aware 版本中进行有界重复展开；
6. 用 lightweight value evidence 对已有候选重新排序；
7. 按 Top-K 保留候选，并生成 property-specific Harness proxy。

`analyzer/generate_property_sequences.py` 是基本规划器，`analyzer/generate_repetition_aware_sequences.py` 负责有界重复，`analyzer/generate_value_guided_sequences.py` 负责后处理排序，`analyzer/generate_harness_from_paths.py` 负责把路径和 proxy 写入 Solidity Harness。

### 4.2 Property resolver

三个相关脚本采用一致的 property resolution 语义。若用户请求的名称包含 `(`，例如 `echidna_property_a(uint256)`，resolver 只接受与函数 `full_name` 完全相同的 key；它不会因为 basename 相同而回退到 `echidna_property_a()`。若请求不包含 `(`，例如 `echidna_property_a`，resolver 才允许按 basename 匹配。若 basename 对应多个 overload，解析结果为 ambiguous 并 fail closed。

这一规则同时处理了两个需求：短名称仍能兼容当前仓库中常见的 `echidna_xxx()` full-name 格式；完整签名优先保留参数信息，basename fallback 仅服务于短名称解析。Harness resolver 还检查 property 是否带参数。当前 Harness 的适用范围限定为零参数 property；显式选择带参数 property 时，生成器直接报告参数支持错误。

### 4.3 Selected property read-set 与 target functions

显式模式下，`property_variables` 只能来自选中 property 的 read-set。规划器扫描普通函数的写集合，保留写入这些变量的函数作为 `target_functions`。property function 自身不作为普通交易候选；它只定义目标状态和最终 oracle。

legacy 模式仍对所有 `echidna_` property 的读取变量求 union，并从 union 推导 target functions。这样，legacy runner 可以继续使用旧 schema 和旧候选语义；新实验可以通过 `--property echidna_target_safe` 或完整的 `echidna_target_safe()` 明确选择一个 property。输出在显式模式下记录 `property_function`、`property_variables`、`target_functions` 和 `paths`，每条 path 还记录自己的 `property_function`。

### 4.4 Backward dependency paths

基本 planner 通过函数写集合与后继函数读集合的交集建立 dependency edges。边保存共享变量和用于排序的 score。随后 `build_relevant_paths()` 从 target functions 构建有界路径，保存：

- `sequence`；
- `length`；
- `score`；
- `dependency_variables`；
- `target_function`；
- `property_function`。

基本 property planner 的路径搜索对函数重复和最大长度有明确边界；静态 path 表示候选结构，运行时可达性还取决于参数、调用者、资金、环境和 revert 行为。一个候选包含某个写读边，只表示它满足规划器定义的局部依赖关系，实际是否能执行仍取决于参数、调用者、资金、环境和 revert 行为。

### 4.5 Bounded repetition

repetition-aware planner 在选中 property 的 `property_variables` 和 `target_functions` 上展开重复候选。`--max-function-visits` 限制单个函数在路径中的访问次数，`--max-expansions` 限制搜索展开量；既有 score、length 和 sequence 排序仍保留。重复路径只有在当前 property 的目标依赖中出现时才有资格进入该 property 的候选池，因此 Property A 的重复需求不会把 Property B 的候选污染为 A 的路径。

bounded repetition 解决的是候选表达能力问题。例如，某个目标需要 `stepX() -> stepX()` 才能累积状态，bounded repetition 可以在预设上限内表示该序列。它不保证每条重复序列都可执行，也不直接给出漏洞发现率。

### 4.6 Lightweight value evidence

value-guided 脚本是路径后处理器。它首先深拷贝输入 path，再对相邻函数边检查已有的 constant writes 与 requirements。当前支持的比较符号是 `==`、`!=`、`>`、`>=`、`<` 和 `<=`；判断结果被分类为 match、conflict、unknown 或 unrelated。

输出保留并补充：

- `property_function`；
- `property_score`；
- `value_score`；
- `value_matches`；
- `value_conflicts`；
- `value_unknowns`；
- `value_edges`；
- `value_rank`。

如果写入是符号值、条件无法静态判断或变量来自复杂表达式，结果保持 unknown，以保留证据的不确定性。value stage 当前覆盖常量写入、简单 requirement 和比较关系；SMT、symbolic execution、mapping inference、跨合约推理和复杂算术推理属于扩展能力。不同 property 的 path list 保持独立，排序阶段只更新已有候选的优先级。

### 4.7 Top-K

Top-K 是候选截断配置，用于控制有限预算下的候选规模。`K=1` 只保留最高排序候选，较大的 K 保留更多备选路径。为了统计完整 candidate count，`results/per-property-isolation/summary.json` 使用 `top_k=1000`，实际保留数量为 8 和 1，均未因截断丢失候选。论文中的 target rank 是 expected sequence 在排序候选列表中的位置；Top-1/3/5 hit 是该 rank 是否不超过对应 K。

### 4.8 Property-specific Harness proxy

legacy Harness 执行模型收集合约中全部零参数 `echidna_` property 并生成 proxy。显式模式只选择 resolver 确认的 property，只加载 contract-level 和 path-level `property_function` 与 CLI 请求相匹配的路径，并只生成一个目标 proxy。若 sequence JSON 缺少 property provenance、contract-level property 与 path-level property 不一致、CLI property 与 JSON 不一致或 property 不存在，生成器 fail closed。若 property 有参数，当前 Harness 明确报错，不静默回退到其他 property。

生成的 Harness 会在目标合约引用旁加入简短的 `Target property: ...` 注释，便于检查生成物。该注释和 proxy 选择用于 provenance，底层执行语义保持原有定义。

### 4.9 Execution-model boundary

Original Echidna 多交易模式和生成 Harness 采用不同的执行模型。原生模式中的目标调用可能分别拥有 sender、`msg.value`、区块环境和交易回滚边界；Harness 执行模型通常由 wrapper 发起连续目标调用，调用者可能固定为 Harness 地址，某一步失败还可能影响整个 wrapper 的状态提交。Harness 是候选路径的可执行封装，对应独立的 Harness 执行模型；原生多交易语义依据 Original 的交易边界单独报告。

这一区分还影响指标解释。Harness 的 sequence function、调用次数和 wall time 适合在相同 candidate、property、预算和执行模型内作描述性比较。原生多交易语义检查与漏洞可达性分别依据 Original 执行记录和动态属性结果复核。

## 5 实验问题与协议

### 5.1 Research questions

本文将实验收敛为三个问题：

- **RQ1：** 显式 per-property planning 是否减少多属性合约中的无关候选，并改善预先定义目标序列的 rank 和 Top-K 命中？
- **RQ2：** dependency、bounded repetition、lightweight value evidence 和 Top-K 是否按设计影响候选构造与排序？
- **RQ3：** 在有限的适配真实来源池上，运行状态、适配限制和执行模型边界是什么？

RQ1 的主要证据是 `results/per-property-isolation/summary.json`；RQ2 使用已有 formal/controlled package；RQ3 使用已有适配真实来源记录。三个问题不合并为一个生态级发现率问题。

### 5.2 Evidence layers

实验结果分为四层：

1. **Controlled mechanism evidence。** 六个预先设计的受控场景用于隔离 property filtering、value direction、bounded repetition、multi-path 和多属性等障碍。
2. **Per-property isolation evidence。** `MultiPropertyInterference.sol` 只用于比较 LEGACY_UNION 与 PER_PROPERTY 的候选组成和目标 rank。
3. **Public/适配真实来源证据。** 四个 candidate、120 条预注册运行用于描述适配任务上的状态分布和可执行性边界。
4. **Engineering status evidence。** `compile_error` 单独记录为构建、导入或 Harness 适配状态，并在运行状态统计中独立列示。`budget_exhausted` 单独保留为 right-censored observation。

受控候选指标、动态属性违反和工程运行状态分别回答候选规划、动态观察和工程适配问题。

### 5.3 RQ1：per-property isolation

实验对象是 `contracts/benchmarks/MultiPropertyInterference.sol`。它包含 `echidna_target_safe()`、`echidna_distractor_a_safe()` 和 `echidna_distractor_b_safe()` 三个互相独立的 property。目标序列在实验前固定为 `prepareTarget() -> triggerTarget()`；planner 配置为 `max_length=6`、`top_k=1000`，路径构造器为 `build_relevant_paths`。

**表 1 受控多属性隔离结果**

| 指标 | LEGACY_UNION | PER_PROPERTY |
|---|---:|---:|
| property variables | 3 | 1 |
| target functions | 3 | 1 |
| candidate sequences | 8 | 1 |
| related candidates | 1 | 1 |
| irrelevant candidates | 7 | 0 |
| irrelevant candidate ratio | 0.875 | 0 |
| expected target rank | 6 | 1 |
| Top-1 hit | false | true |
| Top-3 hit | false | true |
| Top-5 hit | false | true |
| configured top_k | 1000 | 1000 |
| retained candidates | 8 | 1 |

LEGACY_UNION 的 7 条无关候选来自 distractor property 相关链，说明 union read-set 会把与 P_TARGET 无关的路径带入候选池。PER_PROPERTY 只保留 `targetValue` 和 `triggerTarget()`，目标序列成为唯一候选。该结果直接支持“属性级规划减少跨 property 候选干扰”这一受控机制结论，证据层级集中在 candidate isolation、rank 和 Top-K。Echidna 搜索时间、漏洞发现率和真实合约总体性能属于独立评价维度。

### 5.4 RQ2：组件行为

已有六个 controlled scenarios 用于分离不同路径障碍。它们覆盖无关状态路径、状态值方向、重复调用、多路径和多属性等机制问题。主配置中 Full-K1 观察到 180/180 次属性违反，Original 观察到 171/180 次。该结果说明，在预先设计的受控障碍和声明配置下，组合规划器能够为动态搜索提供有效触发前缀；它不等于对所有合约的检测率结论。

组件解释来自两个层面。首先，property stage 通过 read-set 过滤目标相关路径；RQ1 的独立表格量化了这一点。其次，repeat stage 保留 `stepX() -> stepX()` 这类有界重复，value stage 对已有写入和 requirement 计算 match/conflict/unknown，Top-K 决定这些候选中哪些被保留。代码输出的 `property_score`、`value_score`、`value_edges` 和 `value_rank` 提供了候选排序 provenance。当前证据覆盖组件对候选构造和排序的静态影响；因此 RQ2 聚焦组件按设计发挥作用，动态发现能力依据下游运行结果单独评价。

### 5.5 RQ3：有限适配真实来源池

已有适配真实来源证据包含 4 个 candidate 和 120 条预注册运行。记录分为 80 条 usable/descriptive records 与 40 条 `compile_error` engineering rows，其中 observed statuses 为 79 条 `falsified`、1 条 `budget_exhausted` 和 40 条 `compile_error`。

两个 Echidna-origin candidates 构成有限的 non-compile-error comparable subset：Original 为 20/20 条属性违反，Full-K1 为 20/20 条，Full-K5 为 19/20 条，另有 1 条 right-censored。该子集支持的表述是：在两个 adapted Echidna-origin candidates 上，Full-K1 和 Full-K5 仍观察到属性违反。由于 candidate 数量少、适配改变了部分工程条件，且 Harness 与 Original 的 caller/transaction model 不同，这些数字适用于描述有限适配任务上的运行状态；方法排序和生态级性能需要独立、同口径的评估协议。

SmartBugs Original-only subset 的 20 条记录用于说明适配目标在 Original 执行模式下可以运行并观察属性违反。SmartBugs Harness 的 40 条记录为 `compile_error`，其含义是 Solidity 0.4.25 下 Harness 生成、依赖导入或编译链存在工程限制。该状态与动态 detection outcome 分开报告，并在运行状态统计中单独列示。

### 5.6 结果口径

- `falsified`：在声明的 execution model、预算和配置内观测到属性违反。
- `budget_exhausted`：在预算内没有观测到属性违反，记录为 right-censored observation；本文将其作为预算内未观察到反例的运行状态。
- `compile_error`：构建、导入或编译环节未完成，归类为 engineering status，并从动态检测结果统计中独立呈现。
- candidate count、irrelevant ratio、target rank 和 Top-K hit：规划层指标，刻画候选构造与排序；动态漏洞发现通过运行状态单独报告。
- Total calls、sequence length 和时间：只作同执行模型、同 candidate、同 property 条件下的描述性轨迹信息，不直接推出加速结论。

## 6 讨论

### 6.1 属性 identity 是候选规划的控制变量

多 property 合约中的关键问题聚焦不同 property 的状态依赖是否在规划过程中被混合。`MultiPropertyInterference` 的结果显示，union 模式把 3 个变量和 3 个 target functions 交给同一候选生成过程，目标序列排在第 6 位；显式模式只处理目标变量和目标函数，目标序列排在第 1 位。由此，property identity 不只是输出字段，它决定了候选图的节点、边和 Top-K 内容。

该结论也解释了为什么 legacy union 行为仍需保留。旧 runner 可能依赖 union schema；保留该接口能够区分历史实验的输入语义与新实验入口。显式 `--property` 因而是版本边界清晰的新增入口，并与旧结果保持输入语义区分。

### 6.2 规划层指标与动态检测结果

candidate count、irrelevant ratio 和 target rank 衡量规划器向动态测试器提供了什么；它们不测量参数空间中的真实可达性。Top-1 命中表示 expected sequence 位于前 1 个候选，用于刻画规划排序位置；Echidna 在给定预算中的反例观察通过动态运行结果单独统计。类似地，value match 说明一个静态写入与 requirement 在支持的轻量表示下相容，复杂算术、mapping 和外部调用后的条件需要额外语义复核。

这种分层使 RQ1 和 RQ2 可以在不扩大结论的情况下回答：RQ1 关注候选污染，RQ2 关注组件实现。动态 falsification 和 适配真实来源池状态则放在 RQ3 中，以保持证据类型的区别。

### 6.3 Original 与 Harness 的解释边界

Harness 适合把候选序列变成可检查的 Solidity 生成物，并让测试器继续探索参数；它也让 property proxy、sequence function 和编译状态可以被记录。然而 wrapper 的调用者、交易原子性、回滚范围、`msg.value`、block context 和 external-call behavior 可能与 Original 不同。因此，本研究把 Harness 视为一个明确的 execution model，并与 Original 的原生多交易语义分别报告。

这一区分直接影响 适配真实来源结果：两个 Echidna-origin candidates 的有限可比子集可以说明不同配置下仍观察到属性违反，20/20、19/20 适用于两个 Echidna-origin candidates 的有限可比子集；跨模型相对性能排序需要同 caller、transaction model 和 outcome definition 的专门协议。SmartBugs Harness 编译限制用于刻画工程链边界。

## 7 有效性威胁

### 7.1 Controlled benchmark 的外部有效性

受控 benchmark 的状态变量、属性和依赖链是为单一机制障碍设计的。它们能够隔离候选污染、重复需求或值方向，适合解释机制在指定障碍上的作用。真实合约的函数数量、依赖复杂度、调用者分布、编译器版本和资产交互需要独立外部有效性研究；controlled 结果在本文中承担机制解释。

### 7.2 Harness 与 Original 的语义差异

Original 和 Harness 在 caller、transaction boundary、atomicity、rollback scope、`msg.value`、block context、external call 和 reentrancy boundary 上可能不同。Harness proxy 的生成和编译用于确认生成物通过相应工程步骤；两个执行模型的搜索空间和反例含义依据各自运行记录与语义审计分别解释。论文中的结果表必须标注 execution model。

### 7.3 Right-censored budget 状态

`budget_exhausted` 表示给定 budget、seed 和配置内未观察到反例，属于删失记录；统计口径将其与属性违反和工程状态分开列示。当前适配真实来源池中的 1 条记录在状态表和讨论中保留。

### 7.4 `compile_error` 的工程含义

`compile_error` 发生在构建、导入或编译链上，反映工具链或 source adaptation 的工程状态。40 条 SmartBugs Harness compile rows 作为 engineering status 单独保存，与 79 条 falsified 和 1 条 right-censored 分列统计。

### 7.5 跨工具比较的公平性

SMARTIAN、ConFuzzius、Harvey、MuFuzz、IR-Fuzz 或 SmarTest 的跨工具比较需要同 property oracle、caller model、transaction budget、seed 和 outcome definition 的完整 executable protocol。SMARTIAN 的仓库材料覆盖两个简单整数目标；在本文中，相关工作承担 conceptual positioning，跨工具排名需要独立协议。

### 7.6 小规模 适配真实来源池

4 个适配真实来源候选主要用于检查运行状态和适配边界。它们的来源、编译器版本、属性接口和 Harness 条件构成有限适配样本；真实生态多样性需要更多独立 source 和统一协议。RQ3 的结论定位为有限 pool 上的 descriptive evidence。

### 7.7 规划指标的构念边界

静态 candidate count、rank、Top-K hit 和 value evidence 属于规划层证据，完整动态可达性、检测率和安全性依据运行结果与语义审计评价。当前规划器覆盖轻量值证据；SMT、symbolic execution、mapping inference、跨合约推理和复杂算术属于扩展能力。复杂外部状态和调用者交互需要额外语义复核。

## 8 结论

本文研究了显式安全属性下的多交易候选污染问题，并实现了从 property resolver、selected read-set、target-function discovery、backward dependency paths 到 bounded repetition、lightweight value ranking、Top-K 和 property-specific Harness proxy 的连续规划流程。其关键设计是让 property identity 参与候选生成，并据此形成 property-specific 的候选排序。

在预先定义的 `MultiPropertyInterference` 场景中，LEGACY_UNION 产生 8 个候选且 7 个与目标 property 无关，目标序列 rank 为 6；PER_PROPERTY 只产生 1 个目标相关候选，rank 为 1。该结果支持属性级规划减少多属性候选干扰这一机制结论。既有六场景 controlled package 和有限适配真实来源记录进一步展示组件行为、运行状态和工程边界，结论范围保持在相应证据层级。

本文的主要价值在于可追溯的 property-specific candidate planning 与明确的 execution-model accounting。后续若要扩展外部有效性，需要新的、预注册且语义可比的研究问题；这不属于本稿当前证据已经回答的范围。

## 9 适用范围与解释口径

本文的结论范围由证据类型、运行状态和执行模型共同界定。

- MultiPropertyInterference 是预先设计的 controlled mechanism benchmark，适用于解释属性级候选隔离现象；真实合约生态层面的效果需要独立外部有效性研究。
- property variables、target functions、candidate count、target rank 和 Top-K hit 组成规划层指标，刻画候选构造与排序；动态属性结果和工程状态分别依据运行记录呈现。
- budget_exhausted 表示在给定预算、seed 和配置内未观察到反例，本文将其作为 right-censored observation 单独记录。
- compile_error 表示构建、导入或编译链的工程适配状态，在运行状态统计中独立列示。
- Original Echidna 多交易与 Harness 执行模型分别包含各自的 caller、transaction boundary、atomicity、rollback scope、msg.value、block context、external call 和 reentrancy boundary；本文按两类模型的适用范围分别解释结果。
- SMARTIAN、ConFuzzius、Harvey、MuFuzz、IR-Fuzz 和 SmarTest 在本文中承担概念定位；跨工具性能结论需要同 property oracle、caller model、预算和结果定义的独立 executable protocol。
- lightweight value evidence 覆盖常量写入、简单 requirement 和比较关系；SMT、symbolic execution、mapping inference、跨合约推理和复杂算术属于扩展能力。
- 适配真实来源池用于描述运行状态和工程边界，候选数量与适配条件构成有限 descriptive evidence。

## 参考文献与核验说明

正文沿用仓库中已登记的 cite key，包括 Harvey、SMARTIAN、ConFuzzius、Echidna、ContractFuzzer、sFuzz、ILF 和 QuickCheck。MuFuzz 在本文中作为邻近方向出现，正式出版元数据仍需在定稿前复核；IR-Fuzz 与 SmarTest 只承担概念定位，正式引用 key 和具体方法描述也需依据 citation registry 完成核验。此处不引入新的作者、年份、venue 或实验数字。
