# C2公开属性基准预注册与筛选

## 当前状态

本目录用于扩充C-1的5个公开目标。当前已完成预注册规则、本地可用性审计、SMARTIAN 对齐和外部基线批次；**尚未加入新的C2候选，也没有运行正式C2 fuzzing**。

- `source-pools.tsv`：允许使用的公开来源池和本地可用状态；
- `candidate-registry.tsv`：候选级来源、属性、语义和冻结状态；
- `baseline-feasibility.csv`：早期本地比较工具可用性快照；
- `baseline-feasibility-report.md`：早期公平性与Go/No-Go结论；
- `baseline-feasibility-v2.csv`：2026-08-06 刷新的本地审计结果；
- `baseline-feasibility-report-v2.md`：当前外部基线 Go/No-Go 结论；
- `baseline-feasibility-v3.csv`：SMARTIAN 主仓库部署后的最新审计结果；
- `baseline-feasibility-report-v3.md`：当前 SMARTIAN 部署状态与外部基线 Go/No-Go 结论；
- `baseline-feasibility-v4.csv` / `baseline-feasibility-report-v4.md`：排除 `.git` 元数据后的最新审计口径；
- `baseline-feasibility-v7.csv` / `baseline-feasibility-report-v7.md`：SMARTIAN 构建与 smoke 成功后的最新审计口径；
- `smartian-deployment.json`：SMARTIAN 部署版本、SDK、子模块和构建阻塞状态；
- `smartian-calibration.tsv` / `smartian-calibration-summary.json`：3个官方样例的5秒可运行性校准及重复性摘要，不是正式检测率结果；
- `smartian-calibration-repeatability.tsv`：每个样例3次重复运行的完整性与告警观察；
- `smartian-oracle-alignment.tsv` / `smartian-oracle-alignment.json`：两个 SmartBugs 整数属性的独立重放对齐结果，以及其余候选的阻塞原因；
- `SMARTIAN_ORACLE_ALIGNMENT.md`：预言机对齐证据、重放结果和正式纳入门槛；
- `SMARTIAN_FORMAL_FREEZE_PROPOSAL.md` / `smartian-formal-freeze-proposal.json`：正式外部基线批次的冻结参数、范围和完成状态；
- `smartian-formal-20260806/`：按冻结参数完成的 2×30 外部基线原始日志和摘要；不计入 C2 分母；
- `smartian-vs-c1-descriptive.csv` / `.json` / `SMARTIAN_VS_C1_REPORT.md`：SMARTIAN 与现有 C-1 结果的描述性对照，不计算跨工具速度或显著性；
- `SMARTIAN_CALIBRATION.md`：校准条件、结果解释和进入正式实验的门槛；
- `environment.json` / `environment-v2.json` / `environment-v3.json`：对应审计时的本地工具版本。

## 纳入流程

候选必须依次经过：

1. `identified`：先登记来源、commit和source path；
2. `source_available`：源码和依赖已保存在本地；
3. `compiled`：使用固定编译器成功编译；
4. `property_validated`：属性来源明确，已知反例可独立重放；
5. `semantic_supported`：通过Harness语义静态筛查；
6. `frozen_for_c2`：合同、属性、适配补丁、K、预算和seed全部冻结；
7. 冻结后才能把`fuzzing_status`从`not_started`改为运行状态。

任何阶段都可以标记为`excluded`，但必须填写排除原因。不得因为V1运行失败而排除目标。

## 纳入条件

- 公开来源、许可证和不可变版本可追溯；
- 属性由上游提供，或按预先冻结的统一规则从公开漏洞标签构造；
- 已知反例至少需要两个状态改变步骤；
- 能在冻结的本地编译环境中构建；
- 通过语义筛查，或明确作为conditional/unsupported单列；
- 分析、Harness生成、编译和启动失败均保留在端到端分母。

## 当前限制

本机只有现有5个C-1公开目标的局部源码，没有完整Echidna、Building Secure Contracts、SmartBugs或可复用属性数据集。因此在不联网、不下载的约束下，无法诚实地把目标扩充到12–20个。当前5行均标记为`legacy_reference`，因为它们在本预注册流程建立前已经完成C-1实验，不能追溯性地伪装成预注册样本。

2026-08-06 的部署已完成：SMARTIAN 固定 commit、必要 Nethermind/B2R2 源码和 Dirichlet 依赖均已展开，Release 构建生成 `src/bin/Release/net8.0/Smartian.dll`，并用仓库自带 `IB` 示例完成 1 秒 fuzz smoke。随后对 `IB`、`BD_false`、`MS_true` 各完成 5 秒校准，均正常退出；两个 SmartBugs 整数属性按 C-1 的 0.4.25 编译器完成 SMARTIAN/Echidna 对齐，随后各运行 30 次、每次 30 秒的正式外部基线批次，60/60 次均发现 `IntegerBug`。B2R2 的失效 `docs` 子模块被明确跳过。结果作为 C-1 外部工具对照保存，未改变 C2 候选注册表或分母。部署过程和恢复命令见[`baselines/smartian/DEPLOYMENT_STATUS.md`](../../baselines/smartian/DEPLOYMENT_STATUS.md)。

## 验证命令

```bash
python3 analyzer/validate_c2_candidate_registry.py \
  --registry results/public-benchmarks/c2-screening/candidate-registry.tsv

python3 analyzer/audit_baseline_feasibility.py \
  --output-csv results/public-benchmarks/c2-screening/baseline-feasibility.csv \
  --report results/public-benchmarks/c2-screening/baseline-feasibility-report.md \
  --environment results/public-benchmarks/c2-screening/environment.json

# 当前快照（不联网、不安装）
python3 analyzer/audit_baseline_feasibility.py \
  --output-csv results/public-benchmarks/c2-screening/baseline-feasibility-v2.csv \
  --report results/public-benchmarks/c2-screening/baseline-feasibility-report-v2.md \
  --environment results/public-benchmarks/c2-screening/environment-v2.json

# SMARTIAN 主仓库部署后的最新快照
python3 analyzer/audit_baseline_feasibility.py \
  --output-csv results/public-benchmarks/c2-screening/baseline-feasibility-v3.csv \
  --report results/public-benchmarks/c2-screening/baseline-feasibility-report-v3.md \
  --environment results/public-benchmarks/c2-screening/environment-v3.json

# 排除 Git 元数据后的最新快照
python3 analyzer/audit_baseline_feasibility.py \
  --output-csv results/public-benchmarks/c2-screening/baseline-feasibility-v4.csv \
  --report results/public-benchmarks/c2-screening/baseline-feasibility-report-v4.md \
  --environment results/public-benchmarks/c2-screening/environment-v4.json
```

上述命令只读取本地文件和本地命令版本，不联网、不安装，也不运行漏洞发现实验。
