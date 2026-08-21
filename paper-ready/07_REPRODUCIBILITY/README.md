# 07 复现与数据溯源

## 数据原则

- 原始日志：`results/*/runs/`，不可修改。
- 派生表：`parsed/`、`grouped/` 和 `statistics/`，由固定脚本重建。
- 论文入口：[`results/paper-data/dataset-whitelist.csv`](../../results/paper-data/dataset-whitelist.csv)。
- 冻结校验：[`results/paper-data/input-checksums.sha256`](../../results/paper-data/input-checksums.sha256)。
- 全工作区文件盘点：[`results/paper-data/repository-files.tsv`](../../results/paper-data/repository-files.tsv)。
- 冻结环境与范围摘要：[`results/paper-data/repository-freeze.json`](../../results/paper-data/repository-freeze.json)。

## 只重建派生数据

- [`scripts/rebuild_formal_derived_results.sh`](../../scripts/rebuild_formal_derived_results.sh)
- [`scripts/rebuild_formal_b2_derived_results.sh`](../../scripts/rebuild_formal_b2_derived_results.sh)
- [`scripts/rebuild_public_c1_derived_results.sh`](../../scripts/rebuild_public_c1_derived_results.sh)
- [`scripts/rebuild_semantic_applicability_v1.sh`](../../scripts/rebuild_semantic_applicability_v1.sh)

## 会重新运行实验

`prepare_*`、`run_*` 和 `smoke_*` 脚本可能写入 Harness、日志或运行目录。执行前先阅读脚本，并确认不会覆盖冻结证据；SMARTIAN 外部批次入口是 [`scripts/run_smartian_formal_baseline.sh`](../../scripts/run_smartian_formal_baseline.sh)。

## 环境记录

- Formal：[`results/formal/environment.txt`](../../results/formal/environment.txt)。
- C-1：[`results/public-benchmarks/c1/statistics/README.md`](../../results/public-benchmarks/c1/statistics/README.md)。
- SMARTIAN：[`results/public-benchmarks/c2-screening/smartian-deployment.json`](../../results/public-benchmarks/c2-screening/smartian-deployment.json) 和 [`baselines/smartian/DEPLOYMENT_STATUS.md`](../../baselines/smartian/DEPLOYMENT_STATUS.md)。

## 重建后的核对

重建后应重新运行相应验证脚本，并检查 `git diff --check`、JSON/CSV 可解析性以及论文白名单中的路径仍然存在。不要把生成的 `__pycache__/` 当作论文材料。

全工作区盘点会记录本地SDK、第三方嵌套仓库、缓存和历史checkpoint的文件状态，但这些类别不进入论文证据白名单，也不直接提交到主仓库。Git冻结提交负责保存项目管理范围；全工作区inventory负责记录其余本地资产。
