# 面向显式安全属性的智能合约多交易序列规划

## 摘要

智能合约中的安全属性通常描述持久状态在一系列交易后不应出现的条件。对于包含多个显式 `echidna_` property 的合约，若规划器先把所有 property 的读取变量合并，再统一生成交易序列，属于其他 property 的状态依赖路径就可能进入当前目标的候选池，并占据有限的 Top-K 位置。本文研究一种位于属性模糊测试器之前的 property-directed transaction-sequence planning 与 Harness synthesis 流程。该流程以目标 property 的 read-set 为起点，依次推导 property-specific target functions 和 backward dependency paths，再进行 bounded repetition、lightweight value ranking 和 Top-K 选择，并生成只暴露目标 property 的 Harness proxy。对于 `MultiPropertyInterference` 中预先定义的目标序列 `prepareTarget() -> triggerTarget()`，LEGACY_UNION 使用 3 个 property variables 和 3 个 target functions，生成 8 个候选，其中 7 个与目标 property 无关，irrelevant candidate ratio 为 0.875，目标序列 rank 为 6，Top-1/3/5 均未命中；PER_PROPERTY 使用 1 个 property variable 和 1 个 target function，生成 1 个候选，无关候选为 0，ratio 为 0，目标 rank 为 1，Top-1/3/5 均命中。该结果是 controlled mechanism evidence，支持属性级规划减少多属性候选干扰，但不代表真实合约生态的整体性能。已有适配真实来源记录用于说明运行状态和工程边界；其中 `budget_exhausted` 是预算内未观察到反例的 right-censored 状态，`compile_error` 是工程状态。生成的 Harness 与 Original Echidna 多交易执行采用不同的调用者、交易边界和回滚语义，不能按同一执行模型解释。

**关键词：** 智能合约；显式安全属性；多交易序列；状态依赖；Harness synthesis；属性定向规划

## 1 引言

智能合约测试面对的不是一次函数调用，而是一个由交易顺序逐步演化的持久状态。一个安全属性可能只读取最终状态中的一个余额、标志位或计数器，但达到该状态往往需要先调用准备函数，再调用改变状态或触发边界的函数。参数搜索只有在顺序正确的状态前缀已经建立时才有意义。

多 property 合约进一步引入了一个容易被隐藏的规划问题。设 `echidna_balance_safe()` 读取 `balance`，`echidna_owner_safe()` 读取 `owner`。如果规划器把两者的读取变量合并为 `{balance, owner}`，那么写入 `owner` 的函数可能被当作 `balance` 属性的候选前缀。候选路径仍然可能满足一般读写依赖，但它们与当前被评估的 property 没有直接关系。当候选需要经过排序并截断为 Top-K 时，跨 property 路径会占用真正目标路径的位置。

本文把研究问题限定为：能否把显式 property identity 贯穿读取集合、目标函数、依赖路径、重复扩展、值证据排序和 Harness 生成，使每个 property 获得独立的交易序列规划。这个问题关注候选构造和 provenance，而不是重新实现一个独立的通用 fuzzing engine。未指定 property 时保留 legacy union 接口，使历史 runner 仍能读取原有语义；新实验通过显式 `--property` 进入 per-property 模式。

本文的贡献有三点：

1. **属性级候选隔离。** 对显式目标 property 独立解析 full-name 和 read-set，沿写入目标状态的函数构建 backward dependency paths，并在受控多属性干扰场景中度量无关候选、目标 rank 和 Top-K 命中。
2. **可组合且可追溯的规划流程。** 在 property identity 不丢失的前提下接入 bounded repetition、lightweight value evidence、Top-K 和 property-specific Harness proxy，同时保留无 `--property` 时的 legacy union 行为。
3. **有边界的证据解释。** 将 controlled mechanism evidence、有限适配真实来源证据、`budget_exhausted` 和 `compile_error` 分层报告，并明确 Harness 与 Original 的执行模型差异。

## 2 相关工作

### 2.1 Stateful smart-contract fuzzing

智能合约模糊测试需要同时处理参数、调用顺序和持久状态。Echidna-style property testing 以显式属性描述不应发生的状态条件，底层测试器继续搜索能够使属性失败的输入与交易。本文沿用这种属性接口，将研究对象放在属性模糊测试之前的候选序列规划，而不是替换底层搜索器。相关的智能合约模糊测试工作包括 ContractFuzzer、sFuzz、ILF 和 Echidna 的方法线 [@jiang2018contractfuzzer; @nguyen2020sfuzz; @he2019ilf; @grieco2020echidna]。

Harvey 将有状态合约测试中的调用顺序和状态推进作为重要的搜索对象；ConFuzzius 则代表了数据依赖与混合分析结合的方向 [@wustholz2020harvey; @torres2021confuzzius]。本文与这些方向共享多交易状态测试的背景，但输出层次不同：本文首先生成与显式 property 绑定的候选路径，并把它们外置为可检查的序列或 Harness，而不是声称复现或替代这些工具的完整搜索过程。

### 2.2 数据流、状态依赖与序列引导

SMARTIAN 代表静态与动态数据流辅助的智能合约模糊测试方向 [@choi2021smartian]。IR-Fuzz 以及其他中间表示或数据流引导方法属于相邻的输入组织方向。MuFuzz 关注序列感知的变异和 seed 组织，是另一个与多交易测试相关的邻近方向。本文与这些工作在“利用状态或序列结构减少无关探索”的研究空间上相关，但本文的切入点是显式 property read-set 驱动的外部 preprocessing：读集合决定目标函数，目标函数决定依赖候选，候选再进入有界重复和值证据环节。本文没有对 SMARTIAN、IR-Fuzz 或 MuFuzz 进行同 property oracle、同 caller model、同预算和同结果定义的 executable comparison，因此不据此进行工具排名。

### 2.3 约束与学习辅助的交易推理

约束分析、符号执行和学习辅助的交易序列推理提供了与本文不同的搜索路径。SmarTest 可作为此类方向的 conceptual positioning。本文的 value stage 只读取已有的常量写入、简单 requirement 和比较关系，输出 match、conflict、unknown 等轻量证据；它不等同于 SMT solver、symbolic execution、mapping inference 或语言模型交易推理。SmarTest 的正式书目信息和具体方法边界仍需在定稿前依据仓库 citation registry 核验，本文不从未核验的引用推导额外事实或实验数字。

### 2.4 本文的定位

本文的方法位于“显式安全属性”和“交易序列候选规划”交叉处。它不声称首次提出状态依赖、交易排序、重复调用或属性测试，而是检验 property identity 是否能减少多属性合约中的候选混杂，并将该 identity 传递到后续 Harness。相关工作在本文中用于定位设计空间；没有公平、可复现的 executable protocol 时，不把相关工具写成已比较的 baseline。

## 3 问题定义与设计目标

### 3.1 显式属性与交易序列

设合约状态为 `s`，显式安全属性为 `P(s)`。测试器的目标是寻找交易序列 `T = (t_1, ..., t_n)` 及其参数，使执行后的状态满足 `P(s_n) = false`。本文的规划器不负责证明属性，也不负责穷举所有输入；它负责从函数状态读写和 property identity 中产生候选序列。

对合约函数 `f`，记 `R(f)` 为读取的状态变量集合，`W(f)` 为写入的状态变量集合。对 property `P_i`，记 `R(P_i)` 为该 property 自身的 read-set。legacy union 模式使用

`R_union = union_i R(P_i)`。

显式 per-property 模式使用

`R_selected = R(P_i)`。

两种模式的差别发生在候选规划过程中，而不是对历史结果重新解释。`R_union` 保留旧接口的兼容性，`R_selected` 为新实验提供 property-specific provenance。

### 3.2 多属性候选干扰

若两个 property 读取互不相同的终态变量，union 模式会把两个变量都传给 target-function discovery。写入非目标变量的函数因此可能形成合法的依赖边，并在路径排序后进入 Top-K。该现象不一定导致动态执行失败，但会改变候选池的组成和目标路径的 rank。本文用 `MultiPropertyInterference` 隔离这一机制：目标 property、两个 distractor property 以及它们的状态依赖链彼此独立，预先定义的目标序列为 `prepareTarget() -> triggerTarget()`。

### 3.3 设计目标

方法设计遵循三个目标：

- **身份一致。** 从 resolver 到 Harness 的每条路径都保存 `property_function`，不能在后处理或 proxy 生成时重新混入其他 property。
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

这一规则同时处理了两个需求：短名称仍能兼容当前仓库中常见的 `echidna_xxx()` full-name 格式；完整签名则保留参数信息，不被错误的 basename fallback 覆盖。Harness resolver 还检查 property 是否带参数。当前 Harness 不支持带参数 property，因此显式选择此类 property 时直接报错。

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

基本 property planner 的路径搜索对函数重复和最大长度有明确边界；静态 path 是候选结构，不是运行时可达性证明。一个候选包含某个写读边，只表示它满足规划器定义的局部依赖关系，实际是否能执行仍取决于参数、调用者、资金、环境和 revert 行为。

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

如果写入是符号值、条件无法静态判断或变量来自不支持的复杂表达式，结果保持 unknown，而不是被改写为满足。此处理不使用 SMT、symbolic execution、mapping inference、跨合约推理或复杂算术推理。它改变已有候选的排序优先级，不重新 merge 不同 property 的 path list。

### 4.7 Top-K

Top-K 是候选截断配置，不是成功率模型。`K=1` 只保留最高排序候选，较大的 K 保留更多备选路径。为了统计完整 candidate count，`results/per-property-isolation/summary.json` 使用 `top_k=1000`，实际保留数量为 8 和 1，均未因截断丢失候选。论文中的 target rank 是 expected sequence 在排序候选列表中的位置；Top-1/3/5 hit 是该 rank 是否不超过对应 K。

### 4.8 Property-specific Harness proxy

legacy Harness 执行模型收集合约中全部零参数 `echidna_` property 并生成 proxy。显式模式只选择 resolver 确认的 property，只加载 contract-level 和 path-level `property_function` 与 CLI 请求相匹配的路径，并只生成一个目标 proxy。若 sequence JSON 缺少 property provenance、contract-level property 与 path-level property 不一致、CLI property 与 JSON 不一致或 property 不存在，生成器 fail closed。若 property 有参数，当前 Harness 明确报错，不静默回退到其他 property。

生成的 Harness 会在目标合约引用旁加入简短的 `Target property: ...` 注释，便于检查生成物。该注释和 proxy 选择用于 provenance，不改变底层执行语义。

### 4.9 Execution-model boundary

Original Echidna 多交易模式和生成 Harness 采用不同的执行模型。原生模式中的目标调用可能分别拥有 sender、`msg.value`、区块环境和交易回滚边界；Harness 执行模型通常由 wrapper 发起连续目标调用，调用者可能固定为 Harness 地址，某一步失败还可能影响整个 wrapper 的状态提交。因此 Harness 是候选路径的可执行封装，不应被解释为原生多交易语义的同一实现。

这一区分还影响指标解释。Harness 的 sequence function、调用次数和 wall time 只能在相同 candidate、property、预算和执行模型内作描述性比较。生成 proxy 成功或 Harness compile smoke 不能替代原生多交易语义检查，也不能单独证明漏洞可达。

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
4. **Engineering status evidence。** `compile_error` 单独记录为构建、导入或 Harness 适配状态；它不进入检测结果分母。`budget_exhausted` 单独保留为 right-censored observation。

受控候选指标、动态属性违反和工程运行状态分别回答不同问题，不能互相替代。

### 5.3 RQ1：per-property isolation

实验对象是 `contracts/benchmarks/MultiPropertyInterference.sol`。它包含 `echidna_target_safe()`、`echidna_distractor_a_safe()` 和 `echidna_distractor_b_safe()` 三个互相独立的 property。目标序列在实验前固定为 `prepareTarget() -> triggerTarget()`；planner 配置为 `max_length=6`、`top_k=1000`，路径构造器为 `build_relevant_paths`。

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

LEGACY_UNION 的 7 条无关候选来自 distractor property 相关链，说明 union read-set 会把不属于 P_TARGET 的路径带入候选池。PER_PROPERTY 只保留 `targetValue` 和 `triggerTarget()`，目标序列成为唯一候选。该结果直接支持“属性级规划减少跨 property 候选干扰”这一受控机制结论。它没有测量 Echidna 的搜索时间、漏洞发现率或真实合约总体性能，因此结论停留在 candidate isolation、rank 和 Top-K 层面。

### 5.4 RQ2：组件行为

已有六个 controlled scenarios 用于分离不同路径障碍。它们覆盖无关状态路径、状态值方向、重复调用、多路径和多属性等机制问题。主配置中 Full-K1 观察到 180/180 次属性违反，Original 观察到 171/180 次。该结果说明，在预先设计的受控障碍和声明配置下，组合规划器能够为动态搜索提供有效触发前缀；它不等于对所有合约的检测率结论。

组件解释来自两个层面。首先，property stage 通过 read-set 过滤目标相关路径；RQ1 的独立表格量化了这一点。其次，repeat stage 保留 `stepX() -> stepX()` 这类有界重复，value stage 对已有写入和 requirement 计算 match/conflict/unknown，Top-K 决定这些候选中哪些被保留。代码输出的 `property_score`、`value_score`、`value_edges` 和 `value_rank` 提供了候选排序 provenance。由于当前证据没有 solver、符号执行或完整运行时可达性验证，RQ2 的结论是组件按设计影响候选构造和排序，而不是组件单独保证动态发现。

### 5.5 RQ3：有限适配真实来源池

已有适配真实来源证据包含 4 个 candidate 和 120 条预注册运行。记录分为 80 条 usable/descriptive records 与 40 条 `compile_error` engineering rows，其中 observed statuses 为 79 条 `falsified`、1 条 `budget_exhausted` 和 40 条 `compile_error`。

两个 Echidna-origin candidates 构成有限的 non-compile-error comparable subset：Original 为 20/20 条属性违反，Full-K1 为 20/20 条，Full-K5 为 19/20 条，另有 1 条 right-censored。该子集支持的表述是：在两个 adapted Echidna-origin candidates 上，Full-K1 和 Full-K5 仍观察到属性违反。由于 candidate 数量少、适配改变了部分工程条件，且 Harness 与 Original 的 caller/transaction model 不同，这些数字不支持方法排序或生态级性能结论。

SmartBugs Original-only subset 的 20 条记录用于说明适配目标在 Original 执行模式下可以运行并观察属性违反。SmartBugs Harness 的 40 条记录为 `compile_error`，其含义是 Solidity 0.4.25 下 Harness 生成、依赖导入或编译链存在工程限制。该状态与动态 detection outcome 分开报告，不把它计作属性未发现。

### 5.6 结果口径

- `falsified`：在声明的 execution model、预算和配置内观测到属性违反。
- `budget_exhausted`：在预算内没有观测到属性违反，是 right-censored observation；不能写成 property safe、pass 或无漏洞。
- `compile_error`：构建、导入或编译环节未完成，属于 engineering status；不能作为 detection failure 或负面检测率。
- candidate count、irrelevant ratio、target rank 和 Top-K hit：规划层指标，不是动态漏洞发现指标。
- Total calls、sequence length 和时间：只作同执行模型、同 candidate、同 property 条件下的描述性轨迹信息，不直接推出加速结论。

## 6 讨论

### 6.1 属性 identity 是候选规划的控制变量

多 property 合约中的关键问题不是 property 数量本身，而是不同 property 的状态依赖是否在规划过程中被混合。`MultiPropertyInterference` 的结果显示，union 模式把 3 个变量和 3 个 target functions 交给同一候选生成过程，目标序列排在第 6 位；显式模式只处理目标变量和目标函数，目标序列排在第 1 位。由此，property identity 不只是输出字段，它决定了候选图的节点、边和 Top-K 内容。

该结论也解释了为什么 legacy union 行为仍需保留。旧 runner 可能依赖 union schema；删除它会把历史实验的输入语义和新实验混在一起。显式 `--property` 因而是版本边界清晰的新增入口，而不是对旧结果的回算。

### 6.2 规划层指标与动态检测结果

candidate count、irrelevant ratio 和 target rank 衡量规划器向动态测试器提供了什么；它们不测量参数空间中的真实可达性。Top-1 命中表示 expected sequence 位于前 1 个候选，不能替代 Echidna 在给定预算中找到反例。类似地，value match 说明一个静态写入与 requirement 在支持的轻量表示下相容，不说明复杂算术、mapping 或外部调用后的条件必然成立。

这种分层使 RQ1 和 RQ2 可以在不扩大结论的情况下回答：RQ1 关注候选污染，RQ2 关注组件实现。动态 falsification 和 适配真实来源池状态则放在 RQ3 中，以保持证据类型的区别。

### 6.3 Original 与 Harness 的解释边界

Harness 适合把候选序列变成可检查的 Solidity 生成物，并让测试器继续探索参数；它也让 property proxy、sequence function 和编译状态可以被记录。然而 wrapper 的调用者、交易原子性、回滚范围、`msg.value`、block context 和 external-call behavior 可能与 Original 不同。因此，本研究把 Harness 视为一个明确的 execution model，而不是对 Original 的语义替身。

这一区分直接影响 适配真实来源结果：两个 Echidna-origin candidates 的有限可比子集可以说明不同配置下仍观察到属性违反，但不能把 20/20、19/20 转写成跨模型的相对性能排序。SmartBugs Harness 编译限制同样只说明工程链边界。

## 7 有效性威胁

### 7.1 Controlled benchmark 的外部有效性

受控 benchmark 的状态变量、属性和依赖链是为单一机制障碍设计的。它们能够隔离候选污染、重复需求或值方向，却不能代表真实合约的函数数量、依赖复杂度、调用者分布、编译器版本或资产交互。因而 controlled 结果支持机制解释，不支持真实生态外推。

### 7.2 Harness 与 Original 的语义差异

Original 和 Harness 在 caller、transaction boundary、atomicity、rollback scope、`msg.value`、block context、external call 和 reentrancy boundary 上可能不同。Harness proxy 的生成和编译只能证明生成物通过相应工程步骤，不能证明两个执行模型产生同样的搜索空间或同样的反例含义。论文中的结果表必须标注 execution model。

### 7.3 Right-censored budget 状态

`budget_exhausted` 只说明给定 budget、seed 和配置内没有观察到反例。它是删失记录，不是安全证明，也不应进入“属性通过”的分母。当前适配真实来源池中的 1 条记录必须在状态表和讨论中保留。

### 7.4 `compile_error` 的工程含义

`compile_error` 发生在构建、导入或编译链上，反映工具链或 source adaptation 未完成。它不是动态检测失败，也不是合约没有漏洞的证据。40 条 SmartBugs Harness compile rows 作为 engineering status 单独保存，不与 79 条 falsified 或 1 条 right-censored 混成一个 detection metric。

### 7.5 跨工具比较的公平性

本文没有为 SMARTIAN、ConFuzzius、Harvey、MuFuzz、IR-Fuzz 或 SmarTest 建立同 property oracle、caller model、transaction budget、seed 和 outcome definition 的完整 executable protocol。SMARTIAN 的仓库材料也只覆盖两个简单整数目标，不能升级为公平的第二 baseline。因此相关工作只承担 conceptual positioning，不构成跨工具排名。

### 7.6 小规模 适配真实来源池

4 个适配真实来源候选 主要用于检查运行状态和适配边界。它们的来源、编译器版本、属性接口和 Harness 条件并不覆盖真实生态的多样性；重复 seed 也不能替代更多独立 source。RQ3 的结论必须写成有限 pool 上的 descriptive evidence。

### 7.7 规划指标的构念边界

静态 candidate count、rank、Top-K hit 和 value evidence 不是完整动态可达性、检测率或安全性的同义词。当前规划器不处理 SMT、symbolic execution、mapping inference、跨合约推理和复杂算术。对复杂外部状态和调用者交互，结果需要额外语义复核。

## 8 结论

本文研究了显式安全属性下的多交易候选污染问题，并实现了从 property resolver、selected read-set、target-function discovery、backward dependency paths 到 bounded repetition、lightweight value ranking、Top-K 和 property-specific Harness proxy 的连续规划流程。其关键设计是让 property identity 参与候选生成，而不是在所有 property 的 union read-set 上统一排序。

在预先定义的 `MultiPropertyInterference` 场景中，LEGACY_UNION 产生 8 个候选且 7 个与目标 property 无关，目标序列 rank 为 6；PER_PROPERTY 只产生 1 个目标相关候选，rank 为 1。该结果支持属性级规划减少多属性候选干扰这一机制结论。既有六场景 controlled package 和有限 适配真实来源记录 进一步展示了组件行为、运行状态和工程边界，但不改变结论的范围。

本文的主要价值在于可追溯的 property-specific candidate planning 与明确的 execution-model accounting。后续若要扩展外部有效性，需要新的、预注册且语义可比的研究问题；这不属于本稿当前证据已经回答的范围。

## 9 解释边界

本文的结论范围由证据类型和执行模型共同限定。

- MultiPropertyInterference 是预先设计的 controlled mechanism benchmark。其结果支持“属性级规划减少多属性候选干扰”这一机制判断，不外推为真实合约生态的整体性能结论。
- property variables、target functions、candidate count、target rank 和 Top-K hit 是规划指标；它们不直接等同于动态检测率、漏洞数量或运行加速。
- budget_exhausted 仅表示在给定预算、seed 和配置内未观察到反例，是 right-censored observation，不能作为安全证明或测试通过结论。
- compile_error 表示构建、导入或编译链未完成，属于工程状态，不进入动态检测结果分母，也不解释为合约未检测到问题。
- Original Echidna 多交易与 Harness 执行模型在 caller、transaction boundary、atomicity、rollback scope、msg.value、block context、external call 和 reentrancy boundary 等方面可能不同。Harness 是候选路径的可执行封装，不应据此推断两种模型具有相同语义。
- SMARTIAN、ConFuzzius、Harvey、MuFuzz、IR-Fuzz 和 SmarTest 在本文中仅作概念定位；由于没有同 property oracle、caller model、预算和结果定义下的可执行公平比较，本文不作跨工具排名。
- lightweight value evidence 只用于现有候选的排序，不包含 SMT、symbolic execution、mapping inference、跨合约推理或复杂算术推理。
- 适配真实来源池用于描述运行状态和工程边界，候选数量与适配条件不足以代表真实生态分布。

## 参考文献与核验说明

正文沿用仓库中已登记的 cite key，包括 Harvey、SMARTIAN、ConFuzzius、Echidna、ContractFuzzer、sFuzz、ILF 和 QuickCheck。MuFuzz 在本文中作为邻近方向出现，正式出版元数据仍需在定稿前复核；IR-Fuzz 与 SmarTest 只承担概念定位，正式引用 key 和具体方法描述也需依据 citation registry 完成核验。此处不引入新的作者、年份、venue 或实验数字。
