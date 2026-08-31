# V1 Restart — Phase 01：仓库、环境与实验入口审计

审计日期：2026-08-31
审计分支：develop
审计范围：V1 方法代码、冻结证据、脚本入口、工具环境和新实验文件治理。

## 1. Phase 01 conclusion

**PASS WITH WARNINGS**。

**Phase 02: ALLOWED**。

Git 基线、环境和新实验隔离入口检查已完成。历史 matched-random provenance 问题已隔离，不再作为 Phase 02 最小 V1 复现的依赖项：

1. 正确激活 contract-fuzz 后，Slither、solc、solc-select 和 Python 均可用；此前的工具缺失结论来自未初始化 conda 的非交互 shell，已更正。
2. develop 工作线和当前 Git 基线正确；新 runner 已将 Original 与 Full-K1 的输出隔离到 work/v1-restart/<run_id>/。
3. 两个 dry-run 均通过，work/ 被 Git ignore，runner 不写冻结 results/，历史 Harness 未被修改。
4. matched-random-v1 的 checksum historical integrity gate 仍为 BLOCKED；该历史控制实验标记为 LEGACY_CONTROL_QUARANTINED，不用于新的论文结论，也不阻塞 Phase 02 最小复现。

因此 Phase 01 最终结论为 PASS WITH WARNINGS，Phase 02 允许开始。此决定不是修复或刷新 checksum，而是明确隔离 unresolved matched-random provenance 的影响范围。本次未运行 Echidna，未修改任何 results/ 内容。

Warning:

    Legacy matched-random-v1 evidence is quarantined because its
    execution-manifest.tsv cannot be reconciled with the 2026-08-06
    freeze checksum and the original freeze Git history is unavailable.
    It must not be used for new paper claims unless independently
    re-established.


## 2. Git baseline

按要求执行了 git fetch --prune、git status --short 和 git branch -a。fetch 没有产生可见的远程更新输出。

| 项目 | 结果 |
|---|---|
| 当前分支 | develop |
| HEAD | fde47062acafe64ea192ccfbe83daea35699568a |
| master | fde47062acafe64ea192ccfbe83daea35699568a |
| develop | fde47062acafe64ea192ccfbe83daea35699568a |
| 工作区 | clean；git status --short 无输出 |
| 未跟踪且未被忽略的文件 | 无 |
| 异常未跟踪大文件 | 未发现 |
| 当前 ignored 运行文件 | 未发现 |

.gitignore 已覆盖 work/、results/_work/、results/_runtime/、results/_scratch/、Python cache、.tools/、baselines/smartian/、crytic-export/、正式 overhead artifacts 和 checkpoints/*.tar.gz。逐项 git check-ignore 检查通过。本阶段未修改 .gitignore。

## 3. Environment matrix

以下只做版本、路径和可执行性检查，不启动 fuzzing 或编译实验。

| 工具/环境 | 当前结果 | 状态 | Phase 02 影响 |
|---|---|---|---|
| OS | WSL2 Ubuntu-20.04；Linux 6.18.33.2-microsoft-standard-WSL2 | AVAILABLE | 平台存在 |
| Shell | WSL /bin/bash；外层 PowerShell 7.6.4 | AVAILABLE | 应固定使用 WSL |
| contract-fuzz/python | /home/skk/miniconda3/envs/contract-fuzz/bin/python，3.11.15 | AVAILABLE | V1 分析器可用 |
| contract-fuzz/python3 | /home/skk/miniconda3/envs/contract-fuzz/bin/python3，3.11.15 | AVAILABLE | 与环境内 python 一致 |
| Windows python | D:\Python程序\python.exe，3.10.6 | AVAILABLE | 不应与 WSL 混用 |
| Slither | /home/skk/miniconda3/envs/contract-fuzz/bin/slither，0.11.5；slither-analyzer 同版本 | AVAILABLE | 可执行 RW、Value、Harness 分析 |
| solc | /home/skk/miniconda3/envs/contract-fuzz/bin/solc，0.8.20+commit.a1b79de6 | AVAILABLE | 可做当前版本编译预检 |
| Echidna | /usr/local/bin/echidna，2.3.2 | AVAILABLE | 可执行 fuzzing；仍需固定运行参数 |
| Git | WSL 2.25.1；Windows 2.40.0.windows.1 | AVAILABLE | 基线已完成 |
| conda / contract-fuzz | conda env list 显示 contract-fuzz *，路径为 /home/skk/miniconda3/envs/contract-fuzz | AVAILABLE | 需通过 bash -lic 'conda activate contract-fuzz' 固定入口 |
| solc-select | /home/skk/miniconda3/envs/contract-fuzz/bin/solc-select；可见 0.4.23、0.4.25、0.8.20，当前 0.8.20 | AVAILABLE | 可做版本切换；不支持 --version 参数 |
| Docker | Windows 命令可见；本阶段未使用 | AVAILABLE/未验证 | 不代表实验容器可复现 |

本次只读复核是在 bash -lic 'conda activate contract-fuzz' 中完成的；conda env list 将 contract-fuzz 标为 active，并确认 CONDA_PREFIX=/home/skk/miniconda3/envs/contract-fuzz、CONDA_DEFAULT_ENV=contract-fuzz，且 python、Slither、solc、solc-select 均解析到该环境。不能把 Windows Python、系统 WSL Python 和该环境混用。

执行 sha256sum -c --quiet results/paper-data/input-checksums.sha256 的结果是：baselines/smartian/DEPLOYMENT_STATUS.md 缺失，另有 11 个现存文件不匹配。git status 仍干净，说明不是本次审计造成的未提交修改；本阶段不修复或刷新清单。

## 4. V1 pipeline

    Contract
    → RW extraction
    → Dependency
    → Property
    → Repeat
    → Value
    → Top-K
    → Harness
    → Echidna
    → raw log
    → parser
    → statistics

### Contract 与属性

输入为 Solidity 合约和以 echidna_ 开头的零参数属性函数。属性函数不作为普通交易步骤；Harness 生成属性代理。

### RW extraction：analyzer/extract_rw.py

Slither 收集 public/external 函数，排除 constructor、fallback、receive，包含继承函数。每个函数输出状态变量 read/write 集合；优先使用递归 all_state_variables_read/all_state_variables_written，异常时回退。变量优先 canonical_name。

输出只描述静态读写关系，不描述参数值、调用者、交易边界、可达性或回滚结果。

### Dependency：analyzer/generate_sequences.py

若 f1 写入的变量被 f2 读取，则建立 f1 → f2 边；分数为 2 × write-read 数量 + write-write 数量，但没有 write-read 的纯 write-write 关系不建边。DFS 生成长度 2 到 max_length 的路径，不允许函数重复，再按分数、长度、序列排序去重。analyze_contracts() 可在此执行 paths[:top_k]。

### Property：analyzer/generate_property_sequences.py

先收集 echidna_ 属性读取的状态变量，再选出写入这些变量的普通函数作为目标，只保留最终到达目标函数的路径。它比 Dependency 增加属性相关过滤，但仍是函数名和集合交集的启发式；复杂间接读取或非直接 write-read 关系可能漏掉。这里也可 paths[:top_k]。

### Repeat：analyzer/generate_repetition_aware_sequences.py

从写入属性变量的目标函数反向遍历 predecessor，把前驱插入路径开头；max-function-visits、max_path_length 和 max_expansions 共同限制 DFS。Formal 使用 max-function-visits=2。它覆盖 deposit() 等必须重复调用的障碍，但不是完整可达性分析，有界参数会改变候选集合。

### Value：analyzer/extract_value_constraints.py 与 analyzer/generate_value_guided_sequences.py

Value 提取器再次使用 Slither，但用文本节点和正则识别简单常量写入及 require 比较，只支持少量整数、布尔、地址和比较形式；算术、mapping、函数调用、复杂控制流和完整跨函数数据流属于 unsupported 或 unknown。

排序器逐个检查相邻函数：写入常量满足后继 requirement 是 match，确定违反是 conflict，不能确定是 unknown。默认 match 加 4、conflict 减 4，unknown 不调整；再按 value_score 等字段排序。因此 Value 是启发式方向匹配，不是可达性证明。

### Top-K 与排除风险

Top-K 可能发生在 Dependency、Property、Repeat 的生成器，Value 的可选 top-k，以及 Harness 的 load_paths() 最终 path_entries[:top_k]。正确路径可能因 write-read 过滤、禁止重复、路径/扩展上限、Value 只支持简单常量、并列顺序或最终 K1/K5 截断而消失。C-1 的 exercise2-access-control K1 失败而 K5 成功是现有证据。

### Harness：analyzer/generate_harness_from_paths.py

Harness 用 Slither 查找目标函数，按候选序列生成 public wrapper，连续调用目标函数并生成参数；constructor 部署目标合约，属性 proxy 转发到目标属性。mapping/function 参数和带参数 constructor 不支持。

多个目标调用被包装在一次外部调用内，没有逐步 caller、msg.value 或多交易边界控制。这会改变 msg.sender、原子性、回滚范围、区块环境、资金流和外部调用语义。因此 Harness 结果不能与 Original 多交易执行视为完全等价，也不能直接用外层 Total calls 证明等量加速。

### Echidna 与派生统计

Formal 配置为 testLimit=100000、timeout=30、workers=1、stopOnFail=true；Original seqLen=4，Harness seqLen=1。raw log 应未手工修改并带 seed、时间、退出码和完成/错误状态；parse_experiment_logs.py 生成逐运行 CSV，汇总脚本生成分组统计。budget_exhausted 只表示预算内未发现反例，不表示属性通过或合约安全。

实际入口关系：

- prepare_formal_candidate_counts.sh：RW → Dependency/Property/Repeat → Value → Full JSON，固定写 results/formal/candidates/；
- prepare_formal_full.sh：读取既有 RW → Repeat → Value → Full → Harness → solc，固定写 Formal preparation/Harness；
- prepare_formal_b2.sh：RW → Repeat → Value → Full → K1/K2 Harness → solc；
- prepare_public_c1.sh：源码 solc 预检 → RW → Repeat → Value → Full → K1/K5 Harness → solc；
- run_formal_experiments.sh、run_formal_b2.sh、run_public_c1.sh：固定 manifest，调用 Echidna，写冻结 results/.../runs/；
- rebuild_*_derived_results.sh：不启动 Echidna，但可能覆盖 tracked 派生结果。

## 5. Frozen evidence

| 区域 | 实际内容与角色 |
|---|---|
| results/formal/ | runs 450 份 raw log；parsed 4、candidates 24、preparation 12；Formal 主证据 |
| results/formal-b2/ | runs 150 份 raw log；parsed 2、preparation 8；B-2 扩展/附录 |
| results/public-benchmarks/c1/ | runs 450 份 raw log；parsed 5、preparation 80、statistics；C-1 主证据 |
| results/paper-data/ | whitelist、2221 行 checksum、六基准摘要、ranking、scale proxy、workspace freeze；论文逻辑入口 |
| paper-ready/manifest.tsv | 唯一来源、证据角色、主文/附录/排除规则 |

runs/ 是原始证据，不能手工修改；parsed/grouped/summary/statistics/candidate summary 是可由固定脚本重建的派生结果。论文制表必须以 dataset-whitelist.csv 和 manifest.tsv 为准，不能递归扫描全 results/。

明确排除：results/v2/、V2/native-corpus；C0 和 c0-before-compat-fixes；C-1 smoke；runner-output.log；three-step、ablation、mechanism 等旧 pilot/手工示意；results/formal/overhead-v2/；混杂 Noisy random；checkpoint 和历史快照。paper-data 中的 v2-native-ablation-summary.csv 仍是 V2 条件性附录，不得并入 V1 主结果。

冻结完整性警告：checksum 文件存在，但当前验证不是全通过；在研究者复核前，不能声称 checksum 链完整通过，也不应更新清单掩盖差异。

## 6. Script classification

### derived-only

- scripts/rebuild_formal_derived_results.sh
- scripts/rebuild_formal_b2_derived_results.sh
- scripts/rebuild_public_c1_derived_results.sh
- scripts/rebuild_semantic_applicability_v1.sh
- scripts/rebuild_c2_readiness.sh

它们不启动 Echidna，但写固定 results/...，所以本阶段未调用。

### prepare

- scripts/prepare_formal_candidate_counts.sh：写 results/formal/candidates/；
- scripts/prepare_formal_full.sh：写 results/formal/preparation/ 和 contracts/harnesses/formal/；
- scripts/prepare_formal_b2.sh：写 B2 preparation/Harness；
- scripts/prepare_public_c1.sh：写 C-1 preparation/Harness；
- scripts/rebuild_matched_random_v1_preflight.sh：生成随机 schedule/Harness 并做 solc preflight，不是纯只读；
- scripts/prepare_v2_ranking_regression.sh：V2，不能调用。

### execute

V1 正式入口：

- scripts/run_formal_experiments.sh：固定写 results/formal/runs/，每组 30 seed；
- scripts/run_formal_b2.sh：固定写 results/formal-b2/runs/，每组 30 seed；
- scripts/run_public_c1.sh：固定写 results/public-benchmarks/c1/runs/，每组 30 seed。

控制/外部/历史入口：

- run_semantic_differential_v1.sh、run_semantic_trace_replays_v1.sh：固定写 semantic-applicability；
- run_smartian_formal_baseline.sh：固定写 C2 screening，并硬编码 /home/skk/.solc-select/artifacts/solc-0.4.25/solc-0.4.25；
- smoke_public_c1.sh：smoke，排除；
- run_noisy_four_step.sh、run_property_ablation.sh、run_branch_value.sh、run_reset_example.sh、run_repeated_call_ablation.sh、run_dependency_k_ablation.sh、run_dependency_k6_ablation.sh、run_permutation_baseline.sh、run_three_step.sh、run_value_invariance.sh：历史/消融/控制，不进入 V1 主分母。

scripts/resolve_repo_root.sh 能从脚本位置通过 Git 解析根目录。多数脚本也计算 SCRIPT_DIR/PROJECT_ROOT，但都没有通用 output-root 参数。

## 7. File-output audit

规范要求新增运行使用 work/v1-restart/<run_id>/，包含 manifest.tsv、command.txt、environment.txt、generated/、raw/、parsed/、summary/、status/；work/ 已被 .gitignore 隔离。

历史 Formal/B2/C-1 入口仍不安全：没有 output-root 参数，默认写冻结 results/；prepare 脚本默认写冻结 preparation/Harness；部分历史脚本含 rm -f seed-*.log。新 runner 独立使用 work/v1-restart/<run_id>/，不复用这些历史入口；两个 dry-run 未向冻结目录写入任何文件。

## 8. Warnings and quarantined legacy issues

1. EXPECTED_EXTERNAL_MISSING：独立 SMARTIAN 工作区的部署说明不在 fresh clone 中，不恢复伪文件。
2. CRITICAL_FROZEN_EVIDENCE_MISMATCH：results/matched-random-v1/execution-manifest.tsv 的 hash 与冻结记录不同；该 manifest 被正式运行使用。历史 matched-random 控制实验标记为 LEGACY_CONTROL_QUARANTINED，不得用于新的论文结论；该问题不阻塞 Phase 02 最小 V1 复现。
3. SMARTIAN 脚本仍有旧绝对路径；不阻塞 NoisyFourStep 最小复现，但阻塞通用迁移复现。

没有自动修复、安装/升级工具、重建派生结果、重生成 Harness、修改结果或提交。

## 9. Phase 02 recommended command path

Phase 02 只做 NoisyFourStepExample 的一个最小可检查单元：研究问题是隔离目录中的 Original 与 Full-K1 能否按 V1 口径完成最小复现；输入为 contracts/benchmarks/NoisyFourStepExample.sol、固定 V1 配置和 Full-v1.0；输出根为 work/v1-restart/<run_id>/；需要重新运行 Slither、V1 分析器、solc 和两次 Echidna。本 Phase 01 Fix 已完成 dry-run，但没有执行正式实验。

- 1 个 Original seed，configs/formal-original-seq4.yaml；
- 1 个 Full-K1 seed，configs/formal-harness-seq1.yaml；
- RW、Repeat/Value/Full JSON、临时 Harness、编译输出、两份 raw log、解析和状态文件全部进入该 run_id；
- 使用 scripts/run_v1_restart_case.sh；它从 scripts/resolve_repo_root.sh 解析根目录，拒绝不安全 run-id 和已存在 run-id，并将 Full-K1 中间文件全部写入本次 generated/。
- 后续正式运行仍须复核 manifest.tsv、environment.txt、command.txt、status/ 和 checksums.sha256；保持 benchmark、属性、K、testLimit、timeout、workers、stopOnFail 和排除规则不变。

启动前人工复核 manifest.tsv 是否记录 commit、method、contract、property、config、compiler、seed、testLimit、timeout、workers、stopOnFail，以及 RW/候选路径/Top-K/Harness 和 completed/error 分类。budget_exhausted 仍只能表示预算内未发现反例。

## Isolated restart runner

新入口为 scripts/run_v1_restart_case.sh，仅支持 noisy-four-step 的 original 和 full-k1。它必须在 contract-fuzz 已激活且 CONDA_PREFIX/CONDA_DEFAULT_ENV 正确时运行，并通过 scripts/resolve_repo_root.sh 解析仓库根目录。

每个 run-id 只允许使用安全字符，目标目录必须是 work/v1-restart/<run_id>/ 的绝对路径之下；已有 run-id 默认拒绝覆盖，不自动删除。Original 使用 contracts/benchmarks/NoisyFourStepExample.sol 与 formal-original-seq4.yaml。Full-K1 从同一原始合约重新生成 generated/rw.json、repeat-property-sequences.json、value-constraints.json、full-sequences.json 和 Full-K1 Harness，不读取旧 results/noisy-four-step/NoisyFourStepExample-rw.json。

两个 dry-run 均成功：

- phase01-dry-original：status/status.env 为 DRY_RUN=1、STATUS=dry_run、EXIT_CODE=0。
- phase01-dry-full-k1：status/status.env 为 DRY_RUN=1、STATUS=dry_run、EXIT_CODE=0。

两次 dry-run 均创建 manifest.tsv、command.txt、environment.txt、generated/、raw/、parsed/、summary/、status/；command.txt 中所有计划输出均指向本次 work/v1-restart run。dry-run 未执行 Slither、solc、Echidna，未生成临时 Harness，未写入 results/ 或 contracts/harnesses/formal/。实际模式预留 raw/seed-<seed>.log、status/status.env、status/checksums.sha256，并区分 completed、budget_exhausted、startup_error、unknown_error；budget_exhausted 不表示 property passed。

## Checksum reconciliation

逐项结果见 docs/v1-restart/PHASE_01_CHECKSUM_AUDIT.md。该报告记录了每个异常的 expected SHA、actual SHA、精确路径和分类：1 个 EXPECTED_EXTERNAL_MISSING、10 个 DERIVED_RESULT_MISMATCH、1 个 CRITICAL_FROZEN_EVIDENCE_MISMATCH。三份历史冻结记录没有被修改，派生文件没有在本阶段重建。

Checksum historical integrity gate: BLOCKED for matched-random reuse

V1 Restart execution gate: PASS WITH WARNINGS

matched-random-v1 remains PROVENANCE_UNRESOLVED and LEGACY_CONTROL_QUARANTINED; it is not a dependency of the Phase 02 minimal V1 reproduction and must not be used for new paper claims without independent re-establishment.

因此 Phase 01 最终结论为 PASS WITH WARNINGS，Phase 02: ALLOWED。此处仅允许进入 Phase 02，Closeout 本身未启动任何实验；不得修改 frozen results。
