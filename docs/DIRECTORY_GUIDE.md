# 目录与重要文件说明

## 先记住五种文件

| 类型 | 典型内容 | 是否可直接修改 |
|---|---|---|
| 原始证据 | `runs/seed-*.log`、manifest、实验时使用的合约和配置 | 不应修改 |
| 派生结果 | `parsed/`、`grouped/`、summary和statistics CSV | 可以通过固定脚本重建 |
| 方法代码 | `analyzer/` | 修改后必须重新验证，不能与旧实验结果混称同一版本 |
| 执行脚本 | `scripts/` | 有些只重建数据，有些会重新运行实验，使用前必须区分 |
| 历史材料 | 旧pilot、C0、smoke、V2开发结果 | 不进入V1主结论 |

论文数据的机器白名单是 [dataset-whitelist.csv](../results/paper-data/dataset-whitelist.csv)。自动制表不应递归扫描整个 `results/`。

## 顶层目录

| 目录 | 用途 | 论文角色 | 平时是否需要读 |
|---|---|---|---|
| `analyzer/` | 静态分析、路径生成、Harness生成、解析和统计 | 方法实现 | 需要理解主要入口，不必逐行背诵 |
| `contracts/` | 合成合约、公开合约、Harness | 实验对象与生成物 | 需要阅读核心基准和正式Harness |
| `configs/` | Echidna测试预算与序列长度 | 实验配置 | 需要知道正式配置差异 |
| `scripts/` | 准备、运行、重建数据 | 流程入口 | 执行前必须确认是否会重跑实验 |
| `results/` | 原始日志、派生表、审计和统计 | 实验证据 | 主要阅读正式白名单目录 |
| `sum/` | 阶段总结 | 历史研究笔记 | 可作背景，不能替代原始数据 |
| `docs/` | 给项目作者阅读的导航文档 | 人类入口 | 从这里开始 |

## contracts/

### `contracts/benchmarks/`

六个主要合成基准：

- `NoisyFourStepExample.sol`
- `ResetExample.sol`
- `BranchValueExample.sol`
- `RepeatedCallExample.sol`
- `AlternativePathExample.sol`
- `MultiPropertyExample.sol`

它们是理解方法组件最适合的入口，但属于受控合约，不代表真实工程规模。

### `contracts/public-benchmarks/`

- `raw/`：公开案例的本地来源版本。
- `adapted/`：为了兼容 Echidna 属性接口或编译环境而适配的版本。

适配内容必须在论文中披露，说明是否改变了目标状态转移。

### `contracts/harnesses/`

包含多个批次和方法的 Harness。正式论文主数据主要使用 manifest 中明确引用的 Harness：

- `contracts/harnesses/formal/`
- `contracts/harnesses/formal-b2/`
- `contracts/harnesses/public-c1/`

其他目录多为组件消融、早期批次或手工机制演示，不能自动合并。

## analyzer/

方法主流程大致对应：

| 文件 | 作用 |
|---|---|
| `extract_rw.py` | 提取函数的状态读写集合 |
| `generate_sequences.py` | 生成基础状态依赖序列 |
| `generate_property_sequences.py` | 根据安全属性相关状态筛选序列 |
| `generate_repetition_aware_sequences.py` | 允许有界重复函数访问 |
| `extract_value_constraints.py` | 提取简单写入和条件约束 |
| `generate_value_guided_sequences.py` | 根据值匹配、冲突重新排序 |
| `generate_harness_from_paths.py` | 将Top-K候选序列生成Solidity Harness |
| `parse_experiment_logs.py` | 将原始Echidna日志解析为逐运行CSV |
| `summarize_experiment.py` | 生成分组统计 |
| `analyze_public_c1_statistics.py` | C-1的Wilson、McNemar、KM和log-rank分析 |

`analyzer/v2/` 属于开发中方法，不进入冻结的V1结论。

## scripts/

需要严格区分两类脚本：

### 只重建派生数据

- `rebuild_formal_derived_results.sh`
- `rebuild_formal_b2_derived_results.sh`
- `rebuild_public_c1_derived_results.sh`

这些脚本读取已有日志并重建CSV，不应运行Echidna。

### 会准备或重新运行实验

- `prepare_formal_full.sh`
- `run_formal_experiments.sh`
- `prepare_formal_b2.sh`
- `run_formal_b2.sh`
- `prepare_public_c1.sh`
- `run_public_c1.sh`

运行它们可能重新生成Harness或写入 `runs/`，在冻结数据前后都不能随意执行。

## results/formal/

V1四个正式合成基准的主批次：

- `runs/`：450份原始日志，不可修改。
- `parsed/`：逐运行解析结果，可重建。
- `grouped/`：按方法分组的摘要，可重建。
- `formal-group-summary.csv`：15个实验组的总表。
- `candidates/`：四个基准各阶段候选JSON，是排名证据。
- `formal-candidate-summary.csv`：路径数量和display rank。
- `formal-tie-aware-ranking.csv`：并列感知排名。
- `environment.txt`：Formal主批次环境记录。
- `overhead/`：四个小型合约的预处理与编译开销。

## results/formal-b2/

两个扩展合成基准：

- AlternativePath：验证多条可行路径。
- MultiProperty：验证同一合约多个属性。

`runs/` 共150份日志。B2缺少独立环境快照，因此可以用于扩展证据，但必须披露 provenance 限制。

## results/public-benchmarks/c1/

五个公开基准的正式批次：

- `runs/`：450份原始日志。
- `parsed/`、`grouped/`：统一状态语义后的派生数据。
- `public-c1-group-summary.csv`：15组结果。
- `c1-path-preflight.csv`：已知有效路径是否进入K1/K5。
- `statistics/`：Wilson区间、配对检验、KM/log-rank和报告。
- `adaptations.md`：公开案例适配说明。
- `data-semantics.md`：状态和指标定义。

`c0/` 是兼容性筛查，不是正式性能实验；`smoke/` 和 `runner-output.log` 也不进入分母。

## results/paper-data/

这是最终论文制表的逻辑入口：

- `dataset-whitelist.csv`：哪些数据可用于主表、附录或必须排除。
- `synthetic-six-benchmark-summary.csv`：六个合成基准Original/Full-K1主比较。
- `synthetic-six-overall-descriptive.csv`：仅描述性的总体计数。
- `ranking-interpretation.md`：display rank和tie-aware rank的正确解释。
- `input-checksums.sha256`：冻结证据的逐文件校验值。

这里不是新的原始数据源，而是经过审计后的论文入口。

## 附录或早期目录

| 目录 | 可使用内容 | 限制 |
|---|---|---|
| `results/ablation-k/` | Noisy Dependency Top-K机制 | 早期独立批次 |
| `results/branch-value/` | Value和Top-K消融 | 不与Formal同名日志合并 |
| `results/reset-example/` | 早期Property Top-K | 不能使用严格rank下降叙述 |
| `results/repeated-call/repeat-ablation/` | visits1/visits2机制 | timeout与Formal不同 |
| `results/value-invariance/` | 重命名和声明顺序稳健性 | 只有一个设计基准 |
| `results/paper-data/noisy-four-step/` | permutation机制的历史归档 | random基线存在混杂，不作正式性能基线；该目录由旧路径逐文件等内容迁移 |

## 当前应排除的目录

- `results/v2/`：开发中。
- `results/public-benchmarks/c0-before-compat-fixes/`：兼容修复前记录。
- C0、smoke和runner-output：启动或编排记录。
- `results/mechanism/`：少量或手工Harness示意。
- `results/three-step/`、`results/ablation/`：早期pilot。
- Noisy random：每次同时改变序列和seed，不能作为受控随机基线。

## 路径冻结规则

许多脚本和CSV记录了现有相对路径。除已经审计的 NoisyFourStep 历史归档外，不再移动实验目录。继续移动会造成：

- 重建脚本找不到输入；
- 日志中的路径与文件位置不一致；
- 同一数据被复制后出现两个“真相来源”；
- 已生成的checksum失效；
- 论文制表误读旧目录。

`results/noisy-four-step/` 的163个旧文件已逐文件、等内容迁移到 `results/paper-data/noisy-four-step/`，冻结审计确认163/163内容一致；旧运行脚本仍保留原输出路径，仅用于未来重新运行，不是当前归档读取入口。在开题和论文初稿完成前，其余目录通过本说明和白名单进行逻辑整理，不再大规模移动。
