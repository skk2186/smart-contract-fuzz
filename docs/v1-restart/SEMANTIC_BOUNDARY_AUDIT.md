# Harness / Original Semantic Boundary Audit

## 1. 审计目的

本审计记录 V1 外部 Solidity Harness 与 Original Echidna 多交易执行模型之间的语义边界，并为 public benchmark 的 supported/conditional 分类提供可追溯依据。审计不是新的 fuzzing 实验，也不把 pilot 的 falsified 结果解释成语义等价证明。

审计依据包括：

- `docs/v1-restart/PHASE_04_METHOD_CLAIM_AND_PREREGISTRATION.md`；
- `docs/v1-restart/PHASE_05_PUBLIC_PREREGISTRATION_AND_SMOKE.md`；
- `docs/v1-restart/phase05-public-preregistration.tsv`；
- 5 个 public benchmark 的源码及 exercise2 的 `token.sol` 导入闭包；
- `docs/v1-restart/PHASE_06A_PUBLIC_SUPPORTED_3SEED_PILOT.md`；
- Phase 06A work 目录中的 preflight、生成 Harness、raw log、parser、status 和 checksum。

本阶段的结论是静态源码/manifest 审计加已有窄范围证据的整理。若要将某个 public benchmark 的运行结果放入正式主表，仍应完成该任务的 native replay 或等强度的语义差分复核。

## 2. Harness execution model

当前生成器为目标合约创建一个新实例，并把候选路径写入外部 Harness 的 public wrapper。Echidna 对 Harness 的一次外层调用可以触发 wrapper 内连续的多个目标函数调用；K1/K5 代表写入 Harness 的候选路径数量，而不是 Original 的等价交易序列长度。

在该模型中：

- wrapper 内目标调用通常由同一个 Harness 地址发起；
- 候选函数顺序在生成阶段固定，Echidna 主要继续 fuzz wrapper 参数和属性；
- 当前生成器没有通用的逐步 `msg.value` 建模，也不能在 wrapper 内自动模拟不同 sender；
- wrapper 内某一步 revert 可能使整个外层调用回滚；
- 目标函数调用数量被折叠在 wrapper 的一次外层调用中；
- constructor、部署者、初始余额和区块环境仍可能影响目标状态。

因此，Harness 的 falsified 的准确含义是：在当前 Harness wrapper 执行模型、给定输入和预算内观察到了属性反例。

## 3. Original execution model

Original 由 Echidna 对目标合约进行多笔独立交易探索。序列中的每个函数调用通常有自己的交易边界，sender 可能变化；某笔交易失败时，通常只回滚该笔交易，之前已提交的交易状态保留。每笔交易的 `msg.value`、调用者、区块上下文以及外部交互时机也可能不同。

因此，Original 的 falsified 表示在其多交易执行模型下观察到了属性反例。它不能仅凭日志与 Harness 结果做完全等价推断。

## 4. 差异清单

| 语义因素 | Original | Harness | 主要风险 |
|---|---|---|---|
| `msg.sender` / caller alternation | 不同外层交易可能由不同 sender 发起，调用者可以交替 | wrapper 内目标调用通常看到同一个 Harness sender | access control、owner 和 address-keyed state 可能改变 |
| transaction atomicity | 每个函数调用有独立交易边界 | 多个函数调用合并在一次 wrapper 交易中 | 跨交易提交/观察逻辑可能改变 |
| rollback scope | 某一步失败通常只回滚当前交易 | 某一步失败可能回滚整个 wrapper | 失败前缀和已提交中间状态可能不同 |
| `msg.value` / payable | 每笔交易可有独立 value | 当前生成器不提供通用逐步 value 语义 | 资金流和 payable 分支不可默认对齐 |
| `block.timestamp` / `block.number` | 交易间区块环境可能变化 | wrapper 内调用共享一次外层交易环境 | 时间锁、区块间隔逻辑可能改变 |
| external calls / reentrancy | 每笔交易中的调用栈和回调时机独立 | 外部调用嵌套在 wrapper 调用栈中 | 回调、重入和整体回滚边界可能改变 |
| `Total calls` | 主要反映 Echidna 外层目标交易/调用层次 | 主要反映 wrapper 外层调用，内部目标调用被折叠 | 不能用差值直接声称 speedup 或等量工作 |

## 5. 分类原则

### supported

只有在源码闭包未检出 caller、`msg.value`/payable、区块环境、外部调用/重入或 address-keyed 状态等高风险依赖，并且目标路径中每一步可以在声明条件下成功执行时，才可暂列 supported。supported 的含义是“在静态筛查和窄范围成功路径复核条件下可纳入”，不是完整语义等价证明。

### conditional

如果结果依赖固定 caller、sender alternation、mapping key、constructor/deployer、失败后状态保留、value 或其他环境条件，则保留 conditional。conditional 任务可以作为单独案例报告，但默认不得与 supported 任务 pooled。

### excluded

若当前 Harness 无法表达关键语义，或 native replay/差分复核不能确认目标状态转移，任务应 excluded，不得为了填充分母而纳入。编译失败、来源不可追溯、属性结果无法确认和不完整运行也应单独保留并 quarantine。

## 6. Public benchmark 逐任务审计表

表中的“can enter main table”表示语义分类下的潜在纳入资格；Phase 06A 本身仍是 `pilot_only`，不直接写入正式主表。“needs native replay”表示在正式主表使用该任务前的必要复核，不代表本阶段要启动新实验。

| benchmark | classification | property | target sequence / intended path | caller-sensitive? | address-keyed mapping? | msg.value/payable-sensitive? | timestamp/block-sensitive? | external-call/reentrancy-sensitive? | rollback/atomicity-sensitive? | Harness risk level | can enter main table? | needs native replay? | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `echidna-flags` | supported | `echidna_sometimesfalse` | `set0(int256)` with `val % 100 == 0` -> `set1(int256)` with `val % 10 == 0` | no | no | no | no | no | low; target path functions do not revert under intended inputs | yes, after task-level replay and formal preregistration | yes | Adapted source preserves `flag0/flag1` transition and removes unrelated framework properties; Phase 06A only establishes pilot pipeline completion. |
| `echidna-multi` | supported | `echidna_state3` | `f(uint)` with `x=12` -> `g(uint)` with `y=8` -> `h(uint)` with valid `z` | no | no | no | no | no | medium; `require` guards make valid successful prefix material | yes, after task-level replay and formal preregistration | yes | Original seed 1 is `budget_exhausted`; this means no observed counterexample within budget, not property passed or contract safe. |
| `smartbugs-multifunc` | supported | `echidna_count_does_not_underflow` | `init()` -> `run(uint256)` -> `run(uint256)`; the second run with `input > 1` exercises the unchecked 0.4.x decrement | no | no | no | no | no | low; intended path has no caller/value/time/external dependency | yes, as a bounded arithmetic/integration row | yes | The K1 preflight retains the repeated `run` path; do not infer broad real-world generalization from the adapted small source. |
| `smartbugs-onefunc` | supported | `echidna_count_does_not_underflow` | first `run(uint256)` initializes, second `run(uint256)` with `input > 1` decrements/underflows | no | no | no | no | no | low; no caller/value/time/external dependency | yes, as integration evidence only | yes | The path is a repeated single-function trigger; it mainly validates public runner and property integration, not a general multi-transaction ordering advantage. |
| `exercise2-access-control` | conditional | `echidna_no_transfer` | `Owner()` -> `resume()` under a fixed caller condition; `resume()` can unset pause | yes: `msg.sender`, owner equality, possible caller alternation | yes: imported `Token` closure declares `mapping(address => uint256) balances` | no | no | no | high; `onlyOwner` revert and wrapper-wide rollback differ from independent transactions | no for supported pooled main table; separate conditional appendix only | yes, mandatory caller-controlled native replay | Must remain conditional because of `msg.sender`, address-keyed mapping, and caller alternation. Harness fixes calls to the Harness address while Original may alternate senders. |

### 6.1 Classification decision

当前维持 4 个 supported、1 个 conditional，与 Phase 05 preregistration 和 Phase 06A pilot scope 一致。没有因为 3-seed 结果改变分类，也没有把 `exercise2-access-control` 放入 supported pooled 主表。

## 7. 对论文写法的限制

推荐写法：

> V1 在经过静态语义筛查、固定成功路径复核和编译预检的任务上生成外部 Harness，并在声明的执行模型下交由 Echidna 探索参数与属性反例。

必须避免：

- “Harness 与 Original 完全等价”；
- “Harness 的 falsified 自动证明 Original 多交易语义下存在相同反例”；
- “Total calls 下降证明等量工作量 speedup”；
- “budget_exhausted 等于 property passed 或 contract safe”；
- “4 个 supported 与 exercise2 的 conditional 结果可以合并”；
- “smartbugs-onefunc 证明了多交易序列排序优势”。

如果报告固定成功路径的 11/11 差分重放，应明确它只说明在相同 caller 关系、每步成功和最终属性相关状态的窄条件下结果一致；它不证明完整 sender 搜索、失败前缀、交易间环境变化或所有回滚行为等价。

## 8. 下一阶段是否需要 native replay

需要。大阶段 B 应先为每个 public benchmark 建立独立、可审计的 native replay 记录，至少固定：

- 初始部署和 constructor/deployer 条件；
- 目标函数参数和已知路径；
- 每步 caller 及是否允许 alternation；
- 每步成功/失败和回滚边界；
- `msg.value`、payable、时间/区块和外部调用是否参与；
- Original 多交易序列与 Harness wrapper 的最终属性相关状态；
- 原始 trace、重放结果和 checksum。

其中，`exercise2-access-control` 必须先做 caller-controlled replay，不能以当前 Harness 的同 caller 结果代替。若某任务的差分不能在声明条件下对齐，应降级或排除，而不是修改纳入规则。
