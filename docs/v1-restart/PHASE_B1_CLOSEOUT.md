# 大阶段 B1：Closeout

## 1. 基线核验

- 当前分支：`develop`；
- 当前 HEAD：`ac9f08f43997eeb1bae5913cd9326f466d8e5476`；
- 最近提交：`docs: lock V1 paper evidence and semantic audit`；
- `HEAD -> develop` 与 `origin/develop` 均指向该提交；
- 工作区在 B1 开始时已有 `scripts/run_v1_public_smoke_case.sh` tracked 差异。

## 2. runner warning 处理

当前 `git status --short` 仍报告 `scripts/run_v1_public_smoke_case.sh`。只读 diff 显示：

- 内容增删为 `0/0`；
- 文件模式为 `100755 -> 100644`；
- 本阶段没有修改、恢复或提交该脚本。

因此不能把它写成工作区已经没有 tracked modification，也没有自动修正大阶段 A 的 runner warning。大阶段 A 当时记录的换行/权限风险在 B1 仍作为既有工作区风险保留；它不是 B1 新增内容，但需要研究者单独确认和处理。该差异不阻塞 B1 文档预登记，但阻塞把工作区宣称为完全 clean。

## 3. 本阶段新增/修改文件

新增：

1. `docs/v1-restart/PHASE_B1_NATIVE_REPLAY_PREPARATION.md`；
2. `docs/v1-restart/PHASE_B1_PUBLIC_EXPANSION_PREREGISTRATION.md`；
3. `docs/v1-restart/PHASE_B1_CLOSEOUT.md`；
4. `paper-ready/v1/public_benchmark_registry.tsv`。

修改：

5. `paper-ready/v1/evidence_index.tsv`，保留原有 11 条并追加 E12、E13、E14。

未修改：

- `analyzer/`；
- `contracts/`；
- `configs/`；
- `results/`，包括 frozen results 和 `results/matched-random-v1/`；
- 历史 quarantine 结果；
- `scripts/run_v1_public_smoke_case.sh` 内容。

没有新增轻量审计脚本，因为本阶段的只读扫描规模有限，人工分类和明确排除理由比新增脚本更直接，且没有必要让脚本结论替代人工分类。

## 4. public benchmark 扫描与登记结果

- 已扫描 `contracts/`、`configs/`、`docs/v1-restart/`、`paper-ready/` 和 `results/` 的相关 source/registry/audit 入口；仓库中不存在独立 `benchmarks/`、`examples/` 或 `test/` 顶层目录；
- 既有 public benchmark：5 个，其中 4 个 supported、1 个 conditional；
- Phase 06A 的 4 个 supported 任务在本 registry 中均为 `needs_replay`，不直接进入正式 main table；
- `exercise2-access-control` 仍为 `conditional`，必须 caller-controlled replay，前后都不得进入 supported pooled；
- 本阶段发现并登记 3 个候选：`PUB06` AlternativePath、`PUB07` MultiProperty、`PUB08` ThreeStep；
- 3 个候选全部是仓库内部 formal/早期 controlled toy，没有独立 public origin，均为 `excluded`；
- 建议进入 B2 的新增 public candidate 数：0；建议继续进行 native replay 的既有任务数：5（其中 exercise2 为 conditional）；
- `paper-ready/v1/public_benchmark_registry.tsv` 共 8 条 benchmark registry entries；
- `matched-random-v1` 没有作为 benchmark 条目使用，只在限制中明确排除。

## 5. 证据索引更新

`paper-ready/v1/evidence_index.tsv` 原有 11 条未删除，已追加：

- `E12_PHASE_B1_NATIVE_REPLAY_PREP`：`usable`，`use_in_main_table=no`；
- `E13_PHASE_B1_PUBLIC_EXPANSION_PREREG`：`needs_review`，`use_in_main_table=conditional`；
- `E14_PUBLIC_BENCHMARK_REGISTRY`：`needs_review`，`use_in_main_table=conditional`。

总数为 14 条。新增 evidence 只描述准备登记和审计边界，不提供新的效果数据。

## 6. 实验与冻结检查

- 是否运行 fuzzing：否；
- 是否运行 Echidna：否；
- 是否运行 Slither：否；
- 是否运行 solc：否；
- 是否运行 10 seed：否；
- 是否运行 30 seed：否；
- 是否生成正式论文主结果表：否；
- 是否修改 frozen results：否；
- 是否修改历史 quarantine 结果：否；
- 是否把 Phase 06A pilot 提升为正式主表：否；
- 是否把 `exercise2-access-control` 纳入 supported pooled：否；
- 是否创建新分支：否；
- 是否自动 commit 或 push：否。

## 7. 是否允许进入 B2

允许进入 B2 的 native replay / manifest preparation 和人工复核阶段；不允许由本 closeout 直接启动 B2 10-seed main run。正式 10-seed 之前仍需：

1. 研究者复核本阶段 4 个新增/修改文件和既有 runner tracked mode 差异；
2. 对 4 个 supported 任务完成固定路径 native replay，并确认没有新增语义不支持特征；
3. 对 exercise2 完成 same-caller 与 alternating-caller 的 caller-controlled replay，并继续单列；
4. 冻结 B2 独立 manifest、源码/配置 checksum、seed、预算、失败分类和输出目录；
5. 由研究者明确批准后，新增运行写入独立 `work/v1-restart/<run_id>/`，不写入 frozen `results/`。

B1 的核心阻塞项不是工具运行失败，而是：新增 public source 数为 0、native replay 尚未执行、runner tracked mode 差异尚未由研究者单独处理。因此“允许进入 B2 准备”不等于“允许立即运行 10 seed”。

## 8. 研究者下一步

请研究者复核上述文件、候选排除理由、exercise2 caller 边界和 runner 模式差异；确认无误后，再自行对明确路径执行 `git add`、`git commit` 和 `git push` 到 `develop`。本阶段没有自动提交或 push。
