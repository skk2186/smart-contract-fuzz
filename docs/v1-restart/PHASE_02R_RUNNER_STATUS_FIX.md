# Phase 02R Runner Status Fix

## Final status

**PASS WITH WARNINGS**

runner 状态分类已按要求修复，shell 语法检查通过，两个指定 dry-run 均成功，且没有执行 Echidna。warning 有两项：本阶段开始时 git fetch --prune 因远端无响应等待约两分钟后被中断；第一次未激活 contract-fuzz 环境的 dry-run 被前置检查拒绝，并留下了一个只含 startup_error 状态文件的临时目录，随后已原样改名保留，没有覆盖或删除。

本阶段没有进入 Phase 03，也没有运行真实 check-run。

## Changed files

本阶段只修改了：

~~~text
scripts/run_v1_restart_case.sh
~~~

新增阶段报告为：

~~~text
docs/v1-restart/PHASE_02R_RUNNER_STATUS_FIX.md
~~~

runner 目录结构、参数解析、运行命令、输出路径和 RUN_COMPLETED 的整体写入逻辑均未改变。

## Why Phase 02 had the wrong status

Phase 02 的两份 raw log 都包含如下组合：

~~~text
Test echidna_value_safe falsified!
Test limit reached. Stopping.
echidna_value_safe: failed!
EXIT_CODE=1
~~~

旧逻辑先检查 test limit、testLimit、budget.exhaust、time limit 或 timed out。只要这些 marker 先命中，就会直接写 STATUS=budget_exhausted，后面的 falsified/property failed/assertion failed 判断根本不会执行。因此 Echidna 已经发现反例时，预算或停止信息仍可能把结果错误分类为 budget_exhausted。

budget_exhausted 不能解释为 property passed，也不能解释为合约安全。

## Fixed classification priority

在 FAILED_STAGE=echidna 时，新的优先级是：

1. raw log 出现 falsified、property failed、assertion failed 或 failed!，立即写 STATUS=completed；
2. 没有失败 marker 但 EXIT_CODE=0，写 STATUS=completed；
3. 没有失败 marker、EXIT_CODE 非零且确有测试预算或时间限制 marker，才写 STATUS=budget_exhausted；
4. 其他情况保留 STATUS=unknown_error。

实际使用的失败 marker 正则为：

~~~text
falsified|property[[:space:][:punct:]]*failed|assertion[[:space:][:punct:]]*failed|failed!
~~~

这段判断仍被 FAILED_STAGE=echidna 保护。对于 Echidna 找到 falsified 且 EXIT_CODE=1 的运行，状态现在会是：

~~~text
STATUS=completed
RUN_COMPLETED=1
~~~

## Validation commands

执行过的检查和结果：

- git fetch --prune：已执行，但远端无输出并阻塞约两分钟，随后中断；没有改变工作区。
- git switch develop：成功，已经在 develop。
- git status --short：开始前干净。
- git branch --show-current：develop。
- git rev-parse HEAD：9c1d40a3591c5a6e5f5fb44431e7ea0c10dc00f4。
- git rev-parse origin/develop：9c1d40a3591c5a6e5f5fb44431e7ea0c10dc00f4。
- sed -n '330,390p' scripts/run_v1_restart_case.sh：确认了旧的错误优先级。
- 只读 grep 检查了 Phase 02 两份保留 raw log，确认 falsified 与 Test limit reached 同时存在。
- bash -n scripts/run_v1_restart_case.sh：通过。
- Original dry-run：成功。
- Full-K1 dry-run：成功。

为满足环境前置检查，两个成功 dry-run 通过已有的 contract-fuzz 环境执行，实际命令形式为：

~~~text
conda run -n contract-fuzz bash scripts/run_v1_restart_case.sh ... --dry-run
~~~

## Dry-run outputs

成功的 dry-run 输出目录为：

~~~text
work/v1-restart/phase02r-dry-original-s1/
work/v1-restart/phase02r-dry-full-k1-s1/
~~~

两者都包含 command.txt、environment.txt、manifest.tsv 和 status/status.env，并记录：

~~~text
DRY_RUN=1
STATUS=dry_run
RUN_COMPLETED=0
EXIT_CODE=0
FAILED_STAGE=none
~~~

第一次环境未激活的失败临时目录被保留为：

~~~text
work/v1-restart/phase02r-dry-original-s1-preflight-failed/
~~~

它只包含 preflight 失败的 status/status.env，不属于实验结果，也不在 results/ 下。

## Scope checks

- frozen results：未改动；
- analyzer/：未改动；
- contracts/：未改动；
- configs/：未改动；
- paper-ready/：未改动；
- Phase 02 原始日志及 work/v1-restart/phase02-* 原目录：未改动；
- Phase 02 报告：未重写；
- Echidna：本阶段未运行；
- Slither/solc：本阶段未运行；
- 30 seed、C-1、B-2、matched-random、SMARTIAN、V2、public benchmark 和 formal full batch：均未运行。

dry-run 的 command.txt 会保留计划执行的 Echidna 命令，但 status.env 的 DRY_RUN=1、FAILED_STAGE=none 和无 raw/目录表明这些命令没有被执行。

## Phase 03

**不允许由本阶段直接进入 Phase 03。** Phase 02R 只修复 runner 分类并完成 dry-run 验证；Phase 03 保持未开始。研究者确认本报告和 runner diff 后，如仍需端到端确认，可另行预登记 NoisyFourStep Original 与 Full-K1 各一次 check-run，再决定是否进入后续小规模回归。

## Preservation statement

Phase 02 原始日志不被修改，Phase 02 报告不被重写。没有执行 commit 或 push。
