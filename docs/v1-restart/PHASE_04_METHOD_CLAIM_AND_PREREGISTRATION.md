# V1 Restart — Phase 04：Method Claim Freeze、Semantic Boundary 与 Public Benchmark Preregistration

审计日期：2026-09-06  
审计分支：'develop'  
审计时 HEAD：'1b686dd0409825e3a52232fcfcae6038f9b7cddb'  
方法线：V1 / 'Full-v1.0'

## 1. Final status: PASS WITH WARNINGS

Phase 04 的唯一产物是本决策文档。方法定位、可安全主张的创新边界、Harness 与 Original 的语义边界，以及 Phase 05 公开 benchmark 的预登记字段和放行条件已经固定。

状态为 'PASS WITH WARNINGS'，原因如下：

- V1 可以被清楚地表述为既有 property-based fuzzer 的前处理和 Harness synthesis 方法，而不是新的通用 fuzzer。
- 与 SMARTIAN、IR-Fuzz、MuFuzz 等工作的重叠风险已明确标为 high 或 medium-high；本阶段不把 state dependency、transaction sequence、repeated calls、value guidance 或 Top-K 单独包装成首创。
- 语义审计已有 11 个目标：10 个 'supported'、1 个 'conditional'；固定成功路径的差分重放为 11/11 一致，但这不是多交易搜索过程的等价证明，所有目标仍有 transaction-atomicity caveat。
- 当前公开证据只有 5 个 C-1 目标，且包含源码适配；SMARTIAN 外部批次只有 2 个简单整数目标。因此当前证据仍不足以支持广泛的真实合约泛化或竞品排名。
- 本次 git fetch --prune 因 GitHub SSH public-key 权限失败；本地 develop 与当前 origin/develop 引用显示同步。该网络/凭证问题被保留为 provenance warning，没有据此修改文件或猜测远端状态。

本状态不表示已经批准 Phase 05 的正式重复运行。Phase 05 仍必须先完成预登记、编译/路径预检和单 seed smoke，并由研究者复核后再决定是否进入正式批次。

## 2. Scope statement

本阶段只读取既有说明、冻结 manifest、白名单、语义审计、C-1 适配说明和 Phase 01–03 报告，并整理本决策文档。

本阶段：

- 没有运行 Echidna；
- 没有运行 Slither；
- 没有运行 solc；
- 没有运行 30 seed、formal full batch、C-1/B-2/matched-random/SMARTIAN/V2/C2 实验；
- 没有生成新的 raw log、Harness、CSV、统计表或论文结果表；
- 没有修改 analyzer/、contracts/、configs/、冻结 results/ 或 paper-ready/。

开始前检查结果为：工作区干净，git switch develop 已确认当前位于 develop，HEAD 为本报告记录的 SHA。git fetch --prune 仅因 SSH 权限失败，未产生工作区改动。

## 3. Method name freeze

### 中文名称

**面向属性模糊测试的属性定向交易序列 Harness 合成方法**

### 暂定英文名称

**Property-Directed Transaction-Sequence Harness Synthesis for Property-Based Smart Contract Fuzzing**

### 方法身份边界

V1 是面向既有 property-based smart-contract fuzzer 的前处理、sequence planning 和外部 Solidity Harness synthesis 方法。它从用户已经声明的 Echidna safety property 出发，生成可检查的候选交易序列并将 Top-K 序列封装为 Harness，再交给 Echidna 继续进行参数和属性反例探索。

V1 不是新的通用智能合约 fuzzer，不是 Echidna 的 fuzzing engine 替代品，也不修改 Echidna core。V1 的输出是面向特定属性和特定合约的候选 Harness；输出是否适用取决于静态筛查、编译预检、调用者/环境条件和差分语义复核。

## 4. One-paragraph paper positioning

本文将 V1 定位为一种面向既有属性模糊器的、属性定向的交易序列 Harness 合成方法。给定 Solidity 合约和 Echidna safety property，V1 识别属性读取的状态变量，反向保留可能影响这些变量的状态写入链，在有界范围内允许必要的重复函数访问，并用轻量级常量写入与 require 条件证据对候选序列进行可解释排序，最终输出可审计的 Top-K Solidity Harness，供 Echidna 在不修改其核心的情况下探索参数和属性反例。V1 的贡献主张限于这种组合式、可审计的前处理接口及其在声明范围内的机制证据；它不主张普遍优于 Echidna 或其他 fuzzer，也不把单交易 wrapper 与 Original 的多交易执行当作完全等价。

## 5. Contributions we can safely claim

以下表述可以在有对应实验和审计来源时使用：

1. **显式属性定向。** V1 从 echidna_ safety property 读取的状态变量出发，保留最终可能影响该属性的写入链，而不是只按一般读写依赖保留所有候选路径。
2. **组合式方法管线。** Property、Repeat 和 Value 不是互相独立的口号，而是依次作用于候选生成、必要重复访问和轻量值方向匹配的组合管线。
3. **可解释的 Top-K 输出。** V1 保存候选数量、路径内容、重复访问标记、value match/conflict/unknown 证据和显示排名，使某条路径进入 K1/K5 的原因可以被人工检查。
4. **外部 Harness 接口。** V1 通过生成 Solidity Harness 接入 Echidna，不修改 Echidna core；这使候选序列、目标函数参数和最终属性代理可以作为独立产物审计。
5. **有界重复访问。** 在声明的访问上限和路径长度上，V1 可以保留必须重复调用同一函数的候选；RepeatedCall 的受控回归支持这一窄机制结论。
6. **轻量值证据。** 对支持的简单常量写入和条件比较，V1 可标注 MATCH、CONFLICT 或 UNKNOWN 并改变候选排序；它不是符号执行器，也不是一般 Solidity path-constraint solver。
7. **语义边界显式化。** V1 把 Harness 与 Original 的 caller、transaction atomicity、rollback、environment 和 value 语义作为纳入条件审计，而不是默认二者等价。
8. **受控证据。** 现有六个合成基准支持对应障碍上的机制复现；五个 C-1 公开目标支持“在已筛查和已适配任务上的分层结果”，不支持对真实合约总体的外推。

上述贡献是组合贡献。相关工作核查完成前，不应把“属性定向”或“Harness synthesis”写成文献意义上的绝对首创。

## 6. Claims we must not make

以下表述不得作为 V1 当前证据支持的结论：

- V1 是新的通用智能合约 fuzzer，或已经替代 Echidna；
- V1 普遍优于 Echidna、SMARTIAN、MuFuzz、IR-Fuzz、Harvey、ConFuzzius 或其他现有工具；
- V1 首次提出 state dependency、transaction sequence generation、repeated calls、value guidance、Top-K ranking 或 multi-transaction fuzzing；
- Harness 与 Original 的多交易执行完全等价；
- Original 与 Harness 的 Total calls 是相同层次、相同工作量，或可以据此直接声称 speedup；
- 候选路径由 92 条降到 31 条就必然带来端到端 fuzzing 加速；
- budget_exhausted 等于 property passed、合约安全或性质已被证明；
- Harness 报告 falsified 自动证明 Original 多交易语义下存在相同反例；
- 5 个公开 C-1 目标代表真实合约生态，或 K1 在公开任务上普遍可靠；
- 当前两个 SMARTIAN 整数目标的 60/60 结果构成广泛外部 SOTA 排名；
- 将 V2、C2 开发材料或 provenance 未解决的 matched-random 历史控制并入 V1 主结果。

## 7. Related-work overlap table

本表只冻结当前可安全使用的概念边界，不替代完整文献综述。作者、年份、实验规模、实现版本和公平复现实验口径必须在 Phase 05 前依据原始论文或官方资料逐项核查；本表没有据此编造这些信息。

| Work | Main idea | Overlap with V1 | Difference / defensible gap | Risk level | How to phrase safely |
|---|---|---|---|---|---|
| Echidna | 以用户属性/不变量为 oracle 的 property-based smart-contract fuzzing，并探索函数调用和参数。 | V1 使用 Echidna property，并把生成序列交给 Echidna。 | V1 是外部前处理和 Harness synthesis 层，不替代 Echidna 的执行引擎；V1 固定部分顺序，Echidna 仍负责运行时参数和属性检查。 | medium | “V1 为 Echidna 增加可审计的属性定向 Harness 前处理，用于辅助深层属性反例探索。” |
| Harvey | 以定向、按需的交易序列探索控制状态空间。 | 都关注跨函数/跨交易状态和序列搜索空间。 | V1 的候选主要在 fuzzing 前由静态/轻量证据离线生成并输出 Top-K Harness；Harvey 的在线按需探索与 V1 不是同一执行策略。 | medium | “V1 研究的是离线属性定向候选合成与可审计 Harness 接口，不把它表述为优于在线按需序列探索。” |
| SMARTIAN | 结合静态和动态数据流信息，引导有效交易序列和参数探索。 | 状态/数据依赖、交易顺序引导、深层状态序列均有明显重叠。 | V1 面向显式 Echidna property，输出外部 Solidity Harness，采用较轻量的静态 Value/Repeat 证据；这只能构成待验证的工程与接口差异，不构成依赖排序本身的首创。 | high | “与 SMARTIAN 的核心序列/数据流引导存在高重叠；V1 仅主张属性定向、可审计外部 Harness 和明确语义范围的组合差异。” |
| ConFuzzius | 将 fuzzing、数据依赖和约束求解等机制组合，用于更有意义的交易/参数探索。 | 都利用依赖关系缩小状态空间，并关注多交易漏洞。 | V1 不主张混合求解器能力，主要输出 property-directed Harness 和轻量值证据；不能把“使用依赖生成序列”单独当作差异。 | medium-high | “V1 是较轻量的属性定向 Harness synthesis 管线，与混合约束求解器路线互补；是否有实质收益需公平实验。” |
| IR-Fuzz | 使用函数间数据依赖和调用顺序等信息，定向延长或选择交易序列。 | 依赖引导、序列筛选/排序和深层状态探索直接重叠。 | V1 将目标属性读取状态作为反向筛选入口，并显式生成可审计 Top-K Harness；IR-Fuzz 的具体算法和执行环节必须以原始论文核查，不能据此声称没有重叠。 | high | “V1 与 IR-Fuzz 在数据依赖和序列引导上存在高重叠；可辩护范围是显式 property-directed 外部 Harness 组合，而非一般 sequence guidance。” |
| MuFuzz | 面向多交易状态的序列/数据流引导和序列感知变异，处理依赖与重复访问等问题。 | transaction sequence guidance、RAW/状态依赖和 repeated-call 处理均重叠。 | V1 更偏静态、轻量、属性定向，并将序列固化为外部 Harness；Repeat 和 dependency ordering 不能单独作为创新。 | high | “V1 与 MuFuzz 的序列和依赖引导有高重叠；论文只主张 property-directed、可解释 Top-K 和外置 Harness 的组合边界。” |
| SmarTest | 使用语言模型引导 symbolic execution，以寻找易受攻击的交易序列。 | 都关注跨交易漏洞路径和交易序列选择。 | SmarTest 属于 LM-guided symbolic execution；V1 属于 property-directed static/lightweight analysis + harness synthesis for fuzzing。两者执行范式不同，但不能泛化成完全不重叠。 | medium | “SmarTest 与 V1 的执行范式不同，但都涉及脆弱交易序列；V1 不声称两者完全没有概念重叠。” |

结论：V1 最可辩护的不是 state dependency、交易排序、重复调用或值引导的单点首创，而是“显式属性定向 + 可解释 Top-K + 外部 Harness 合成 + 语义边界审计”的组合。该组合仍需后续文献核查和公开任务实验支持。
## 8. Harness semantic boundary table

当前 V1 Harness 由一个外部 wrapper 在一次调用内连续调用候选目标函数；Original 则由 Echidna 以多笔独立目标交易探索序列。下表是纳入 Phase 05 前的最低语义边界。

| Semantic factor | Original multi-transaction behavior | Harness wrapper behavior | Risk | Allowed handling | Exclusion / conditional rule |
|---|---|---|---|---|---|
| msg.sender / caller alternation | 每笔目标交易的 sender 可能变化，序列中可以交替调用者。 | wrapper 调用目标合约时通常由同一个 Harness 地址发起，候选内部固定 caller 关系。 | high | 若源码不读取 caller 且属性不依赖 caller，可在静态审计和固定成功路径重放后标 supported。 | 读取 msg.sender、tx.origin 或依赖 sender 交替时至少 conditional；无法对齐时 excluded。 |
| Transaction atomicity | 每个函数调用是独立交易；前一步成功状态不会因后一步交易失败而回滚。 | 多个目标调用在一个 wrapper 交易中执行，边界被合并。 | high | 仅对每一步都成功、只比较最终属性相关状态的固定路径作窄范围纳入。 | 依赖跨交易提交、观察或失败后保留状态时 conditional；无法重放对齐时 excluded。 |
| Revert rollback scope | 某一笔交易 revert 通常只回滚该笔交易，之前交易的状态保留。 | wrapper 内某一步 revert 可能使整个 wrapper 回滚；当前 Harness 不提供通用逐步隔离。 | high | 必须单独记录每一步成功/失败，并做成功路径与中间失败负面对照。 | 失败前缀是目标语义的一部分而又不能对齐时 excluded。 |
| msg.value | 每笔交易可以有独立 value，且 payable 函数可按交易接收资金。 | 当前生成器不提供通用的逐步 msg.value 建模；wrapper 的 value 不能自动等价为每一步 value。 | high | 只有不读取 msg.value、不依赖资金转移且无 payable 语义时可 supported。 | value 影响状态、余额或属性时 conditional；无法显式适配时 excluded。 |
| block.timestamp / block.number | 不同交易可能处于不同区块或时间。 | wrapper 内部调用共享同一外层交易环境，不能代表每步推进。 | medium-high | 源码不读取这些环境变量时可纳入；若读取则需预先设计环境等价性审计。 | 时间锁、区块间隔或属性依赖环境推进时 excluded，除非有明确受控适配。 |
| External calls / reentrancy | 外部调用、回调和重入发生在各独立交易上下文中，交互顺序可能不同。 | 外部调用嵌套在 wrapper 的单交易上下文中，调用栈和回滚边界可能不同。 | high | 仅在源码闭包无低级调用、delegatecall、外部回调和重入敏感点时可 supported。 | 存在外部交互或重入依赖时至少 conditional，没有差分审计不得进入主比较。 |
| Access control requiring different callers | Original 可由不同 sender 分别完成部署、授权和后续操作。 | wrapper 通常由同一个 Harness 地址完成全部步骤，可能人为满足或绕过 caller 关系。 | high | 只允许固定同 caller 的窄命题；必须在 manifest 中记录 caller 假设。 | 需要不同 caller 或 caller alternation 时 conditional；不能控制/重放时 excluded。 |
| Payable functions | 每个 payable 目标交易可有独立 value 和余额变化。 | 当前 wrapper 不自动生成逐步 payable/value 语义。 | high | 不包含 payable 入口且无资金依赖时可 supported。 | 包含 payable 或资金流目标时 conditional/excluded，不得默认与 Original 可比。 |
| Constructor / initialization state | Original 目标合约在部署时确定初始化 sender、value 和初始状态，之后跨交易使用。 | Harness constructor 创建目标合约一次，再由 wrapper 使用；部署者和初始化上下文可能不同。 | medium-high | 初始状态、编译器和 constructor 无环境依赖时可纳入；每个 run 必须使用新鲜部署。 | constructor 参数、部署者权限或初始化环境影响目标时 conditional；无法复现时 excluded。 |
| Stateful sequence length vs wrapper call count | seqLen=4 表示最多四笔独立目标交易，顺序和 sender/参数由 Echidna 探索。 | seqLen=1 只表示一次 wrapper 外层调用，其中可能封装四个或更多目标调用。 | high | 只在各自执行模型内报告发现率；用固定 trace 验证窄范围最终状态。 | 不得将两者当作等量交易预算；需要等量工作量的比较 excluded。 |
| Echidna Total calls meaning | 主要统计 Echidna 外层目标调用/交易层次的次数。 | 统计 wrapper 的外层调用，内部目标函数调用数量被折叠在一次 wrapper 中。 | high | 可分别报告为日志指标，并明确计数层次。 | 不能用二者差值声称 speedup、工作量相等或顺序搜索成本相同。 |

必须持续遵守以下解释规则：

- Total calls 不能作为 Original 与 Harness 的等价工作量；
- budget_exhausted 不能写成 property passed；
- Harness 的 falsified 只说明 wrapper 执行模型下观察到了属性反例，不自动证明 Original 多交易语义完全等价；
- 只有 differential replay 或等价强度足够的 semantic audit，才能把“固定成功路径的结果一致”提升为更强的窄范围结论；即使如此，也不等价于所有失败前缀、sender 搜索或运行时环境的等价。

当前语义证据的实际解读是：11/11 条预先固定的成功路径在相同 caller 关系下重放一致；exercise2-access-control 仍是 conditional，因为 Original 可能交替 sender，而 Harness 固定为同一 Harness sender；通用负面对照已经展示 caller alternation 和中间失败回滚的差异。因此 supported 是“未检出额外高风险特征且通过窄重放”的分类，不是完整语义等价证明。

## 9. Dataset evidence currently available

论文制表应以 paper-ready/manifest.tsv 和 results/paper-data/dataset-whitelist.csv 为逻辑入口，不递归扫描全部 results/。当前可用证据如下：

| Evidence block | Current evidence | Allowed interpretation | Boundary |
|---|---|---|---|
| 六个合成基准 | Full-K1 180/180；Original 171/180，包含 Formal 主批次与 B-2 扩展。 | 在指定受控障碍上，V1 能生成并使用有效候选 Harness；Property、Value、Repeat 在对应案例中有可观察作用。 | 合约为专门设计的小型机制基准，不代表真实生态；异质批次不能未经说明做 pooled 因果结论。 |
| Formal 候选空间 | 四个 Formal 基准 Dependency retained paths 合计 92，Property retained paths 合计 31，减少 61 条，即 66.3043478%。 | 候选空间压缩和属性相关筛选的描述性证据。 | 路径减少不自动等于 fuzzing 加速或更少底层工作。 |
| 五个 C-1 公开目标 | Full-K5 149/150；Original 144/150；Full-K1 120/150。 | 在已筛查、已适配、预先固定预算的 5 个公开目标上的运行级分层结果。 | 公开任务数量小；适配内容和 Harness 语义必须披露；不能外推成真实合约总体或 K1 普遍可靠。 |
| C-1 Top-K 证据 | exercise2-access-control 的 Full-K1 为 0/30，Full-K5 为 30/30；正确路径排名为第 2 的事实使 K1 失败。 | Top-K 选择是实质性影响因素，K5 可能覆盖 K1 漏掉的已知有效路径。 | 该目标还是 conditional；结果不能解释为纯排序收益，因为 caller 语义不同。 |
| 语义适用性 | 11 个目标中 10 个 supported、1 个 conditional；固定成功路径差分重放 11/11 一致。 | 在固定 caller 关系、每步成功、最终属性相关状态的窄条件下，两种执行方式可重放。 | 仍有统一的 transaction atomicity caveat；不证明完整搜索过程等价。 |
| SMARTIAN 外部批次 | 2 个简单整数目标，各 30 次，共 60/60 完成并发现共同 IntegerBug oracle。 | 部署链路、日志解析和共同 oracle 在这两个目标上的可执行性。 | 不是广泛竞品排名、不是 C-2 泛化证据。 |
| Scale proxy | 当前 11 个目标约 32–79 行，retained paths 约 1–33；四个小型合成合约准备时间中位数约 1.30–1.32 秒。 | 当前方法管线和候选规模的起点描述。 | 不足以证明大型真实项目的可扩展性。 |
| matched-random | 历史控制存在 provenance/checksum reconciliation warning。 | 只能在独立重建并重新审计后考虑使用。 | 当前 matched-random-v1 保持 LEGACY_CONTROL_QUARANTINED，不得作为新主张的基础。 |

此外，Phase 01 记录了冻结 checksum 清单存在外部文件缺失和现存文件不匹配的历史警告；本阶段不修复、不刷新 checksum，也不以新的文档覆盖该警告。任何 Phase 05 复用的输入必须在新 manifest 中重新记录路径、版本和 SHA-256，并在不一致时 quarantine。

## 10. Why current evidence is not yet a full CCF-C exit

当前证据足以支撑开题、学位论文实验章节或聚焦机制的工具型短文，但还不能稳妥支撑“普遍提升真实智能合约模糊测试”的 CCF-C 类出口，主要原因是：

1. **外部有效性不足。** 正式公开任务只有 5 个，且有适配和语义筛查；数量与任务多样性不足以代表真实合约总体。
2. **新颖性边界风险高。** SMARTIAN、IR-Fuzz、MuFuzz、ConFuzzius 和 Harvey 等工作已经覆盖不同形式的数据流、交易序列、按需探索或约束引导。V1 需要用文献核查和直接比较证明组合边界，而不是继续堆同一受控合约的 seed。
3. **执行语义不完全相同。** Harness 单交易 wrapper 可能改变 caller、atomicity、rollback、区块环境、msg.value、payable、外部调用和 reentrancy。发现率差异不一定只反映顺序规划。
4. **基线广度有限。** SMARTIAN 目前只在两个简单整数目标上完成对齐批次；这可以证明链路可运行，不能证明广泛 SOTA 排名。
5. **规模证据有限。** 现有开销和候选规模主要来自小型合约，没有大型真实项目的函数数、依赖边、路径深度、生成失败率和编译开销曲线。
6. **冻结与 provenance 仍需守护。** 旧的 matched-random 控制和 checksum reconciliation warning 不能被新表格静默吸收；V1 与 V2/C2 必须继续分开。

因此当前建议是收窄论文主张、完成公开 benchmark 预登记和语义适用性记录，再决定是否进行有信息增益的正式实验，而不是把更多 seed 当成主要补强手段。
## 11. Phase 05 preregistration schema

Phase 05 的任何正式公开实验，必须在看到该批次 fuzzing 结果前冻结一份逐 benchmark_id、逐属性的 manifest。下面字段是最低要求；缺失字段不得进入正式运行。

| Field | Required content and freeze rule |
|---|---|
| benchmark_id | 稳定且唯一的任务 ID；一个合约-属性组合一行，派生 Harness 作为同一任务的关联输入，不另造一个样本。 |
| source | 原始来源名称、可复核 URL/commit 或本地来源路径；同时记录来源文件 SHA-256。来源不可确认时不得进入主分母。 |
| contract_file | Original 使用的确切 Solidity 文件；Harness 使用的生成文件另列关联路径，不能把生成物伪装成原始来源。 |
| contract_name | 编译入口中的确切合约名；多文件/多合约任务记录源码闭包和选择规则。 |
| property | 精确属性函数名、返回语义和读取状态；属性适配必须在运行前冻结。 |
| adaptation_description | 说明扁平化、Solidity pragma、属性代理、无关属性移除等所有适配；说明是否改变状态转移、caller、资金或 oracle 语义。 |
| semantic_classification | 只能为 supported、conditional 或 excluded；分类依据必须来自 fuzzing 前的静态审计和人工/差分规则。 |
| reason_for_inclusion | 说明为什么该任务满足来源、属性、编译和语义纳入条件；不能引用本批次运行结果作为理由。 |
| reason_for_exclusion | 不纳入的任务也要登记原因，例如 unsupported msg.sender/msg.value/time/reentrancy、编译失败、属性不可确认或来源不可追溯。空值必须明确写 none。 |
| original_config | Original 的完整配置路径、内容摘要和 SHA-256；至少冻结 testMode、seqLen、testLimit、timeout、workers、stopOnFail。 |
| harness_config | Harness 的完整配置路径、内容摘要和 SHA-256；明确 wrapper 的 seqLen 与 Original 不同的执行层次。 |
| k_values | 预先声明的 K 集合，例如 1,5；不得依据已知路径排名或首轮结果事后选择 K。 |
| seeds | 精确 seed 列表或可展开的范围、seed 生成规则和重复次数；smoke seed 与正式 seed 分开标记。 |
| test_limit | 每个方法组的整数预算；Original 与 Harness 若不同必须说明，不能用 Total calls 补偿解释。 |
| timeout | 每个 run 的超时和单位；超时分类、退出码和 raw log 处理规则预先固定。 |
| workers | worker 数；为公平比较应预先固定并记录实际值。 |
| stop_on_fail | 布尔值；预先固定，且说明发现反例后是否停止以及这如何影响日志。 |
| output_root | 新实验只能写 work/v1-restart/<run_id>/ 或等价隔离运行区；不得直接写冻结 results/。每个 run 要有 manifest.tsv、command.txt、environment.txt、generated/、raw/、parsed/、summary/、status/。 |
| success_definition | run-level 成功只定义为 raw log 明确出现属性反例，例如 falsified/property failed，并通过 parser 确认；不是“没有看到反例”。汇总成功率使用 falsified_runs / valid_runs。 |
| failure_definition | 明确区分 budget_exhausted（当前预算内未发现反例）、startup_error、unknown_error、incomplete 和明确 passed。除反例外，这些都不能改写为安全证明；启动/不完整运行不得静默删除。 |
| parser_script | 固定 analyzer/parse_experiment_logs.py 及其参数、版本/commit；汇总和统计也记录固定脚本，不手工改 CSV。失败 marker 必须优先于预算终止 marker。 |
| checksum_policy | 对源码、属性/配置、manifest、命令、环境、生成 JSON/Harness、raw log、parser 输出和汇总记录 SHA-256；raw log 不手工编辑；缺失或不匹配则保留原物并 quarantine，不刷新清单掩盖差异。 |

### Phase 05 的候选任务登记规则

- 先登记全部候选、纳入项和排除项，再运行任何正式 fuzzing；不得因 V1 能否成功而回头选择合同或属性。
- supported 不是自动等价证明。主比较仍需完成编译预检和固定成功路径差分重放；差分范围要写入 manifest。
- conditional 可以保留为单独的条件支持/附录案例，但只有 caller、value、环境和回滚条件被明确控制且差分通过，才可考虑进入相应的可比分层；默认不与 supported pooled。
- excluded 不进入性能分母，但必须保留来源、分类理由和失败证据。
- 已知 triggering path 可用于 preflight 和重放，但 any_known_triggering_path 不等于完整可达性证明；路径本身不能事后决定纳入规则。
- C0、smoke、启动失败、编译失败和不完整日志必须独立计数，不得静默从审计表删除。

### Run-level 状态解释

| Status | Meaning | Paper wording |
|---|---|---|
| completed + falsified marker | 在当前执行模型、预算和输入下观察到属性反例。 | “发现反例”；不能自动提升为 Original 语义等价。 |
| budget_exhausted | 没有反例 marker，且预算/时间限制明确终止。 | “在当前预算内未发现反例”；不能写成属性通过或安全。 |
| explicit passed | 工具明确报告 property passed/passing。 | 仍只是当前测试执行的结果，不能写成普遍安全证明。 |
| startup_error | 正式测试前的编译、路径、配置或环境错误。 | 单独报告；不进入 valid_runs。 |
| unknown_error / incomplete | 无法确认完成和属性结果。 | 单独报告并 quarantine；不删除、不归入成功或预算耗尽。 |

## 12. Phase 05 go / no-go conditions

### Go 条件

只有以下条件全部满足，才允许从预登记进入正式重复实验：

1. 本报告已由研究者复核，方法名称和安全主张没有夸大。
2. 相关工作表已完成原始论文/官方资料核查，并保留 SMARTIAN、IR-Fuzz、MuFuzz 的高重叠风险表述。
3. 所有候选公开任务、来源、属性、适配、编译器、supported/conditional/excluded 分类及纳入/排除理由已在 fuzzing 前冻结。
4. Original/Harness 配置、K 值、seed、testLimit、timeout、workers、stopOnFail、成功/失败分类和 parser 版本已冻结。
5. 每个纳入任务已完成编译和 Harness preflight；失败任务保留失败证据并分类，不从分母中静默删除。
6. 每个 supported 任务已完成固定成功路径的窄范围 differential replay；conditional 任务只有在明确条件满足后才能进入相应分层，默认不与 supported pooled。
7. 先完成 public benchmark preregistration + compile/preflight + 1 seed smoke；smoke 只验证入口和输出结构，不进入正式分母。
8. smoke 通过后，研究者检查 manifest.tsv、command.txt、environment.txt、生成路径/Harness、raw log、status 和 checksums，确认没有向冻结 results/ 写入文件。
9. 每个正式 run 都能被独立复核，原始日志只读保存，budget_exhausted、startup error、unknown error 和 incomplete 均保留。

### No-go 条件

出现任一情况就不得进入正式重复实验：

- 任务来源、属性或适配无法追溯，或分类是在看到 fuzzing 结果后才改变；
- Harness 生成/编译失败，或生成路径不含声明的 Top-K 候选；
- msg.sender、msg.value、payable、区块环境、外部调用、reentrancy 或 rollback 语义有高风险但没有预先声明条件和差分证据；
- 试图把 conditional 与 supported 混成一个 pooled 分母而没有共同语义条件；
- 使用 Total calls 作为等量 Original/Harness 工作量，或把 budget_exhausted 当 property passed；
- 输出目录会覆盖冻结 evidence，或 run 缺少 manifest、环境、原始日志、status/checksum 之一；
- parser、统计脚本或失败分类会手工改 raw log/CSV，或无法保留启动失败和未知失败；
- 需要依赖当前未解决 provenance 的 matched-random、V2/C2 开发结果或不可执行外部基线来填充主表。

## 13. Files changed

本阶段新增唯一文件：

    docs/v1-restart/PHASE_04_METHOD_CLAIM_AND_PREREGISTRATION.md

本阶段未修改：

- analyzer/：未修改；
- contracts/：未修改；
- configs/：未修改；
- results/formal/：未修改；
- results/formal-b2/：未修改；
- results/public-benchmarks/：未修改；
- results/paper-data/：未修改；
- paper-ready/：未修改；
- work/：本阶段未写入临时草稿或实验输出。

没有执行 commit 或 push，也没有覆盖、移动或删除冻结证据。

## 14. Recommended next phase

有条件建议进入 Phase 05，但只从以下单元开始：

1. 冻结公开 benchmark preregistration，包括全部候选、属性、适配、语义分类、预算、K、seed 规则和排除原因；
2. 在隔离 work/v1-restart/<run_id>/ 中做 compile/preflight；
3. 每个拟纳入任务先做 1 个 seed smoke；
4. 由研究者亲自复核 manifest、生成 Harness、状态分类、checksum 和语义条件；
5. 只有复核通过后，另行决定是否进行小规模重复实验，最后才考虑正式 seed 批次。

本阶段不建议直接运行 30 seed，不建议扩展 V2，不建议重跑 matched-random/SMARTIAN 或生成新的论文结果表。Phase 05 的第一步是可审计的公开任务登记和预检，而不是增加日志数量。

