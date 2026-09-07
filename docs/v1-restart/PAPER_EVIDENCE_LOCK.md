# 大阶段 A：Paper Evidence Lock

## 1. 阶段目的与锁定范围

本阶段把 Phase 01–Phase 06A 已有材料整理为可追溯的论文 evidence inventory，并单独记录 Harness 与 Original 的语义边界。本阶段不是正式主实验，不改变任何 V1 方法、实验口径或冻结结果。

本阶段明确不做以下事情：

- 不运行 30 seed，不扩大 public benchmark；
- 不补 SMARTIAN、MuFuzz 或 IR-Fuzz 工具级实验；
- 不刷新 `results/` 下的 frozen results 和 checksum；
- 不修改历史 quarantine 结果；
- 不把 Phase 06A pilot 写成正式主表；
- 不把 `budget_exhausted` 写成 property passed 或 contract safe；
- 不把 Harness 与 Original 写成完全等价，也不以 `Total calls` 声称 speedup。

本阶段新增的 inventory 入口是：

- `paper-ready/v1/evidence_index.tsv`；
- `docs/v1-restart/SEMANTIC_BOUNDARY_AUDIT.md`；
- `docs/v1-restart/PHASE_A_EVIDENCE_LOCK_CLOSEOUT.md`。

## 2. 当前仓库状态

| 项目 | 核验结果 |
|---|---|
| 当前分支 | `develop` |
| 当前 HEAD | `33e3a81b8d416326f3b54003427f9cb8f31f17a0` |
| 最近提交 | `33e3a81 test: run public supported V1 3-seed pilot` |
| 工作区 | `scripts/run_v1_public_smoke_case.sh` 有未提交换行差异；`git diff --ignore-space-at-eol` 无内容差异 |
| 关键 Phase 01–06A 文档 | 均存在 |
| Phase 06A work 目录 | 存在 |
| analyzer/contracts/configs/results | 本阶段未修改 |

工作区中的 runner 改动属于进入本阶段前已有的 Phase 06A 状态。本阶段没有覆盖、回退或提交该文件；提交前应由研究者确认该换行差异确实只是文件格式差异。

## 3. Phase 06A 原始产物盘点

本地 `work/v1-restart/phase06a-public-supported-3seed/` 可读取到：

- 36 个 pilot run 目录，即 4 个 supported benchmark × 3 个 method × 3 个 seed；
- 4 个有效 preflight 目录，均为 `STATUS=preflight_pass`，均包含 Original 编译、RW/Repeat/Value/Full 生成、K1/K5 Harness 及编译产物；
- 1 个保留的首次 flags preflight 空目录，没有 status marker，也不计入有效 preflight；它保留为启动前环境配置失败的 provenance warning；
- 36/36 pilot 目录均包含 `manifest.tsv`、`command.txt`、`environment.txt`、对应 `raw/seed-<seed>.log`、`parsed/smoke.csv`、`summary/smoke.csv`、`status/status.env` 和 `status/checksums.sha256`；
- 40/40 个 pilot/preflight checksum manifest 通过 WSL `sha256sum -c`；
- 36/36 个 pilot 的 `status.env` 与 `parsed/smoke.csv` 分类一致；
- 36/36 个 pilot 的原始日志均保留了与分类相符的 marker。

实际 pilot 分类为：

| status | 数量 | 解释 |
|---|---:|---|
| `falsified` | 35 | 当前执行模型、输入和预算内观察到属性反例 |
| `budget_exhausted` | 1 | `echidna-multi / Original / seed 1` 在预算内未观察到反例；不表示 property passed 或 contract safe |
| `startup_error` | 0 | — |
| `unknown_error` | 0 | — |
| `incomplete` | 0 | — |
| parser/status mismatch | 0 | — |

因此，Phase 06A 的原始产物是可审计的 pilot provenance，但其 3-seed 结果仍只能作为 `pilot_only`。产物完整不等于结果已经获得正式主表资格。

## 4. 论文正文、附录与 quarantine 的证据边界

### 可进入正文的证据类型

以下材料可以进入论文正文的方法、实验设置、可复现性或限制章节，但不自动构成新的效果主表：

- Phase 01 的仓库隔离、工具基线、冻结目录边界和运行区治理；
- Phase 02R 的 runner 状态分类优先级，以及 `falsified` 优先于预算终止 marker 的实现规则；
- Phase 04 冻结的方法定位：V1 是既有 Echidna 属性模糊测试之上的前处理和外部 Solidity Harness synthesis，不是新的通用 fuzzer，不替代 Echidna，也不修改 Echidna core；
- Phase 05 的 public preregistration schema、任务来源、属性、编译器、配置、K 值、成功/失败定义和 supported/conditional 分类规则；
- Phase 05R 的 command/environment provenance 修复和独立 preflight run-id 规则；
- 受控 Formal 机制证据可用于说明 Property、Value、Repeat 和 Top-K 各自解决的窄障碍，但必须保持其受控 benchmark 限制，并以原始运行和冻结白名单为来源。

### 只能进入附录或方法案例的证据

- Phase 02 的单 benchmark、Original/Full-K1 各一个 seed 最小复现；
- Phase 03 的 24-run controlled regression；
- Phase 06A 的 36-run、3-seed public pilot；
- 任何只证明路径生成、编译、启动或固定成功路径重放的材料；
- `smartbugs-onefunc` 这类主要验证 runner/public integration 的任务，不得被包装成多交易序列优势证据。

Phase 06A 不支持统计显著性、30-seed 成功率代表性、Full-K1/Full-K5 普遍优于 Original、Total calls speedup 或 Harness/Original 完全等价。唯一的 `budget_exhausted` 必须以“在给定预算内没有观察到反例”表述。

### 禁止使用或保持 quarantine 的证据

`results/matched-random-v1/` 继续保持：

- `PROVENANCE_UNRESOLVED`；
- `DO_NOT_USE_FOR_NEW_CLAIMS`；
- `LEGACY_CONTROL_QUARANTINED`。

本阶段没有重算、覆盖或刷新其 checksum，没有把它放入 `paper-ready` 主表，也没有把它与 Phase 06A 或 V1 frozen results 混合。Phase 01 记录的冻结 checksum 缺失/不匹配警告同样保留；本阶段不以新文档掩盖该历史问题。

`results/v2/`、`V2/native-corpus/`、C0、smoke、历史 pilot、不可证明完整执行的 overhead-v2 以及未经白名单允许的旧控制材料，不进入 V1 主结果。

## 5. Phase 01–Phase 06A 的论文位置与可支撑主张

| 阶段 | 可引用来源 | 可支撑的论文位置 | 可支撑的内容 | 明确限制 |
|---|---|---|---|---|
| Phase 01 | `PHASE_01_REPOSITORY_ENV_AUDIT.md`、`PHASE_01_CHECKSUM_AUDIT.md`、`PHASE_01_FREEZE_PROVENANCE.md`、`PHASE_01_CLOSEOUT.md` | Reproducibility、threats、data governance | 仓库/运行/证据三区隔离、工具基线、冻结结果保护、历史 provenance 风险被显式隔离 | checksum 历史 gate 仍有 warning；不构成性能结果 |
| Phase 02 | `PHASE_02_MINIMAL_REPRODUCTION.md` 及两个 `work/v1-restart/phase02-*` 运行目录 | 方法案例、附录 | NoisyFourStep 上 Original 与 Full-K1 均以 raw log 观察到反例；Full-K1 固定交易顺序，但 `withdraw` 参数仍由 Echidna fuzz | 单 seed；旧 runner 曾把 falsified 错分为 budget_exhausted；不能比较 Total calls 或证明语义等价 |
| Phase 02R | `PHASE_02R_RUNNER_STATUS_FIX.md` 及 runner diff/dry-run | Implementation correctness、Reproducibility | `falsified/failed` marker 优先于预算 marker；失败、预算耗尽、未知错误和启动错误分开 | 主要是分类修复和 dry-run；未由本阶段新增端到端效果实验 |
| Phase 03 | `PHASE_03_CONTROLLED_REGRESSION.md` 及 24 个 work 运行 | Mechanism evaluation、附录 | NoisyFourStep=property pruning/Top-K，Reset=reset 干扰，BranchValue=value guidance，RepeatedCall=repeat-aware；四个受控目标均在本批次观察到反例 | 受控小型合约、3 seed、非 frozen 主批次；不能外推真实生态或外部竞品 |
| Phase 04 | `PHASE_04_METHOD_CLAIM_AND_PREREGISTRATION.md` | Method positioning、Related work、Threats | 冻结 V1 的组合定位、贡献边界、语义边界和 public preregistration 规则 | 不支持“首次使用依赖/排序/重复调用”的绝对首创，也不批准正式重跑 |
| Phase 05 | `PHASE_05_PUBLIC_PREREGISTRATION_AND_SMOKE.md`、`phase05-public-preregistration.tsv` | Experimental setup、Dataset selection、Reproducibility | 5 个 public task 的来源/属性/配置/编译器/纳入规则；4 supported、1 conditional；preflight 和 1-seed smoke 入口可执行 | smoke 不是效果主表；conditional 任务不得与 supported pooled |
| Phase 05R | `PHASE_05R_PUBLIC_RUNNER_PROVENANCE_FIX.md`、`scripts/run_v1_public_smoke_case.sh` | Reproducibility、Implementation details | command/environment 写入时机和独立 preflight run-id 修复，保证 compiler/provenance 可追溯 | runner 的未提交换行差异需研究者复核；不产生新的论文效果结论 |
| Phase 06A | `PHASE_06A_PUBLIC_SUPPORTED_3SEED_PILOT.md`、`work/v1-restart/phase06a-public-supported-3seed/` | Pilot appendix、pipeline validation | 4 个预登记 supported 候选的 36 次 pilot 均完成；35 falsified、1 budget_exhausted；preflight、Harness、raw、parser、status、checksum 链条可检查 | `pilot_only`；不支持统计显著性、普遍优越性、speedup、30-seed 代表性或语义完全等价 |

## 6. Harness 与 Original 的统一解释边界

Original 是 Echidna 探索的多笔独立目标交易；Harness 是一次外层 wrapper 调用中连续执行多个目标函数。即使固定成功路径的最终属性结果一致，也不能因此写成两种执行模型完全等价。

论文必须保留以下潜在差异：`msg.sender`、caller alternation、transaction atomicity、rollback scope、`msg.value`、payable behavior、`block.timestamp`、`block.number`、external calls 和 reentrancy。Harness falsified 只能表示在当前 wrapper 执行模型下观察到属性反例；它不自动转化为 Original 多交易语义下完全等价的反例。

`Total calls` 必须按各自的外层计数层次分别报告，不能将 Original 的多交易调用数与 Harness 的 wrapper 调用数当作等量工作，也不能据此声称 speedup。

## 7. 当前可以写、不能写的结论

### 可以写

- V1 是面向显式 Echidna safety property 的属性定向交易序列 Harness synthesis 前处理方法；
- Property、Repeat、Value 和 Top-K 在对应受控障碍上具有可观察、可解释的机制作用；
- Phase 06A 证明 4 个预登记 supported 任务的 runner、preflight、K1/K5 Harness、日志解析和 checksum 产物链在 3-seed pilot 中可完成；
- `exercise2-access-control` 因 `msg.sender`、address-keyed mapping 和 caller alternation 保持 conditional；
- 在窄范围固定成功路径和明确 caller 条件下，可以报告有限的语义适用性/可重放性，但不是全搜索过程等价。

### 不能写

- “V1 普遍优于 Echidna、SMARTIAN、MuFuzz 或 IR-Fuzz”；
- “Phase 06A 的 35/36 证明 Full-K1/Full-K5 更强或更快”；
- “Phase 06A 具有统计显著性”或“3 seed 代表 30 seed”；
- “Total calls 减少就是 speedup”；
- “Harness 与 Original 完全等价”；
- “budget_exhausted 表示 property passed 或 contract safe”；
- “exercise2-access-control 可与 4 个 supported benchmark pooled”；
- “matched-random-v1 可作为新的控制证据”；
- “1050 次运行等于 1050 个独立合约”或据此外推真实生态总体。

## 8. 是否允许进入下一阶段

本阶段 evidence lock 可以结束，允许进入“大阶段 B”的预登记、人工复核和 public-task native replay 准备阶段，但不是正式 30-seed 主实验授权。

进入 B 前必须保持以下门槛：

1. 研究者复核本文件、`SEMANTIC_BOUNDARY_AUDIT.md`、`evidence_index.tsv` 和 closeout；
2. 研究者确认 `scripts/run_v1_public_smoke_case.sh` 的未提交改动只是换行差异，并决定是否单独提交该 Phase 06A runner 变更；
3. public formal batch 继续使用独立 run 目录和预登记 manifest，不写入 frozen results；
4. 先对 supported 任务做逐任务 native replay/语义复核，再决定是否进入正式主表；
5. exercise2 继续单独作为 conditional，不得进入 supported pooled 分母；
6. 不恢复或重新利用 `results/matched-random-v1/`，不把 V2/C2 材料并入 V1。

因此，本阶段没有阻塞“大阶段 B 的审计/复核入口”，但阻塞任何未经人工复核的正式 30-seed 运行和主表提升。
