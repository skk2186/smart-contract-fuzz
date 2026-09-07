# 大阶段 B1：Public Benchmark Native Replay Preparation

## 1. 阶段定位

本文件是大阶段 B1 的 native replay 准备登记，不是 replay 结果，也不是新的 fuzzing 实验。

native replay 的目的，是对已经登记的 public benchmark 做逐任务、固定序列的语义边界确认：在可控制的调用者、参数、交易边界和新部署状态下，记录 Original 多交易模型与 Harness wrapper 模型对属性相关最终状态的关系。

本阶段只登记 replay 目标、必要条件和进入门槛。它不运行 Echidna、Slither 或 solc，不产生 10-seed/30-seed 结果，不修改 `results/` 或历史 quarantine 数据。

## 2. 为什么 native replay 不是新的 fuzzing 实验

native replay 只重放预先声明的已知路径或目标序列，输入是固定的 benchmark、调用顺序、caller schedule 和参数约束，输出是逐步调用成功状态、最终属性相关状态以及 Original/Harness 的差异记录。它不从随机 seed 估计发现率、发现时间或排名，也不用于挑选有利结果。

因此 replay 不能：

- 事后改变 Phase 05/06A 的 supported、conditional 或 pilot_only 分类；
- 把 Harness 的 `falsified` 自动解释为 Original 多交易语义下等价的反例；
- 把 `budget_exhausted` 写成 property passed、contract safe 或无漏洞证明；
- 将 replay 记录提升为正式主结果表。

## 3. 必须保持的执行语义边界

Original 是 Echidna 生成的多笔独立目标交易；当前 Harness 是一次外层 wrapper 调用中连续调用多个目标函数。因此 replay 必须同时记录：

- `msg.sender` 与是否需要 caller alternation；
- 每一步是否为独立交易；
- 某一步 revert 时的回滚范围；
- 参数值、`msg.value`/payable 条件（如有）；
- `block.timestamp`、`block.number` 或其他环境依赖（如有）；
- external call、delegatecall、reentrancy 和多合约状态（如有）；
- 属性相关状态的最终值和属性结果。

同一 caller、每一步成功、无环境变化依赖的固定路径，只能支持窄范围的 replay 一致性。它不能证明两种搜索过程、交易预算或调用次数完全等价。

## 4. 逐任务登记

| benchmark | current_classification | replay_priority | replay_goal | known_path_or_target_sequence | caller_requirement | value_requirement | block_or_time_requirement | external_call_requirement | rollback_requirement | expected_output | main_table_gate | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `echidna-flags` | supported | P0-required | 确认依赖 `flag0` 的两步状态转移在固定成功路径上保持属性相关最终结果 | `set0(100*k) -> set1(10*m)`，其中第一步使 `flag0=false`，第二步使 `flag1=false` | 同一 caller 足够；不需要 alternation | 需要满足函数参数的整除条件；不是 `msg.value` | 无已知要求 | 无已知 external call | 两步都应成功；记录 wrapper 整体回滚边界 | 两种模型的 `flag0/flag1` 与 `echidna_sometimesfalse` 最终结果；逐步成功记录 | replay 一致、输入约束和 checksum 经人工复核后，才可考虑 supported main table | 仍保留 Harness 单交易 wrapper caveat |
| `echidna-multi` | supported | P0-required | 确认 `state1 -> state2 -> state3` 的三步 require 链在 native 多交易与 wrapper 固定路径之间可重放 | `f(12) -> g(8) -> h(z)` | 同一 caller 足够；不需要 alternation | `f` 和 `g` 有精确参数要求；`h` 的参数不影响目标状态 | 无已知要求 | 无已知 external call | 三步均成功；任一步失败时分别记录多交易与 wrapper 的回滚范围 | `state1/2/3` 和 `echidna_state3` 的最终结果，以及每步成功/失败 | replay 一致并完成任务级人工复核后，才可考虑 supported main table | `budget_exhausted` 仍只表示给定预算内未观察到反例 |
| `smartbugs-multifunc` | supported | P0-required | 确认 Solidity 0.4.x unchecked arithmetic 下的初始化与重复 `run` 访问在两个执行模型中的属性相关结果 | `init() -> run(a) -> run(b)`，第二次 `run` 选择会使 `count` 下溢的输入 | 同一 caller 足够；不需要 alternation | 需要记录 `a`、`b` 与当前 `count` 的关系；不是 `msg.value` | 无已知要求 | 无已知 external call | 每一步调用结果、0.4.x 算术行为和整体回滚范围必须记录 | `initialized`、`count` 和 `echidna_count_does_not_underflow` 的最终结果；编译器版本 | replay 一致、0.4.23/0.4.25 适配说明和人工复核完成后，才可考虑 supported main table | 适配源码只增加属性；不能把该任务泛化为真实生态代表 |
| `smartbugs-onefunc` | supported | P0-required | 确认同一函数的首次初始化调用与第二次下溢触发调用在 native replay 中可重放 | `run(a) -> run(b)`，第一次建立 initialized，第二次选择会使 `count` 下溢的输入 | 同一 caller 足够；不需要 alternation | 需要记录两次输入与 `count` 的关系；不是 `msg.value` | 无已知要求 | 无已知 external call | 两次调用结果、0.4.x 算术行为和整体回滚范围必须记录 | `initialized`、`count` 和 `echidna_count_does_not_underflow` 的最终结果；编译器版本 | replay 一致、适配说明和人工复核完成后，才可考虑 supported main table | 主要验证 public integration 和 runner 链，不单独支持多交易优势结论 |
| `exercise2-access-control` | conditional | P0-conditional | 明确 caller 一致与 caller alternation 对 `Owner() -> resume()` 的影响，避免把 Harness 固定 caller 当作 Original 等价 | `Owner() -> resume()`；要求 `Owner` 与 `resume` 使用同一 caller 才能完成目标路径 | **必须 caller-controlled**；至少重放 same-caller 与 alternating-caller 两种 schedule | 无已知 `msg.value`/payable 要求 | 无已知要求 | 无已知 external call；导入闭包仍需记录 | `resume` 失败、wrapper 整体回滚和 Original 单步失败范围都要分别记录 | same-caller 下的状态/属性结果、alternation 下的差异、失败和回滚记录 | replay 前后都不得进入 supported pooled main table；除非未来有明确、预登记的 caller 模型扩展 | 继续保留 `msg.sender`、address-keyed mapping 和 caller alternation 边界 |

## 5. replay 输出与进入门槛

后续 B2 replay manifest 至少应记录：`benchmark`、源码路径和 SHA-256、属性、已知序列、每一步参数、caller schedule、交易边界、compiler、执行模型、逐步状态、最终属性结果、revert/rollback 结果、开始/结束时间和人工复核结论。

四个 supported 任务只有在固定路径 replay 一致、任务级语义风险复核完成且没有新增不支持特征后，才可由研究者决定是否进入 B2 的 10-seed main-run preparation。exercise2 必须以 caller-controlled replay 单独报告，不能因为 replay 或 K5 smoke 结果升级为 supported pooled。

B1 结束时不授权直接运行 10 seed。B2 仍须先锁定独立 run 目录、manifest、配置、seed、预算、失败分类和排除规则；任何正式运行都不能写入冻结 `results/`。

## 6. 结论边界

本登记支持的是“哪些 public 任务需要什么语义复核，以及何时可以考虑进入下一阶段”。它不支持 Original 与 Harness 完全等价、不支持等量调用预算或 speedup，也不产生新的反例发现率结论。
