# 论文版实验目录

这是本项目当前阶段的“单一人工入口”。它把原始仓库中的 V1、B-2、C-1、C-2、V2、C0 和 smoke 材料分成论文主结果、附录、复现材料和排除项。

## 重要规则

- 这里不复制 `results/` 中的 CSV、日志或合约；所有数据仍以原路径为唯一事实来源。
- `manifest.tsv` 是机器可读的白名单，论文制表只应读取它列出的 `include_in_main=yes` 或 `appendix` 条目。
- 原始日志不可手工修改；派生 CSV 应通过固定脚本重建。
- V1 是当前冻结的方法版本；B-2 是 V1 的扩展合成批次；V2 是独立开发线，不能和 V1 主结果混合。
- C-1 是已完成的五个公开基准批次；C-2 目前没有新增候选，SMARTIAN 仅完成两个简单整数目标的外部可执行性批次，不能写成广泛 SOTA 结论。

## 目录

| 入口 | 内容 | 论文角色 |
|---|---|---|
| [`00_PROJECT_SUMMARY.md`](00_PROJECT_SUMMARY.md) | 当前阶段总结、证据、创新点、风险与 Go/No-Go | 首先阅读 |
| [`01_METHOD/`](01_METHOD/) | V1 方法、代码入口和版本边界 | 方法章节 |
| [`02_MAIN_RESULTS/`](02_MAIN_RESULTS/) | Formal、B-2、论文白名单和主表 | 主结果 |
| [`03_PUBLIC_C1/`](03_PUBLIC_C1/) | 五个公开基准、适配和统计 | 主结果/限制 |
| [`04_CONTROLS_AND_ABLATIONS/`](04_CONTROLS_AND_ABLATIONS/) | matched-random、早期消融和 V2 分离规则 | 附录 |
| [`05_SEMANTIC_AND_LIMITS/`](05_SEMANTIC_AND_LIMITS/) | Harness 语义审计、适用范围和限制 | 方法/威胁 |
| [`06_EXTERNAL_BASELINES/`](06_EXTERNAL_BASELINES/) | SMARTIAN 部署、对齐、60 次外部基线运行 | C-2 进展/限制 |
| [`07_REPRODUCIBILITY/`](07_REPRODUCIBILITY/) | 环境、脚本、校验和、重建方法 | 复现 |
| [`08_APPENDIX/`](08_APPENDIX/) | B-2、规模 proxy、机制示意和可条件使用材料 | 附录 |
| [`99_ARCHIVE_RULES.md`](99_ARCHIVE_RULES.md) | 不进入论文主表的目录、快照和归档策略 | 整理规则 |
| [`manifest.tsv`](manifest.tsv) | 文件级论文数据白名单 | 制表入口 |
| [`FREEZE_STATUS.md`](FREEZE_STATUS.md) | 当前冻结范围、验证结果和未决边界 | 冻结入口 |

## 推荐阅读路径

先读 [`00_PROJECT_SUMMARY.md`](00_PROJECT_SUMMARY.md)，再读 [`docs/START_HERE.md`](../docs/START_HERE.md) 和 [`docs/DIRECTORY_GUIDE.md`](../docs/DIRECTORY_GUIDE.md)。写主结果时只从 [`manifest.tsv`](manifest.tsv) 中的主结果条目取数；写附录时再读取 `appendix` 条目。

## 整理结果

除已审计的 NoisyFourStep 历史归档迁移外，目前不再物理移动原始文件。仓库中的脚本、CSV和checksum记录了当前相对路径，继续移动会破坏溯源。无关材料已经通过本目录的 `logical_exclude` 规则从论文视图中剔除；如果以后需要压缩磁盘，再依据 [`99_ARCHIVE_RULES.md`](99_ARCHIVE_RULES.md) 逐类、可恢复地归档。
