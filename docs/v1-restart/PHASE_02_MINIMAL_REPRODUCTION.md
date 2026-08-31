# Phase 02 Minimal Reproduction

## Final status

**PASS WITH WARNINGS**

两次预登记运行都正常完成，Full-K1 的 Top-1 是人工确认的目标路径，生成的 Harness 调用顺序正确，且两份原始日志都显示 echidna_value_safe 被 falsify。唯一 warning 是 runner 的 status/status.env 将两次 EXIT_CODE=1 都记录为 STATUS=budget_exhausted；因此属性结果以原始日志中的 falsified 为准，状态分类不被手工改写。

本阶段没有运行其他 benchmark、没有运行 30 个 seed、没有运行 C-1/B-2/matched-random/SMARTIAN/V2，也没有修改算法、配置、runner 或冻结结果。

## Baseline

- 工作线：develop
- 开始前工作区：干净
- HEAD 与 origin/develop：均为 f9b93ef69d0cd0416909d3e7c05c74848022d074
- 方法版本：Full-v1.0-restart，基于冻结的 V1 方法线
- benchmark：contracts/benchmarks/NoisyFourStepExample.sol
- 属性：echidna_value_safe()
- seed：Original 和 Full-K1 均为 1
- 工具环境：Python 3.11.15、Slither 0.11.5、solc 0.8.20、Echidna 2.3.2

本阶段研究的问题是：在一个包含无关状态依赖的受控合约上，Original 是否需要自行探索正确的多步顺序，而 Full-K1 是否能先通过属性定向分析和值引导生成可审计的目标 Harness。

实验输出分别位于：

- work/v1-restart/phase02-noisy-original-s1/
- work/v1-restart/phase02-noisy-full-k1-s1/

这些是运行区临时输出，不属于冻结论文证据目录。

## Benchmark semantics

目标属性为：

~~~text
echidna_value_safe()  <=>  value <= 100
~~~

要违反属性，最终必须使 value > 100。唯一写入 value 的关键函数是 withdraw(uint256 x)，它要求 approved == true，然后执行 value = x。

状态推进关系是：

~~~text
register()              设置 registered = true
deposit()               要求 registered == true，设置 funded = true
approve()               要求 funded == true，设置 approved = true
withdraw(uint256 x)     要求 approved == true，设置 value = x
~~~

因此人工确认的目标路径是：

~~~text
register()
→ deposit()
→ approve()
→ withdraw(x), x > 100
~~~

六个 noise 函数为：

- noise1(uint256) 写 noiseA；
- noise2() 读 noiseA、写 noiseB；
- noise3() 读 noiseB、写 noiseC；
- noise4() 读 noiseC、写 noiseA；
- noise5(uint256) 写 noiseB；
- noise6() 读写 noiseC。

这些函数确实形成 noiseA → noiseB → noiseC 等状态读写依赖，但它们既不读取也不写入 value、registered、funded 或 approved。因此它们扩大了普通依赖搜索的候选空间，却不是使 echidna_value_safe 失败所需的状态推进链。

## Original configuration

configs/formal-original-seq4.yaml 的关键配置为：

~~~text
testMode   = property
testLimit  = 100000
seqLen     = 4
timeout    = 30
workers    = 1
stopOnFail = true
~~~

seqLen = 4 表示 Echidna 自己探索最多四笔交易组成的序列，顺序和参数都由 Echidna 的随机搜索决定。

configs/formal-harness-seq1.yaml 的关键配置为：

~~~text
testMode   = property
testLimit  = 100000
seqLen     = 1
timeout    = 30
workers    = 1
stopOnFail = true
~~~

Full-K1 的 seqLen = 1 表示 Echidna 外层调用一次 Harness wrapper；wrapper 内部已经固定调用四个目标函数。因此两个 seqLen 反映的是不同执行层次，不是完全等量的参数设置。不能直接把两次运行的 Total calls 当成相同工作量，也不能由本阶段计算 speedup。

## Original seed-1 result

运行目录：work/v1-restart/phase02-noisy-original-s1/

raw/seed-1.log 显示：

- echidna_value_safe：falsified；
- Echidna 先报告了一个很大的 withdraw 参数，随后给出缩减后的反例 withdraw(101)；
- 最终调用序列为 register() → deposit() → approve() → withdraw(101)；
- Total calls: 2137；
- 原始日志的 EXIT_CODE=1。

status/status.env 记录为 STATUS=budget_exhausted，与原始日志的属性结果不一致。这是 runner 状态分类 warning；原始日志、manifest、command、environment 和 checksum 文件均保留，没有被修改。budget_exhausted 不能解释为属性通过或合约安全；本次原始日志实际观察到了反例。

## Full-K1 pipeline

### RW extraction

generated/rw.json 给出的属性和关键读写关系为：

| 函数 | 读取 | 写入 |
|---|---|---|
| echidna_value_safe() | value | 无 |
| withdraw(uint256) | approved | value |
| approve() | funded | approved |
| deposit() | registered | funded |
| register() | 无 | registered |

属性先告诉分析器它观察 value；分析器找到写入 value 的 withdraw，再沿着 withdraw 所需的 approved、funded、registered 依赖追溯到前置函数。noise 函数的读写只发生在 noiseA、noiseB、noiseC 上，不能连接到属性读取的 value。

### Property/repeat path generation

generated/repeat-property-sequences.json 记录：

~~~text
property_functions    = ["echidna_value_safe()"]
property_variables    = ["NoisyFourStepExample.value"]
target_functions       = ["withdraw(uint256)"]
generated_path_count   = 3
retained_path_count    = 3
dfs_expansions         = 3
max_path_length        = 4
max_function_visits    = 2
~~~

本次生成并保留了三条以 withdraw(uint256) 结束的路径，长度分别为 4、3、2。排名第一的 path 是：

~~~text
register()
→ deposit()
→ approve()
→ withdraw(uint256)
~~~

它的 repeat_rank 为 1，has_repetition = false。虽然 Full pipeline 启用了 max_function_visits = 2，NoisyFourStep 的目标路径本身不需要重复调用；Repeat-aware 不是本例的主要成功原因，真正对应的后续验证对象是 RepeatedCallExample。

Property-directed 的含义不是收集所有“某函数写入的变量被另一函数读取”的边，而是从指定属性读取的状态 value 出发，保留最终可能影响该属性的状态推进路径。

### Value guidance

generated/value-constraints.json 识别出：

~~~text
register() 写 registered = true
deposit()  要求 registered == true，并写 funded = true
approve()  要求 funded == true，并写 approved = true
withdraw() 要求 approved == true，并把 value 写成参数 x
~~~

对 Top-1 路径，generated/full-sequences.json 记录：

~~~text
property_score   = 6
value_adjustment = 12
value_score      = 18
value_matches    = 3
value_conflicts  = 0
value_unknowns   = 0
~~~

三条 value edge 全部是 match：

1. register() 写 registered = true，满足 deposit() 的 require(registered)；
2. deposit() 写 funded = true，满足 approve() 的 require(funded)；
3. approve() 写 approved = true，满足 withdraw() 的 require(approved)。

更短的两条候选路径得到 value_score = 12 和 6，因此 Top-1 保持为完整四步路径。Value guidance 只利用静态可识别的简单常量写入和简单 require，标记 MATCH、CONFLICT 或 UNKNOWN；它不是完整符号执行，也没有求解所有 Solidity path constraints。withdraw(x) 中的 value = x 是动态参数写入，x > 100 仍由 Echidna 在运行时 fuzz，而不是由 value guidance 静态求解。

### Top-1 sequence

generated/full-sequences.json 的 Top-1 实际序列为：

~~~text
register()
→ deposit()
→ approve()
→ withdraw(uint256)
~~~

这与 benchmark 的人工确认路径一致。

### Generated Harness

generated/NoisyFourStepFullK1RestartHarness.sol 的关键结构是：

~~~solidity
NoisyFourStepExample public target;

constructor() {
    target = new NoisyFourStepExample();
}

function full_sequence_1(uint256 arg_1_3_0) public {
    target.register();
    target.deposit();
    target.approve();
    target.withdraw(arg_1_3_0);
}
~~~

Harness 会创建新的 NoisyFourStepExample 实例。sequence wrapper 叫 full_sequence_1，实际调用顺序正是四步目标路径。withdraw 的参数不是固定值，而是 wrapper 参数 arg_1_3_0，所以 Echidna 仍然可以 fuzz 这个参数。Harness 的 echidna_value_safe() 代理调用 target.echidna_value_safe()。

runner 已用 solc 编译该 Harness，并在其上运行 Slither 和 Echidna。

### Echidna result

运行目录：work/v1-restart/phase02-noisy-full-k1-s1/

raw/seed-1.log 显示：

- echidna_value_safe：falsified；
- Echidna 的缩减反例为 full_sequence_1(101)；
- 一次 wrapper 调用后属性查询返回 false；
- Total calls: 2；
- 原始日志的 EXIT_CODE=1。

因此 Full-K1 通过固定顺序把参数搜索集中到 withdraw(x)，并在 x = 101 时观察到属性失败。status/status.env 同样记录为 STATUS=budget_exhausted；该状态与 raw log 不一致，按 warning 保留原样。

## Original vs Full-K1

| 项目 | Original | Full-K1 |
|---|---|---|
| 输入合约 | 原合约 | 生成的 Harness |
| seqLen | 4 | 1 |
| 顺序由谁探索 | Echidna | V1 预处理器固定 Top-1 |
| 参数由谁探索 | Echidna | Echidna，仍 fuzz withdraw 参数 |
| seed | 1 | 1 |
| 属性结果（以 raw log 为准） | falsified | falsified |
| 外层调用含义 | 单笔目标函数交易 | 一次 wrapper 调用 |
| 是否可直接比较 Total calls | 否 | 否 |

Original 的 raw log 记录 Total calls: 2137，Full-K1 记录 Total calls: 2，但这些数字对应不同执行模型和计数层次。本阶段只做机制理解，不做统计检验、speedup 或 Full-K1 普遍优于 Original 的结论。

## Semantic warning

Original 通常由 Echidna 作为多笔独立交易执行：四个目标函数可以跨交易发生，调用者也可能交替。seed-1 的 Original raw log 已展示不同目标调用者地址。

Full-K1 可能表现为一次外部交易调用：

~~~text
full_sequence_1(x)
  ├─ target.register()
  ├─ target.deposit()
  ├─ target.approve()
  └─ target.withdraw(x)
~~~

在这种模型下，目标合约看到的 msg.sender、交易边界和回滚范围可能与 Original 不同；还可能影响 block.timestamp、block.number、msg.value 以及 caller alternation。wrapper 内任一步 revert 时，也可能整体回滚，而不是只回滚一笔独立交易。因此这里的成功说明 V1 在这个受控 benchmark 上生成了有效 Harness，不证明 Original 与 Harness 完全等价，也不证明真实多交易语义下已经优于 Echidna。

## What I should understand after Phase 02

### Q1：为什么 Original 在这个 benchmark 上可能比较难？

Original 要在包含四个目标函数和六个 noise 函数的调用集合中自行找到正确顺序，同时还要找到使 withdraw(x) 违反属性的参数。错误顺序会因为 require 失败，noise 路径又不会推进 value，所以随机序列空间中真正有用的序列比例较低。

### Q2：Property-directed pruning 到底解决了什么问题？

它把搜索目标从“所有可能的数据依赖”缩小为“最终可能影响指定属性读取状态的依赖路径”。本例中属性读取 value，分析器锁定写入 value 的 withdraw，再反向保留能建立 approved、funded、registered 的前置链，排除 noise 状态依赖。

### Q3：Repeat-aware 在 NoisyFourStep 中是不是主要贡献？

不是。NoisyFourStep 的目标路径只需每个关键函数调用一次，Top-1 的 has_repetition 为 false。Repeat-aware 是 Full pipeline 的组成部分，但它真正应在必须重复调用同一函数的 RepeatedCallExample 上验证。

### Q4：Value guidance 在这个案例中提供了什么额外证据？

它提供了三条可解释的正向匹配证据：registered = true 满足 deposit、funded = true 满足 approve、approved = true 满足 withdraw。因此完整路径得到三个 match、零 conflict、零 unknown，并从候选中保持为 Top-1。它没有替代运行时参数 fuzz，也没有求解一般 Solidity 约束。

### Q5：为什么 Harness 成功不能直接证明方法已经在真实多交易语义上优于 Echidna？

因为 Harness 把多步顺序封装进一个 wrapper，可能改变 msg.sender、交易边界、回滚原子性和区块/调用上下文；同时 Original 与 Harness 的 Total calls 也不是同一工作量定义。受控 benchmark 上的属性 falsification 只能证明这条生成 Harness 在当前执行模型下有效。

## Blocking issues

没有发现硬性阻塞：

- Full-K1 Top-1 正确；
- Harness 调用顺序正确；
- 两次 runner 都返回正常完成；
- manifest、command、environment、raw log、status 和 checksums 均存在；
- results/、contracts/、configs/、analyzer/、scripts/ 未修改。

需要在后续工作中处理的 warning 是 runner 状态分类：两份 status.env 都把 raw log 明确报告的 falsified 记为 budget_exhausted。本阶段没有修 runner，也没有修改任何运行证据。

## Phase 03 recommendation

**有条件推荐进入 Phase 03，但不应立即扩大实验。** 下一步应先对 runner 的 falsified/budget-exhausted 分类差异做独立核查，并保持本阶段两份原始运行不可变；核查完成后，才按 V1 工作流进入四个 Formal 主基准各 3 个 seed 的小规模回归。本报告不运行 Phase 03。
