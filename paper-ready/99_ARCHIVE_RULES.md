# 99 归档与排除规则

## 当前策略：逻辑剔除，冻结后不再移动

本次整理原则上采用逻辑剔除。唯一已经发生的物理迁移是：`results/noisy-four-step/` 的163个历史文件迁移到 `results/paper-data/noisy-four-step/`；冻结前已将迁移后文件与Git基线逐项比较，163/163内容一致。其余原始结果不再搬动，因为现有脚本、CSV和checksum使用当前相对路径；继续大规模移动会让重建、溯源和论文制表产生隐性错误。论文视图中的“排除”由 `manifest.tsv` 和本文件实现。

如果以后确实需要节省磁盘，必须先：

1. 生成全仓库路径清单和 checksum；
2. 逐类移动到明确的 `results/_archive/<date>/`；
3. 更新所有引用和重建脚本；
4. 在归档目录保留原相对路径、原因和恢复说明；
5. 重新运行验证，再删除任何副本。

## 默认排除类别

| 类别 | 路径 | 原因 |
|---|---|---|
| V2 开发线 | `results/v2/`、`analyzer/v2/` | 未冻结，不能覆盖 V1 结论 |
| V2 native pilot | `results/native-corpus-seed-v1/`、`results/native-corpus-seed-v2-serial/`、`results/native-corpus-seed-fair/` | 独立方法线；只按明确附录规则使用 |
| 兼容性旧批次 | `results/public-benchmarks/c0/`、`results/public-benchmarks/c0-before-compat-fixes/` | 不是正式性能实验，部分为兼容修复前结果 |
| 启动/编排 | `results/public-benchmarks/c1/smoke/`、各批次 `runner-output.log` | 不进入运行分母 |
| 早期 pilot | `results/three-step/`、`results/ablation/`、`results/mechanism/` | seed、预算或 Harness 口径不同 |
| 混杂随机 | `results/paper-data/noisy-four-step/random/`、`random-sequences.csv` | 同时改变序列和 seed，不能作为受控随机基线 |
| 不完整开销 | `results/formal/overhead-v2/` | 已明确标记为临时 partial |
| 历史快照 | `checkpoints/*.tar.gz`、`baseline-feasibility-report-v2..v6.md`、`baseline-feasibility-v2..v6.csv`、`environment-v2..v6.json` | 仅保留历史 provenance；当前入口使用最新审计文件 |

## 当前有效的 C-2 文件

C-2 目录中的 `baseline-feasibility-report-v7.md`、`baseline-feasibility-v7.csv`、`environment-v7.json`、candidate registry 和 SMARTIAN 对齐/正式批次属于最新审计链；旧版本不应在论文中引用为当前结论。

## 清理 `__pycache__` 和生成物

`analyzer/__pycache__/`、临时 `.log` 和局部编译输出不属于论文材料。它们可以在确认没有被实验脚本作为输入后单独清理；本次不执行删除，以免误删用户正在使用的中间文件。
