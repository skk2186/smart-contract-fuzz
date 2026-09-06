# V1 Restart — Phase 05 Public Benchmark Preregistration、Compile/Preflight 与 1-Seed Smoke

Final status: PASS WITH WARNINGS

## 1. 阶段范围与冻结结论

本阶段只做公开 C-1 任务预登记、编译/路径预检和每个任务最多一个 seed 的 smoke。没有运行 30 seed、Formal full batch、Public C-1 full rerun、B2、matched-random、SMARTIAN、V2 或 C2 large experiment。

预登记在任何本阶段 fuzzing smoke 之前写入并冻结为：

- docs/v1-restart/phase05-public-preregistration.tsv
- 5 个已有 C-1 公开 benchmark、每个一个合约-属性组合；
- k_values 固定为 1,5；
- smoke seed 固定为 1；
- formal_seeds_planned 固定为 1-30，但本阶段没有执行；
- supported / conditional 分类没有根据 smoke 结果改变。

本阶段不产生正式论文效果结论；不把 smoke 结果写入 paper-ready；不刷新 frozen results；不根据 smoke 成败改变 preregistration inclusion/exclusion；不把 conditional 与 supported pooled。

## 2. 仓库状态与工具范围

- 当前分支：develop
- HEAD：57399a6210ac4818ad66109a732bf0a7ff34699a
- 工作区开始时干净，结束时只有本报告、预登记 TSV 和本阶段专用 runner 的新增改动。
- 按要求尝试 git fetch --prune，但远端 SSH 返回 GitHub Permission denied (publickey)。本地 develop 仍显示与 origin/develop 同步；本阶段结果以本地 HEAD 为准，不能声称已重新验证远端最新提交。
- 未修改 analyzer/、contracts/、configs/、results/、paper-ready/。
- 没有刷新任何冻结 checksum。
- 使用方法版本标记 Full-v1.0.1-compat；Original 配置为 configs/public-c1-original.yaml，Harness 配置为 configs/public-c1-harness.yaml，testLimit=100000、timeout=30s、workers=1、stopOnFail=true。
- 预检实际运行了 solc 和 Slither；Slither 由 analyzer/extract_rw.py 调用。Smoke 实际运行了 Echidna，Echidna 启动过程也执行了编译和 Slither 分析。没有联网下载 benchmark。

## 3. 新增文件

允许提交的新增文件：

- scripts/run_v1_public_smoke_case.sh
- docs/v1-restart/phase05-public-preregistration.tsv
- docs/v1-restart/PHASE_05_PUBLIC_PREREGISTRATION_AND_SMOKE.md

runner 只接受一个 benchmark、一个 method、seed 1；preflight 和 smoke 的所有输出都写入 work/v1-restart/phase05-public-smoke/。它拒绝覆盖已有 run、拒绝 symlink 输出路径，并在 command.txt 中检查冻结路径泄漏。

## 4. 预登记任务与语义分类

| benchmark | contract / property | classification | inclusion / semantic reason |
|---|---|---|---|
| echidna-flags | contracts/public-benchmarks/adapted/EchidnaFlagsTarget.sol / echidna_sometimesfalse | supported | 保留 flag0/flag1 状态转移，移除两个无关框架测试属性；未发现 caller、value、时间、外部调用或地址映射特征，仍保留单交易 wrapper 的 atomicity caveat。 |
| echidna-multi | contracts/public-benchmarks/raw/echidna/multi.sol / echidna_state3 | supported | 原始本地 Echidna 多步示例，无额外高风险环境特征，仍需窄范围成功路径 replay。 |
| exercise2-access-control | contracts/public-benchmarks/raw/exercise2/solution.sol / echidna_no_transfer | conditional | 导入闭包读取 msg.sender，并使用 mapping(address => uint256)；Owner() -> resume() 依赖跨步骤 caller 一致，而 Harness 固定为 Harness 地址，Original 可能交替 sender。 |
| smartbugs-multifunc | contracts/public-benchmarks/adapted/SmartBugsMultiFuncEchidna.sol / echidna_count_does_not_underflow | supported | 增加 Echidna 属性、扁平化源码，并以 0.4.25 兼容编译器保持 0.4.x unchecked arithmetic 语义；无额外高风险环境特征。 |
| smartbugs-onefunc | contracts/public-benchmarks/adapted/SmartBugsOneFuncEchidna.sol / echidna_count_does_not_underflow | supported | 增加 Echidna 属性、扁平化源码，并以 0.4.25 兼容编译器保持 0.4.x unchecked arithmetic 语义；无额外高风险环境特征。 |

当前五个候选中没有 excluded 行；reason_for_exclusion 对所有行明确写为 none。C-1 历史的 0.4.23 启动失败记录仍是环境兼容性排查证据，不是本次五个预登记任务的新增排除规则。

## 5. Compile / path preflight

5 个 benchmark 的 Original 编译、contract/property 定位、Slither 读写提取、Repeat/Value/Full 路径生成、K1/K5 Harness 生成和对应 solc 编译全部通过。每个 preflight 目录均有 manifest.tsv、command.txt、environment.txt、generated/、raw/、parsed/、summary/、status/。

| benchmark | compiler | generated known/top path evidence | original compile | K1/K5 Harness compile | status |
|---|---:|---|---|---|---|
| echidna-flags | 0.8.20 | set0(int256) -> set1(int256) | pass | pass / pass | preflight_pass |
| echidna-multi | 0.8.20 | f(uint256) -> g(uint256) -> h(uint256) | pass | pass / pass | preflight_pass |
| exercise2-access-control | 0.8.20 | Owner() -> pause() and Owner() -> resume(); resume path is not K1 | pass | pass / pass | preflight_pass |
| smartbugs-multifunc | 0.4.25 | init() -> run(uint256) -> run(uint256) | pass | pass / pass | preflight_pass |
| smartbugs-onefunc | 0.4.25 | run(uint256) -> run(uint256) | pass | pass / pass | preflight_pass |

预检生成物只在各自的 work preflight 目录中。既有 contracts/harnesses/public-c1/ 文件只作为对照和输入背景，没有被修改或覆盖。

## 6. 1-seed smoke 结果

下面的状态以 analyzer/parse_experiment_logs.py 的结果为准：

- falsified：raw log 出现属性反例 marker；
- budget_exhausted：明确到达预算终止且没有反例 marker；不表示属性通过或合约安全；
- startup_error：编译、路径或环境启动失败；
- unknown_error / incomplete：本阶段没有出现。

| benchmark | Original seed 1 | Full-K1 seed 1 | Full-K5 seed 1 | canonical smoke interpretation |
|---|---|---|---|---|
| echidna-flags | falsified | falsified | falsified | 三个入口均可启动并有完整 parser 输出。 |
| echidna-multi | budget_exhausted | falsified | falsified | Original 在该 seed/预算内未发现反例；不写成 passed。 |
| exercise2-access-control | falsified | budget_exhausted | falsified | conditional 任务单独报告；K1 未覆盖已知 Owner() -> resume() 路径。 |
| smartbugs-multifunc | falsified | falsified | falsified | 三个入口均可启动并有完整 parser 输出。 |
| smartbugs-onefunc | falsified | falsified | falsified | 三个入口均可启动并有完整 parser 输出。 |

共产生 18 个 smoke/重跑目录：15 个首次 smoke，外加因 runner metadata/导入问题产生的 3 个保留重跑或修复核对目录。所有 raw log 均保留；没有删除失败或重新命名旧 raw log 来改变分母。

### 保留的启动错误与 runner 修复

exercise2-access-control 的首次 Original run 使用了复制到 work 的 solution.sol，导致相对 import token.sol 无法解析，runner 正确记录为 startup_error。之后 runner 修复为 Original 直接使用已登记的仓库源码路径，并用新 run_id 重跑；重跑分类为 falsified。首次 startup_error 仍在 work 中保留，不计入 valid smoke。

另有两个首次运行的 status.env 分类曾与 parser 不一致：Echidna raw log 含预算终止，但 runner 的正则没有正确识别句点转义。raw log 未修改；固定 parser 已将其判为 budget_exhausted，metadata 以 parser 结果 reconciliation，并用新 run_id 重跑。最终修复后的 status.env 与 parsed/smoke.csv 一致。

最终 parser 统计为：

- 13 falsified；
- 4 budget_exhausted；
- 1 startup_error（保留的首次 exercise2 Original）；
- 0 unknown_error；
- 0 incomplete。

这些计数是 Phase 05 入口/日志审计计数，不是论文结果表，也不是成功率比较。

## 7. K1/K5 支持与 runner 分类

- K1 和 K5 均能在五个任务上生成并由对应 solc 编译。
- K5 smoke 没有因为 runner 不支持而阻塞；本阶段使用了已有的 K5 生成/编译链，并将输出放在 work。
- 每个 smoke 目录都有 manifest.tsv、command.txt、environment.txt、generated/、raw/、parsed/、summary/、status/ 和 status/checksums.sha256。
- raw log 没有手工编辑；checksum 覆盖已登记源码、配置、预登记 TSV、既有路径/语义审计输入以及本 run 的 manifest、command、environment、generated、raw、parsed、summary、status。
- 全部 command.txt 未发现指向 results/formal、results/formal-b2、results/public-benchmarks/c1、results/paper-data 或 contracts/harnesses/formal 的输出泄漏。
- parser 和 summarizer 都成功生成输出；最终 status.env 与 parser 状态一致。

## 8. 本阶段能支持和不能支持的结论

能支持：

- 五个既有 C-1 任务的来源、源码、属性、适配和语义分类已在 fuzzing 前登记；
- 五个任务的 Original 编译和 V1 Full 路径/Harness 生成入口可执行；
- K1/K5 Harness 在本地对应编译器下可编译；
- 每个已登记任务的 seed 1 smoke 能被分类为 falsified、budget_exhausted 或启动错误；
- runner 可以把 raw、派生解析、状态和 checksum 全部隔离在 work。

不能支持：

- 谁更强、统计显著性或任何 speedup；
- 从 seed 1 推断 30 seed 成功率；
- 把 budget_exhausted 写成属性通过或合约安全；
- 把 Original 和 Harness 的 Total calls 当作等量底层工作量；
- 把 Harness wrapper 与 Original 多交易执行宣称完全等价；
- 把 conditional exercise2 与四个 supported 任务 pooled；
- 把五个公开任务外推为真实合约总体；
- 把 smoke 结果写入论文主表或刷新 paper-ready。

## 9. Phase 06 建议与进入条件

可以考虑进入 Phase 06 小规模重复实验的任务：

- echidna-flags
- echidna-multi
- smartbugs-multifunc
- smartbugs-onefunc

前提是研究者先复核每个任务的 preflight generated JSON、K1/K5 Harness、raw log、parser CSV、status 和 checksum，并确认已有窄范围语义 replay 的解释仍适用。

exercise2-access-control 必须保持 conditional。若进入 Phase 06，只能作为单独条件案例，预先控制 caller 一致性并保留差分证据；不得与 supported 主分母 pooled。它不能因为本次 K5 smoke falsified 就升级为 supported。

Phase 06 不应直接跑 30 seed。建议先对四个 supported 任务各执行 1–3 个预登记 seed，确认路径、编译、日志和状态口径后，再由研究者决定是否扩大；所有新增输出继续写入独立 work 目录，不提升到 frozen results。

## 10. 研究者复核清单

进入下一阶段前，请复核：

1. docs/v1-restart/phase05-public-preregistration.tsv 的 27 列和五行任务是否符合预期；
2. exercise2 的 conditional 理由和 Owner() -> resume() caller 假设；
3. 五个 preflight 目录中的 full-sequences.json 与 K1/K5 Harness；
4. smoke 目录中首次 exercise2 startup_error 和 parser 修复重跑；
5. 预算终止只能写 budget_exhausted，不能写 property passed；
6. Original/Harness 的调用者、交易原子性、回滚边界和 Total calls 限制；
7. Git diff 只包含本报告、预登记 TSV 和 public smoke runner。

本阶段没有 commit 或 push。