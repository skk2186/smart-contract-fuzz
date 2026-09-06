# Phase 05R — Public Smoke Runner Provenance Fix

Final status: PASS WITH WARNINGS

## Scope

本阶段只修复 public smoke runner 的 provenance 记录问题，并新增本报告。

修改文件：

- scripts/run_v1_public_smoke_case.sh
- docs/v1-restart/PHASE_05R_PUBLIC_RUNNER_PROVENANCE_FIX.md

未修改：

- docs/v1-restart/phase05-public-preregistration.tsv
- docs/v1-restart/PHASE_05_PUBLIC_PREREGISTRATION_AND_SMOKE.md
- analyzer/
- contracts/
- configs/
- results/
- paper-ready/

## 修复内容

### 1. command.txt 的 value-constraints 命令

修复 preflight 的 write_command_record()，现在记录的命令包含与真实执行一致的输出路径：

~~~text
python analyzer/extract_value_constraints.py <source> --contract <contract> > <output_root>/generated/value-constraints.json
~~~

验证输出中的实际记录为：

~~~text
python analyzer/extract_value_constraints.py /home/skk/research/smart-contract-fuzz/contracts/public-benchmarks/adapted/EchidnaFlagsTarget.sol --contract PublicEchidnaFlagsTarget > /home/skk/research/smart-contract-fuzz/work/v1-restart/phase05-public-smoke/echidna-flags-preflight-phase05r-provenance-20260906-01/generated/value-constraints.json
~~~

### 2. environment.txt 的 solc 版本记录时机

已将 write_environment、write_command_record 和 write_manifest 移到：

~~~text
solc-select use "$COMPILER"
~~~

成功之后执行。

因此 environment.txt 记录的是目标 benchmark 实际使用的 solc 版本。preflight 验证结果为：

~~~text
COMPILER=0.8.20
SOLC_VERSION=solc, the solidity compiler commandline interface Version: 0.8.20+commit.a1b79de6.Linux.g++
~~~

如果 solc-select use "$COMPILER" 失败，runner 会先写出最小 status/status.env，状态为 startup_error，FAILED_STAGE=solc_select，RUN_COMPLETED=0，然后退出；checksum 写入逻辑允许此时尚未生成 environment/command/manifest。

另外增加了向后兼容的 preflight --run-id <run_id>，仅用于选择新的临时输出目录，默认 preflight 路径保持不变。

## 验证

开始前使用仓库所属的 WSL Git 环境确认：

- 分支：develop
- HEAD：97ca2ba60863d54172a710c6777705a315e01ccc
- 工作区：clean
- git fetch --prune：成功

执行的验证命令：

~~~text
bash -n scripts/run_v1_public_smoke_case.sh
grep -n "extract_value_constraints.py" scripts/run_v1_public_smoke_case.sh
grep -n "solc-select use" scripts/run_v1_public_smoke_case.sh
grep -n "write_environment" scripts/run_v1_public_smoke_case.sh
git diff --check -- scripts/run_v1_public_smoke_case.sh
bash scripts/run_v1_public_smoke_case.sh --mode preflight --run-id phase05r-provenance-20260906-01 --benchmark echidna-flags
sha256sum -c work/v1-restart/phase05-public-smoke/echidna-flags-preflight-phase05r-provenance-20260906-01/status/checksums.sha256
~~~

preflight 结果：

~~~text
STATUS=preflight_pass
RUN_COMPLETED=1
EXIT_CODE=0
FAILED_STAGE=none
~~~

本次 preflight 调用了 solc，并通过 analyzer/extract_rw.py 使用了 Slither API；没有运行 Echidna，没有运行 smoke。

## 证据边界

Phase 05 已有 raw log 不被修改；
Phase 05 smoke 结果不被重写；
本阶段不产生新的论文效果结论；
本阶段不刷新 frozen results；

本阶段没有扩大 seed，没有重跑正式 public smoke 批次，也没有进入 Phase 06。

## 提交建议

研究者只应提交：

~~~text
scripts/run_v1_public_smoke_case.sh
docs/v1-restart/PHASE_05R_PUBLIC_RUNNER_PROVENANCE_FIX.md
~~~

不得提交 work/临时输出目录。

## Phase 06

不允许因本报告直接进入 Phase 06；仍需按 V1 研究流程由研究者单独复核并明确确认。
