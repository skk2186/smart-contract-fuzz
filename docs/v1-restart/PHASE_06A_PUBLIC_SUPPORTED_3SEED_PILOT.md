# Phase 06A：Public Supported Benchmarks 3-Seed Pilot

Final status: PASS WITH WARNINGS

## 1. 范围与研究问题

本阶段只验证四个已在 Phase 05 预登记为 supported 的公开基准，在 seed 1、2、3 下运行 Original、Full-K1、Full-K5 时是否能稳定启动，并检查 runner 的 provenance、parser/status 一致性、K1/K5 Harness 生成与编译。

本阶段不产生正式论文主表，不刷新 frozen results，不纳入 conditional 任务，不使用 Total calls 计算 speedup，也不把 budget_exhausted 当作 property passed。

## 2. Git 与文件状态

- 当前分支：develop
- Start HEAD：efe2cb44fb9c25293f85a3fa50bc493b5eeead93
- Final HEAD：efe2cb44fb9c25293f85a3fa50bc493b5eeead93
- origin/develop：efe2cb44fb9c25293f85a3fa50bc493b5eeead93
- 工作区基线由 WSL Git 确认 clean；runner 的 Windows 侧 100755/100644 显示差异是权限元数据显示问题，WSL Git 保持 100755。
- 本阶段修改 runner：scripts/run_v1_public_smoke_case.sh
- 新增阶段报告：docs/v1-restart/PHASE_06A_PUBLIC_SUPPORTED_3SEED_PILOT.md
- 未修改 analyzer/、contracts/、configs/、results/、paper-ready/。
- 未修改 Phase 05 preregistration TSV、Phase 05 报告或 Phase 05R 报告。
- 未提交、未 push，也未提交 work/ 临时输出。

## 3. Runner 修复

保留了 Phase 05 的 preflight 行为和 smoke 的 seed 1 限制，新增：

1. --mode pilot-preflight：只接受四个 supported benchmark，并把 preflight 输出隔离到 work/v1-restart/phase06a-public-supported-3seed/。
2. --mode pilot：只允许 seed 1、2、3；输出目录为 work/v1-restart/phase06a-public-supported-3seed/<run_id>/。
3. 明确拒绝 exercise2-access-control 和其他非 supported benchmark。
4. pilot-preflight 使用 run-id 生成独立目录；失败目录不会被覆盖，便于安全重跑。
5. pilot 优先读取默认有效 preflight；默认目录不完整时，只选择同一 benchmark 下 STATUS=preflight_pass 的重跑目录。
6. 保留 falsified/failed marker 优先于 budget_exhausted 的分类顺序。

验证结果：

- bash -n：通过；
- git diff --check：通过；
- Phase 05 smoke seed 2：按预期拒绝；
- Phase 06A pilot seed 4：按预期拒绝；
- Phase 06A pilot exercise2-access-control：按预期拒绝；
- runner 文件模式：WSL Git 仍为 100755。

## 4. 工具运行范围

- Echidna：运行 36 次 pilot。
- Slither：4 个独立 preflight 中通过 analyzer/extract_rw.py 调用。
- solc：4 个 preflight 中分别编译 Original、K1 Harness、K5 Harness；pilot 运行前选择预登记 compiler，Echidna 负责其运行时编译路径。
- analyzer/contracts/configs：没有修改。
- exercise2-access-control：没有运行，也没有进入 supported 分母。

## 5. 独立 preflight

| benchmark | run_id | status | Original | rw/Repeat/Value/Full | K1 Harness | K5 Harness |
|---|---|---|---|---|---|---|
| echidna-flags | phase06a-echidna-flags-preflight-r2 | preflight_pass | compile | pass | generated + compile | generated + compile |
| echidna-multi | phase06a-echidna-multi-preflight | preflight_pass | compile | pass | generated + compile | generated + compile |
| smartbugs-multifunc | phase06a-smartbugs-multifunc-preflight | preflight_pass | compile | pass | generated + compile | generated + compile |
| smartbugs-onefunc | phase06a-smartbugs-onefunc-preflight | preflight_pass | compile | pass | generated + compile | generated + compile |

四个有效 preflight 的 status.env 均为：

- STATUS=preflight_pass
- RUN_COMPLETED=1
- EXIT_CODE=0
- FAILED_STAGE=none

四个 preflight 的 status/checksums.sha256 均验证通过。每个有效目录均保留 manifest.tsv、command.txt、environment.txt、generated/、raw/、summary/ 和 status/。

首次 flags preflight 使用了 phase06a-echidna-flags-preflight，但调用进程没有激活 contract-fuzz，runner 在读取未设置的 CONDA_DEFAULT_ENV 时安全退出；该目录保留为启动前环境配置 warning，没有 status marker，不计入有效 preflight 表，也没有被覆盖。随后使用新的 run_id phase06a-echidna-flags-preflight-r2 成功完成。

## 6. 36 个 pilot 结果

每个单元格对应一个独立 run，run_id 格式为 phase06a-<benchmark>-<method>-s<seed>。所有 pilot 均写入 phase06a-public-supported-3seed/<run_id>/。

| benchmark | method | seed 1 | seed 2 | seed 3 | parser/status |
|---|---|---|---|---|---|
| echidna-flags | Original | falsified | falsified | falsified | 3/3 一致 |
| echidna-flags | Full-K1 | falsified | falsified | falsified | 3/3 一致 |
| echidna-flags | Full-K5 | falsified | falsified | falsified | 3/3 一致 |
| echidna-multi | Original | budget_exhausted | falsified | falsified | 3/3 一致 |
| echidna-multi | Full-K1 | falsified | falsified | falsified | 3/3 一致 |
| echidna-multi | Full-K5 | falsified | falsified | falsified | 3/3 一致 |
| smartbugs-multifunc | Original | falsified | falsified | falsified | 3/3 一致 |
| smartbugs-multifunc | Full-K1 | falsified | falsified | falsified | 3/3 一致 |
| smartbugs-multifunc | Full-K5 | falsified | falsified | falsified | 3/3 一致 |
| smartbugs-onefunc | Original | falsified | falsified | falsified | 3/3 一致 |
| smartbugs-onefunc | Full-K1 | falsified | falsified | falsified | 3/3 一致 |
| smartbugs-onefunc | Full-K5 | falsified | falsified | falsified | 3/3 一致 |

汇总：

- pilot 总数：36；
- falsified：35；
- budget_exhausted：1；
- startup_error：0；
- unknown_error：0；
- incomplete：0；
- parser/status 不一致：0；
- 每个 pilot 都有 manifest、command、environment、raw/seed-<seed>.log、parsed/smoke.csv、summary/smoke.csv、status/status.env 和 status/checksums.sha256；
- 36 个 pilot 目录的 checksum 验证通过。

echidna-multi / Original / seed 1 的 budget_exhausted 只表示该预算内没有观察到反例，不能解释为属性通过、合约安全或无漏洞。

## 7. 本阶段能支持的结论

- 四个已登记为 supported 的公开任务在 seed 1–3 下均能完成 runner 启动和日志解析。
- Phase 06A runner 能将四个任务的 36 个 run 隔离到 work，并记录 manifest、command、environment、raw、parsed、summary、status 和 checksum。
- 四个任务的 Original 编译、V1 路径生成、K1/K5 Harness 生成和编译入口均可执行。
- 在本次 3-seed pilot 中没有出现 pilot startup_error、unknown_error 或 incomplete。
- status.env 与 parser 对 36 个 pilot 的分类完全一致。

## 8. 本阶段不能支持的结论

本阶段不能说明：

- Original、Full-K1 或 Full-K5 谁更强；
- 任何统计显著性；
- 任何 speedup 或等量工作量优势；
- 3 个 seed 可以代表 30-seed 成功率；
- Harness 与 Original 的多交易语义完全等价；
- 单交易 wrapper 与 Original 的 caller、atomicity、rollback 边界相同；
- 四个公开任务可以代表真实合约总体；
- budget_exhausted 等同于 property passed；
- 结果可以直接写入 paper-ready 主表；
- 本阶段结果允许不经人工复核直接启动 30-seed 正式实验。

## 9. Phase 06B 建议

建议进入 Phase 06B 的预登记/人工复核阶段，但不建议把本报告直接当作 30-seed 开跑授权。进入前应复核四个有效 preflight 的 generated JSON、K1/K5 Harness、36 个 raw log、parsed CSV、status 和 checksum；继续保持 exercise2-access-control 的 conditional 边界，不与 supported 任务 pooled。

明确保留以下边界：

- 本阶段不产生正式论文主表；
- 本阶段不刷新 frozen results；
- 本阶段不修改 paper-ready；
- 本阶段不把 conditional 任务 pooled；
- 本阶段不使用 Total calls 计算 speedup；
- 本阶段不把 budget_exhausted 当成 property passed；
- 本阶段不证明 Harness 与 Original 完全等价；
- 本阶段不允许直接进入 30 seed。

