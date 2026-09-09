# D0 Experimental Weakness Review

## 1. Scope and Review Standard

本评审面向一篇可以尝试投稿 C 会的研究论文，而不是顶会级大规模工具竞赛。评审问题是：在不扩大 PHS 的方法边界、不改写 V1 冻结证据的前提下，当前实验是否已经形成方法—实验—主张闭环；如果还不完整，最小的额外实验包是什么。

PHS 的正式定位保持为 **Property-directed Harness Synthesis**（属性定向 Harness 合成方法）：它位于 Echidna 之前，是读取显式 safety property、规划候选 transaction sequence、生成外部 Solidity Harness 的 preprocessing/synthesis 层。PHS 不修改 Echidna core，也不是新的通用智能合约模糊测试器。

本阶段只进行证据复核和实验决策，不运行 Echidna、Slither、solc、benchmark、fuzzer 或任何实验 runner，不新增 benchmark 源码，不改写已有结果，不重新执行 B4，也不使用 `results/matched-random-v1/` 支撑新 claim。

## 2. Current Evidence Inventory

### 2.1 受控机制证据

正式 V1 受控 Formal benchmark 为 NoisyFourStep、ResetExample、BranchValueExample 和 RepeatedCallExample。它们分别隔离无关路径、reset/同分候选、值方向冲突和必须重复调用的障碍。现有候选汇总显示，四个主要 Formal benchmark 的 Dependency retained paths 合计 92 条，Property retained paths 合计 31 条，减少 61 条（66.30%）。

已有受控结果可以直接支持以下范围内观察：

- NoisyFourStep 从 30 条候选降到 3 条，目标路径成为唯一 Top-1；
- BranchValue 的 Property-K1 为 0/30，Value-K1 和 Full-K1 为 30/30；
- RepeatedCall 的不允许重复配置为 0/30，完整方法为 30/30；
- ResetExample 的 reset 干扰扩大同分候选集合，值证据可进一步区分候选；
- Formal 主批次中的 Original、组件配置和 Full-K1 已有 30-seed 受控运行，B-2 还包含 AlternativePath 与 MultiProperty 扩展，但 B-2 的独立环境快照不完整，不能与主批次无条件 pooled。

这些数据是机制证据，不是对真实生态的抽样，也不能自动转化为端到端效率或安全结论。

### 2.2 Public evidence

当前 B4 supported pool 是四个 public tasks：`echidna-flags`、`echidna-multi`、`smartbugs-multifunc` 和 `smartbugs-onefunc`。`exercise2-access-control` 依赖 `msg.sender`、owner equality、caller alternation 和 address-keyed mapping，继续为 `conditional_replay_required`，不进入 supported pooled result。B1 还登记了 PUB06–PUB08，但它们是仓库内部 Formal/早期 toy，均被排除，不能冒充 public expansion。

B4 预登记并完成 4 benchmark × 3 methods × 10 seeds = 120 runs，方法为 Original、Full-K1 和 Full-K5。结果为 118 `falsified`、2 `budget_exhausted`；120/120 artifact set complete，120/120 checksum pass，parser/status mismatch、startup_error、unknown_error 和 incomplete 均为 0。两个预算耗尽运行是 `b4-echidna-multi-original-s1` 和 `b4-echidna-multi-full-k5-s7`；其含义仅为在给定预算内没有观察到反例，不是 property passed、contract safe 或漏洞不存在。

B4 的 `main_table_usable` 仍为 `conditional`。Original 的 `seqLen=4` 表示 Echidna 多交易搜索，Harness 的 `seqLen=1` 表示一次外层 wrapper 调用；两者的 caller、transaction atomicity、rollback scope、`msg.value`、block context 和外部调用边界不相同。因此 B4 是声明执行模型下的描述性比较，不是等价交易预算或 Total calls speedup 实验。

### 2.3 Provenance and boundary evidence

已有材料的强项包括预登记、expected-run registry、manifest、command、environment、raw、parsed、summary、status、checksum 和静态语义门控。B2 的 `static_gate_pass` 不是 native replay pass；固定成功路径的一致性也不是完整搜索过程等价。`results/matched-random-v1/` 仍标记为 `PROVENANCE_UNRESOLVED`、`DO_NOT_USE_FOR_NEW_CLAIMS`、`LEGACY_CONTROL_QUARANTINED`。

仓库中还保留历史 C-1 统计材料和窄范围 SMARTIAN 运行材料；它们不能改变当前 B4 的四任务 supported pool，也不能变成广泛的竞品排名。SMARTIAN 材料只覆盖两个简单整数目标，适合说明部署/解析链可执行，不足以作为第二个公平工具级 baseline。

## 3. Strengths of Current Evaluation

当前体系并不是“只有一个 toy example”：

1. **方法—机制对齐清楚。** Property、Repeat、Value 和 Top-K 各自有专门障碍，且保留了候选 JSON、rank、Harness 和原始日志，reviewer 可以追溯选择原因。
2. **存在双层评价结构。** Formal controlled benchmarks 负责回答“为什么机制可能有效”，public tasks 负责回答“流程能否在公开属性任务上运行并给出可分类结果”。这是适合小型方法论文的基本结构。
3. **B4 的执行完整性很强。** 120 个预登记运行全部完成，artifact、checksum、status 和 parser 链没有缺口，也没有把失败运行静默删除。
4. **边界主动披露。** 当前材料没有把 PHS 包装成 Echidna replacement，没有把 `budget_exhausted` 写成通过，没有用 Total calls 声称 speedup，也没有把 conditional task 或 quarantine 数据混入 supported pool。
5. **研究问题仍然可形成清晰论文叙事。** 论文可以围绕 property-directed candidate planning、可解释的 Harness synthesis、bounded repeat、lightweight value evidence 和 Top-K 保留展开，而不是假装完成了所有 fuzzing 系统的全面比较。

## 4. Experimental Weaknesses

下表区分真正可能导致 C 会 reviewer 拒稿的风险，和可以靠窄定位、措辞及限制章节控制的风险。

| 维度 | 当前判断 | C 会风险 | 写作能否充分化解 |
|---|---|---|---|
| benchmark diversity | supported public 只有 4 个，且任务规模小、模式相近；其中两个是 SmartBugs arithmetic 变体，`smartbugs-onefunc` 主要是重复单函数集成证据 | 若声称一般生态有效，风险高 | 只能部分化解；需要把 claim 限于预登记任务，并优先补高匹配任务 |
| benchmark count | 4 个 supported public contract/property 单元；Formal 是机制样本，不是生态样本 | 对“普遍优于”或泛化 claim 接近 blocker | 不能完全化解；对窄定位机制论文可通过双层设计降为高风险而非致命 |
| seed count | B4 每个 cell 10 seeds | 对描述性结果可接受，对稳定概率或统计 claim 偏弱 | 大部分可化解；不应把 10 seed 写成代表性总体 |
| baseline strength | Original Echidna 是自然且可执行的主 baseline；没有公平的多工具同模型比较 | 若写成 fuzzer ranking，风险高 | 对 preprocessing 论文可由问题定义化解；仍需干净内部 ablation |
| public vs controlled balance | Formal 机制映射好，但 public 层浅且接近饱和 | reviewer 可能认为优势只在人工场景 | 不能完全化解；需要更困难的机制匹配场景或少量新 public |
| external validity | 任务来源和语义筛查清楚，但样本不能代表真实生态 | 影响论文外部结论，可能成为拒稿主因 | 只能通过窄 claim、limitations 和 B5 新任务缓解 |
| semantic validity | wrapper 与 Original 存在 caller、原子性、回滚、value、区块和 external-call 差异；B2 仍是 static gate only | 若将两者当成等价执行模型，属于严重/近 critical 风险 | 对 supported 非 caller-sensitive 任务可由 scope 化解；对 access-control 任务需要 conditional replay 或排除 |
| metric richness | 当前主 B4 主要是 falsified/budget 状态和 provenance；大部分任务 10/10，成功率有 ceiling effect | 只用 success rate 很难证明 PHS 的增益 | 不能只靠写作；需要 rank、reachability、time 或 hard-scenario 指标 |
| ablation/mechanism evidence | 已有 Formal 组件对照，但不是统一的新一轮 factorial ablation，且缺少一组机制指标闭环 | reviewer 可能问“到底是哪一层产生效果” | 不能完全化解；轻量 ablation 是高 ROI 补强 |
| statistical evidence | B4 是 10-seed descriptive comparison；不支持显著性或 pooled inference | 对 descriptive C 会短文可接受，对普遍优越性不够 | 可以通过不做统计 claim 化解；不应为形式显著性机械扩 seed |
| reproducibility/provenance | 120/120 完整且 checksum pass，预登记和 semantic boundary 文档齐全 | 不是主要拒稿风险 | 主要可通过写作、附录和 artifact package 展示 |
| novelty-to-experiment fit | 组合式 property-directed preprocessing、external Harness 和可解释 Top-K 有清楚定位，但 public tasks 没有覆盖所有困难 | reviewer 可能认为贡献只是工程 glue | 需要把 controlled 机制作为核心实验，并补 rank/reachability 指标；不必全面复现所有 fuzzer |

### 4.1 高风险但当前可控的两个因素

第一，`118/120` 的 falsified 数量看起来很强，但也意味着最终 falsification rate 几乎没有区分度。三组任务全部为 10/10，差异集中在 `echidna-multi` 的两个 budget observations。这里的高比例不是 PHS 普遍优越性的证据，反而提示 ceiling effect：论文主指标不能只写最终是否 falsified。

第二，Harness 语义差异并不是一个可以用 checksum 消除的工程问题。checksum 只说明文件没有被改写；它不能证明 wrapper 和 Original 的 caller、transaction atomicity 或 rollback scope 相同。该边界必须在结果、图表、表注和 threats 中保持一致。

## 5. Weaknesses Addressable by Writing

以下弱点不需要大规模新实验，前提是论文严格收窄：

- 明确 PHS 是 Echidna 前的 external preprocessing/Harness synthesis，不是新的通用 fuzzer，因此不强求与 SMARTIAN、MuFuzz、IR-Fuzz、Harvey、ConFuzzius、SmarTest 全部做工具级横评；
- 将 Formal benchmark 明确命名为 controlled/custom/synthetic mechanism evaluation，解释每个场景隔离的障碍，不把它们写成真实生态样本；
- 将四个 public task 写成“预登记、已筛查任务上的范围内描述性证据”，不写成真实合约总体；
- 继续将 `exercise2-access-control` 保持 conditional，将 B2 `static_gate_only` 与 native replay 区分；
- 说明 Original 与 Harness 不是完全等价执行模型，禁止 Total calls speedup、等量工作和跨模型安全结论；
- 说明 `budget_exhausted` 只是预算内未观察到反例，observed falsification rate 只是 task/config/seed 范围内的描述性比率；
- 把 SMARTIAN、MuFuzz、IR-Fuzz 等放在 Related Work/conceptual positioning，不能把已有窄 SMARTIAN 材料写成广泛第二 baseline；
- 把 provenance completeness 解释为可追溯性，而不是合约安全、独立复现或语义等价证明。

这些写作措施可以把“证据有限”变成诚实的研究范围，但不能让四个 public task 变成更多任务，也不能凭措辞创造效率或统计证据。

## 6. Weaknesses Requiring Experiments

### A. 必须补

1. **机制与指标的闭环。** 至少要有一组困难场景使最终 falsification 不再全部饱和，并记录 target-state reachability、target candidate rank、Top-K hit、必要 repeat 是否被保留和 time-to-falsify。否则 PHS 的实际优势只能停留在静态路径数量。
2. **轻量组件 ablation。** 用 Original 作为外部执行 baseline，并在相同 controlled/custom 场景中比较 Full PHS 与去掉 Property、Repeat、Value 的组件版本；Top-1/Top-K 作为排序敏感性。已有 Formal 组件材料可作为起点，但 B5 应固定一套可读的 ablation 口径，而不是把历史不同预算的表格直接拼接。
3. **语义门控的处理。** supported public task 仍可以保持当前范围；任何想让 caller-sensitive 任务进入论文结果的计划，都必须先做 caller-controlled same-caller/alternating-caller replay。否则继续排除或单列 conditional，不能用普通 Harness 成功替代。

### B. 强烈建议补

- 在独立来源、属性和适配可追溯、且 wrapper 语义风险低的前提下新增 2 个 public benchmark；
- 将至少一个新场景做成更深的状态依赖或更高的无关状态噪声，而不只是增加同一 toy 的 seed；
- 对最核心的 hard-scenario 结果做按 task 分层的描述性不确定性报告；若使用 time-to-falsify，保留 budget exhaustion 作为 right-censored observation；
- 记录预处理、候选生成和 Harness 编译开销，但把它们作为 overhead/engineering secondary metric，不写成跨执行模型 speedup；
- 若找到真正可复现、oracle 和 caller 模型可对齐的轻量外部工具，再单独预登记一项第二 baseline；当前不以此为 B5 前置条件。

### C. 可通过写作化解

- 不做全面 SOTA 竞品表；
- 不把 10 seeds 解释成真实总体；
- 不把 controlled scenario 解释成 real-world benchmark；
- 不把四个 public task 解释成生态代表；
- 不报告跨 Original/Harness 的 Total calls speedup；
- 不把 `budget_exhausted`、checksum pass、static gate pass 写成安全或 replay proof。

### D. 不值得补

- 现在把所有 B4 cell 从 10 扩到 30；
- 为了 baseline 数量强行复现 SMARTIAN、MuFuzz、IR-Fuzz、Harvey、ConFuzzius 或 SmarTest；
- 继续增加与 NoisyFourStep、BranchValue、RepeatedCall、ResetExample 同构、没有新机制信息的 synthetic contract；
- 将 `matched-random-v1` 解冻、重算或写入新的论文 claim；
- 为了“填满 public 数量”把 PUB06–PUB08 或任何内部 Formal toy 改名为 public benchmark；
- 用复杂符号执行、语言模型或大规模生态 crawling 替换 PHS 当前清楚而窄的 value evidence 问题。

## 7. Seed Expansion Assessment

### 7.1 10 → 30 seeds 增加了什么

它可以更精细地描述同一 benchmark/property/config 在不同随机种子下的波动，减少单个 cell 由少数 seed 主导的偶然性，并在任务本身存在明显 success-rate 差异时改善区间宽度。它不能证明方法对新的合约类型有效，也不能修复 semantic mismatch。

### 7.2 它解决不了什么

- 不能解决只有 4 个 supported public benchmark 的 diversity/count 问题；
- 不能解决 Original 之外缺少公平外部工具 baseline 的问题；
- 不能把 controlled scenario 变成真实生态样本；
- 不能解决 wrapper 与 Original 的 caller、atomicity、rollback 或 value 语义差异；
- 不能解决 `118/120` 带来的 ceiling effect，也不能自动产生 target rank、Top-K hit 或 candidate-reduction 之外的新机制证据；
- 不能让 10 个 seed 变成 30 个独立合约。

### 7.3 ROI 判断

当前 B4 扩成全量 30 seeds 将增加 240 个运行，但仍只覆盖同一批 4 个 public task。相同计算预算用于 2 个高匹配 public task，或 3 个能产生非饱和指标的 controlled/custom scenario，并配一个轻量 ablation，能同时降低 diversity、metric 和 mechanism-attribution 风险。因此当前决定是：

**30-seed expansion：暂不推荐。**

只有在 B5 完成后，某个核心 task 的关键结果仍对 seed 高度敏感，或需要为一个已经选定的主结果补充窄范围 uncertainty，才对最核心的 1–2 个 task/method cell 条件性追加 seed；不做全量 10→30。

## 8. Public Benchmark Expansion Assessment

### 8.1 价值比较

新增 2–4 个真正独立 public benchmark 对 reviewer perception 的提升通常高于同一任务追加 seed，因为它直接增加 contract/property/source diversity，并能测试 PHS 在不同状态依赖深度、sequence length、repeat、require/value pattern 下是否仍可用。它也比新造一个与现有 Formal 同构的 toy 更能改善 external validity。

但当前 B1 仓库扫描没有发现可诚实纳入的新增 public source：PUB06–PUB08 都是内部 Formal/早期 toy，必须排除。因此 public expansion 在 D0 不是“看到数量就纳入”，而是一个有独立 acquisition、license/source、property、compiler、adaptation 和 semantic gate 的条件性路线。

### 8.2 理想新增 benchmark 的筛选条件

最理想的新增任务应满足：

1. 有可固定的独立 public origin、许可证和源码闭包，不是本仓库变体；
2. 有原作者 property 或可由公开来源审计的可信 property；
3. 至少需要两步状态操作，最好具有 3–6 步依赖深度或明显的无关写入噪声；
4. 至少覆盖一种当前 public pool 尚未充分覆盖的 pattern：深层 require/value gate、重复 transition、多个结构相近但值方向不同的候选、或不同的状态读写拓扑；
5. 不依赖当前 wrapper 无法表达的 sender alternation、逐步 `msg.value`、时间/区块推进、external call/reentrancy 或失败后跨交易状态，除非另有预登记的语义适配；
6. 可以固定 known path/target goal、编译器、配置、K、成功定义和失败分类，并保存适配是否改变状态转移的逐项说明；
7. 不根据 PHS 结果事后决定纳入，且失败、编译失败和不兼容任务都保留在筛选审计中。

结论是：**public benchmark expansion 有高价值，但对当前仓库状态是 CONDITIONAL；若独立筛查无法找到合适任务，不应为数量而纳入。**

## 9. Controlled/Custom Scenario Assessment

### 9.1 是否应该补自定义场景

应该。PHS 的贡献问题本来就是 property-directed preprocessing 如何解决特定的 sequence-planning obstacle；为隔离该机制而设计 controlled/custom/synthetic scenario 在方法论上是合法的。关键是把它们诚实标为 controlled scenario，不将其写成 real-world benchmark。

当前四个 Formal benchmark 已经提供第一层机制证据，但它们相对小且容易饱和。B5 最值得补的是“更深/更难/可测量”的场景，而不是继续复制同一四个设计。建议设计 3 个必选新 scenario，或在时间充足时增加第 4 个：

| 场景 | PHS 障碍 | 应记录的 mechanism metrics |
|---|---|---|
| C1 Irrelevant-State Explosion | 多个可写无关状态、reset/poison 干扰，但 property 只依赖一条深链 | relevant candidate ratio、irrelevant candidate reduction、target rank、target-state reachability |
| C2 Deep Repeated Transition | `prepare -> increment × N -> unlock -> trigger`，N 大于 1 且有明确上限 | repeat count coverage、target sequence rank、hard-budget falsification、time-to-falsify |
| C3 Value-Gated Competing Paths | 多条结构相近路径，只有特定 threshold/value 方向可以推进 | no-value vs value-evidence rank、Top-K hit、successful trigger rate、time-to-falsify |
| C4 optional Noise + Repeat + Value | 将三个小机制组合到一个更长但仍可审计的场景 | component interaction、rank stability、seed-to-seed stability |

### 9.2 核心实验还是附录

建议把 C1–C3 作为论文核心 mechanism evaluation 的一部分，而不是全部塞进附录。主文用一个矩阵说明每个场景隔离的问题、比较配置和主指标；完整候选 JSON、路径列表、逐 seed 日志和额外 ablation 放附录或 artifact package。这样能形成清楚的双层叙事：

~~~text
Layer 1: controlled mechanism evaluation
    -> 为什么 Property / Repeat / Value / Top-K 能解决声明的障碍
Layer 2: public benchmark evaluation
    -> 这种 preprocessing 在少量预登记公开任务上能否运行并产生范围内观察
~~~

这比单纯追求大量 public benchmark 更适合当前 PHS 的贡献形态；但 Layer 1 不能替代 Layer 2，Layer 2 也不能把 Layer 1 的人工控制条件隐藏掉。

## 10. Baseline Assessment

### 10.1 Main empirical baseline

当前最适合 PHS 的主实证 baseline 是 **Original Echidna**。理由是它直接回答 PHS 的真实问题：在同一属性测试框架下，加入 PHS 这一外部 preprocessing/Harness synthesis 层后，观察结果是否改变。它是当前能重复执行、输入和 oracle 可说明、工程依赖最少且不需要伪造新工具结果的 baseline。

Full-K1 和 Full-K5 是 PHS 的配置/敏感性比较，不是独立 baseline。它们可以显示 Top-K 选择的影响，但不能替代 Original。

### 10.2 Lightweight internal ablation

B5 应优先增加轻量内部消融，而不是强行复现完整外部 fuzzer。推荐固定为：

- Original Echidna；
- `Property-only` 或 dependency-without-property-filter，用于隔离属性过滤；
- `Full PHS without bounded repeat`，用于隔离 Repeat；
- `Full PHS without value evidence`，用于隔离 Value；
- Full PHS-K1 与 Full PHS-K5，用于隔离 Top-K 截断。

如果实现口径只能稳定提供其中三项，应优先保留 `-Repeat`、`-Value` 和 Full，另以现有 Property/Dependency 路径表补充 Property 证据。所谓 simple/unfiltered harness 只能作为明确命名的 dependency-only control，不能被包装成独立 fuzzer baseline。

### 10.3 Literature positioning baselines

SMARTIAN、MuFuzz、IR-Fuzz、Harvey、ConFuzzius 和 SmarTest 适合放在 Related Work 和 conceptual positioning。只有当某个实现公开、环境可控、property oracle、caller model、sequence budget 和结果定义可以公平对齐时，才值得成为 B5 的 executable second baseline。当前仓库没有这样的完整基础；已有 SMARTIAN 两个简单整数目标不足以支持工具级排名。因此 B5 默认**不**把第二 external baseline 设为 required。

## 11. Metric Assessment

### 11.1 Primary metrics

B5 最值得作为论文主结果维度的是：

1. **Target candidate rank / Top-K hit。** 对有 known target path 的 controlled scenario，报告目标路径 rank、是否进入 K1/K5 和按 seed 的 hit rate；这是 PHS 直接控制的对象。
2. **Target-state reachability。** 用预先定义的状态前缀或 successful skeleton 判断目标状态是否在预算内可达，不把任意 wrapper 调用数量当作达成。
3. **Hard-scenario time-to-falsify 或 fixed-budget trigger success。** 在困难、非饱和场景上报告事件时间和右删失；明确这是各自执行模型下的 operational observation，不是自动等价的算法 speedup。
4. **Seed-to-seed stability。** 按 benchmark 分层报告 Top-K hit、reachability 和 observed trigger success 的波动；它用于稳定性描述，不自动成为 pooled 显著性结论。

### 11.2 Secondary metrics

- observed falsification rate，尤其是有预算耗尽且不饱和的任务；
- candidate count and reduction，明确它是静态候选空间指标；
- sequence length、required repeat count、Top-K candidate count；
- preprocessing、candidate generation 和 Harness compilation overhead；
- artifact completeness、checksum pass、parser/status agreement，作为 reproducibility/provenance 指标。

### 11.3 Mechanism-only metrics

- relevant candidate ratio 与 irrelevant candidate reduction；
- value-guided rank improvement 和 value conflict resolution；
- repeated-call coverage / repeat count coverage；
- Top-K contains target sequence；
- candidate rank before/after Property、Repeat、Value；
- controlled path reachability under an explicitly declared skeleton。

### 11.4 当前不能安全使用的指标或解释

- Original 与 Harness `Total calls` 的差值不能直接叫 speedup；
- `budget_exhausted` 不能作为 property passed、safe 或 vulnerability absent；
- 120-run pooled falsification rate 不能作为真实生态概率；
- 118/120 不能转写为显著优越性，尤其不能忽略 10/10 ceiling effect；
- 只有成功样本的平均时间不能替代包含 right censoring 的 time-to-falsify；
- checksum、artifact completeness 和 static gate 不能作为安全或 semantic equivalence 指标；
- 不应在当前证据上做“普遍优于 SMARTIAN/MuFuzz/IR-Fuzz”等工具级 claim。

## 12. Minimum Viable C-venue Path

最短可行路线不是全量扩 seed，而是用一个小型 B5 填补“机制归因 + 非饱和指标”缺口：

1. **保留现有 B4。** 不改 120-run、四个 supported task、现有 raw log、summary、checksum 或 main-table flag。
2. **新增 3 个 controlled/custom scenario**：C1 Irrelevant-State Explosion、C2 Deep Repeated Transition、C3 Value-Gated Competing Paths。它们必须独立预登记为 controlled/custom，不得与 public pooled，也不得修改已有 benchmark 来制造优势。
3. **增加轻量 ablation。** 至少比较 Original、Full、`-Repeat`、`-Value`，并在竞争路径场景比较 K1/K5；若 Property-only 的实现和输入口径稳定，再加入 `-Property`。所有配置共享预先声明的场景、预算、seed 和成功定义。
4. **使用机制指标作为主轴。** 固定报告 rank/Top-K hit、target-state reachability、hard-scenario trigger success 或 time-to-falsify、seed stability；候选压缩和 preprocessing overhead 为辅助指标。
5. **推荐 seed 为 10/每个新 scenario×method cell。** 这足以形成可审计的短期比较；不把当前 B4 全量扩到 30。若新场景仍全部饱和，应停止扩 seed，先修正问题设计和指标，而不是堆更多重复运行。
6. **维持 Original Echidna 为主实证 baseline。** 不把外部工具复现设为 B5 前置条件。

完成这一路线后，论文可以安全地声称：PHS 的组合机制在预先设计的、比现有 Formal 更困难的受控状态序列障碍上产生可解释的候选排序/保留和范围内的触发观察；并且在四个已登记 supported public tasks 上能够完成可审计的描述性运行。它仍不能声称真实生态普遍泛化、与 Original 完全语义等价、等量工作 speedup、普遍优于外部 fuzzer 或合约安全。

## 13. Stronger C-venue Path

稍强但仍短期可完成的路线为 B5-Min 加以下内容：

1. 从独立公开来源新增 2 个通过 source/property/license/compiler/semantic gate 的 public benchmark；若筛查失败，保留失败记录并不以内部 toy 替代。
2. 让新增 public task 覆盖不同的 state dependency depth、require/value pattern、repeat behavior 或更大但可审计的 source size；每个新 task 使用 10 seeds，采用与 B4 相同的状态定义和 provenance 协议。
3. 对 `exercise2-access-control` 做独立 caller-controlled same-caller/alternating-caller replay appendix；无论结果如何，它都不自动进入 supported pooled result。
4. 只对 B5 中最核心、最不饱和的 1–2 个 task/method cell 做窄范围追加 seed 或 confidence/uncertainty 描述；不做全量 30-seed expansion。
5. 只有在存在真正公平且低成本的实现时，才加入一个第二 executable baseline；否则把 SMARTIAN 等保留为 literature positioning。

这条路线额外降低 public diversity、caller semantics 和核心结果稳定性三类风险，但不会把论文变成大规模生态 benchmark study。

## 14. Overall Reviewer-style Judgment

当前材料已经构成一篇 C 会论文的可靠基础：方法定位清楚，受控机制有对应证据，B4 有完整的 120-run provenance，语义限制也被主动记录。但在只使用当前 B4 的情况下，论文仍有三个关键缺口：public diversity 偏窄、falsification rate 明显饱和、组件贡献和目标路径指标尚未形成统一的主结果闭环。

因此，当前评价**可以支撑一次窄定位投稿尝试，但还不足以形成风险可接受的 regular C-venue submission package**。建议启动一个范围受控的 B5；完成 B5-Min 后，可以形成更完整、可信且不夸大的 C 会实验包。B5 的目标是补齐审稿人最可能攻击的证据，而不是把实验扩展为顶会规模。
