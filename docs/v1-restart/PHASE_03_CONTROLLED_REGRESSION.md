# V1 Restart — Phase 03：Controlled Mechanism Regression

更新日期：2026-09-01

## Final status

**PASS WITH WARNINGS**

本阶段验证 V1 主方法在四个受控 Formal 基准上的机制可复现性，不构成正式 30 seed 实验，不进入 public C1、B2、matched-random、SMARTIAN、V2 或 C2，也不产生论文统计结论。

研究问题是：在固定合约、属性和配置下，Property、Value、Repeat 和 Top-K 机制是否仍能生成预期的 Full-K1 路径，并在 Echidna 中重现目标属性反例。

输入为四个 benchmark 合约、属性 `echidna_value_safe`、Original 配置 `configs/formal-original-seq4.yaml`、Full-K1 配置 `configs/formal-harness-seq1.yaml`，以及 seed 1、2、3。输出全部写入 `work/v1-restart/`。本阶段重新运行了 Echidna；Full-K1 还重新运行了 V1 分析器、Slither 读写提取和值约束提取，并用 solc 编译生成 Harness。没有把任何新 raw log 写入冻结 `results/`。

## Runner 变更

修改了 `scripts/run_v1_restart_case.sh`，方法版本记录为 `Full-v1.0-restart-benchmark-v1`。

只增加了 `--benchmark` 参数，并保留省略该参数时的 NoisyFourStep 默认行为。显式映射如下：

| benchmark | contract | property | Original config | Full-K1 config |
|---|---|---|---|---|
| `noisy-four-step` | `NoisyFourStepExample` | `echidna_value_safe` | `formal-original-seq4.yaml` | `formal-harness-seq1.yaml` |
| `reset-example` | `ResetExample` | `echidna_value_safe` | `formal-original-seq4.yaml` | `formal-harness-seq1.yaml` |
| `branch-value` | `BranchValueExample` | `echidna_value_safe` | `formal-original-seq4.yaml` | `formal-harness-seq1.yaml` |
| `repeated-call` | `RepeatedCallExample` | `echidna_value_safe` | `formal-original-seq4.yaml` | `formal-harness-seq1.yaml` |

输出目录结构没有改变。manifest/environment 另外记录了 `test_limit=100000`、`timeout=30`、`workers=1`、`stop_on_fail=true`。没有修改 analyzer、contracts 或 configs。

## Runner 分类 check-run

有效的 NoisyFourStep check-run 均显示 raw log 含 `falsified` 和 `echidna_value_safe: failed!`，对应 `status.env` 为 `STATUS=completed`、`RUN_COMPLETED=1`；没有把已发现反例的运行分类为 `budget_exhausted`。

- `work/v1-restart/phase03-check-noisy-full-k1-s1/`：有效，`completed`。
- `work/v1-restart/phase03-check-noisy-original-s1-retry/`：有效，`completed`。
- `work/v1-restart/phase03-check-noisy-original-s1/`：第一次未通过 contract-fuzz 环境前置检查，保留为 `startup_error`，没有 raw log，也没有运行 Echidna；未覆盖该目录，重试使用了上面的新 run-id。

另外，四个 benchmark 的 Original/Full-K1 映射 dry-run 均为 `STATUS=dry_run`、`RUN_COMPLETED=0`，没有运行 Echidna。

## 正式小规模运行

共 24 个运行：4 个 benchmark × 2 个 method × 3 个 seed。所有正式运行的 raw log 均出现 `falsified`、`echidna_value_safe: failed!` 和 `Test limit reached. Stopping.`；由于失败 marker 优先级正确，所有 status 均为 `STATUS=completed`、`RUN_COMPLETED=1`、`FAILED_STAGE=echidna`、`EXIT_CODE=1`。这表示发现了属性反例并结束运行，不表示属性通过或合约安全。

### NoisyFourStepExample — Property-directed pruning / Top-K

- Original：`work/v1-restart/phase03-noisy-four-step-original-s1/`、`phase03-noisy-four-step-original-s2/`、`phase03-noisy-four-step-original-s3/`
- Full-K1：`work/v1-restart/phase03-noisy-four-step-full-k1-s1/`、`phase03-noisy-four-step-full-k1-s2/`、`phase03-noisy-four-step-full-k1-s3/`
- 三个 Full-K1 的 Top-1 均为 `register() -> deposit() -> approve() -> withdraw(uint256)`；候选数为 generated 3、retained 3。
- Harness wrapper 调用顺序正确，末端 `withdraw` 参数为 Echidna fuzz 的 `arg_1_3_0`，未静态写死。

### ResetExample — Property-directed / Top-K under reset interference

- Original：`work/v1-restart/phase03-reset-example-original-s1/`、`phase03-reset-example-original-s2/`、`phase03-reset-example-original-s3/`
- Full-K1：`work/v1-restart/phase03-reset-example-full-k1-s1/`、`phase03-reset-example-full-k1-s2/`、`phase03-reset-example-full-k1-s3/`
- 三个 Full-K1 的 Top-1 均为 `begin() -> authorize() -> commit() -> execute(uint256)`；候选数为 generated 33、retained 33。
- `reset()`/`poison()` 干扰没有取代有效阶段路径；`execute` 参数仍为动态 fuzz 参数。

### BranchValueExample — Value guidance

- Original：`work/v1-restart/phase03-branch-value-original-s1/`、`phase03-branch-value-original-s2/`、`phase03-branch-value-original-s3/`
- Full-K1：`work/v1-restart/phase03-branch-value-full-k1-s1/`、`phase03-branch-value-full-k1-s2/`、`phase03-branch-value-full-k1-s3/`
- 三个 Full-K1 的 Top-1 均为 `prepareGood() -> unlock() -> activate() -> trigger(uint256)`；Top-1 的 value score 为 18，3 个 value matches、0 个 conflicts；候选数为 generated 7、retained 7。
- `trigger` 参数仍为动态 fuzz 参数，未静态写死。

### RepeatedCallExample — Repeat-aware generation

- Original：`work/v1-restart/phase03-repeated-call-original-s1/`、`phase03-repeated-call-original-s2/`、`phase03-repeated-call-original-s3/`
- Full-K1：`work/v1-restart/phase03-repeated-call-full-k1-s1/`、`phase03-repeated-call-full-k1-s2/`、`phase03-repeated-call-full-k1-s3/`
- 三个 Full-K1 的 Top-1 均为 `deposit() -> deposit() -> unlock() -> withdraw(uint256)`；`has_repetition=true`，`deposit()` 出现 2 次；候选数为 generated 3、retained 3。
- Harness wrapper 保留了两个连续 `deposit()`，`withdraw` 参数仍为动态 fuzz 参数。

每个 Full-K1 运行均已检查 `rw.json`、`repeat-property-sequences.json`、`value-constraints.json`、`full-sequences.json`、生成的 Harness、raw log、status、checksum、manifest、command 和 environment。所有 checksum 校验通过，没有 `MISSING` 项，也没有冻结路径泄漏。runner 创建的 `parsed/` 和 `summary/` 目录未用于本阶段派生统计；没有结果被提升到正式证据区。

## 结果边界与语义说明

本阶段支持的窄结论是：

- NoisyFourStep 的属性相关筛选和 Top-1 路径仍可复现；
- ResetExample 的有效阶段路径在 reset 干扰下仍可进入 Top-1；
- BranchValue 的常量值证据仍能把 `prepareGood()` 排在 Top-1；
- RepeatedCall 的必要重复访问仍会被生成并进入 Top-1；
- 在本阶段预算下，Original 和 Full-K1 的四个受控目标均能发现 `echidna_value_safe` 反例。

Original 与 Harness 的交易语义差异仍然保留：Original 使用多笔独立交易序列，而 Harness 将候选调用封装在一次 wrapper 调用中。因此调用者、交易原子性、中间回滚范围和每次外层调用包含的目标函数数可能不同。本阶段不能证明两者语义完全等价。

本阶段不能得出以下结论：

- 不能声称 Full-K1 普遍优于 Original；
- 不能计算正式 speedup；
- 不能把 Total calls 当作等量工作；
- 不能把 `budget_exhausted` 当作 property passed；
- 不能证明 Harness 与 Original 语义完全等价；
- 不能外推到真实合约总体或外部工具竞争结果；
- 不能把本阶段 24 次运行与冻结 V1 30 seed 结果 pooled；
- 不能把本阶段结果写入 public C1、B2、matched-random、SMARTIAN 或 V2 结论。

## Scope、警告与 Phase 04

- analyzer：未修改。
- contracts：未修改。
- configs：未修改。
- frozen `results/`：未修改。
- `paper-ready/`：未修改。
- public C1、B2、matched-random、SMARTIAN、V2、C2、30 seed 和 formal full batch：均未运行。
- `git fetch --prune` 已执行，但因远端 SSH 公钥权限失败；本地 `develop` 显示与 `origin/develop` 同步。
- 首次未激活 contract-fuzz 的 check-run 目录按规则保留，没有删除或覆盖；有效重试目录另行记录。
- 当前工作树中的 runner 修改尚未 commit 或 push。

**Phase 04：允许在研究者复核本报告、runner diff、24 个运行目录及两项 warning 后进入。** 进入 Phase 04 不意味着可以直接启动 30 seed 或修改纳入规则；仍需单独预登记研究问题、输入、预算和输出目录。
