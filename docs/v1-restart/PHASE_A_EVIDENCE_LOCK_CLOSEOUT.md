# 大阶段 A：Evidence Lock Closeout

## 1. 执行记录

- 执行时间记录：2026-09-07T11:34:24+08:00（Asia/Hong_Kong）；
- 当前分支：`develop`；
- 当前 HEAD：`33e3a81b8d416326f3b54003427f9cb8f31f17a0`；
- 最近提交：`33e3a81 test: run public supported V1 3-seed pilot`。

## 2. 新增文件

本阶段只新增以下 4 个文件：

1. `docs/v1-restart/PAPER_EVIDENCE_LOCK.md`
2. `docs/v1-restart/SEMANTIC_BOUNDARY_AUDIT.md`
3. `paper-ready/v1/evidence_index.tsv`
4. `docs/v1-restart/PHASE_A_EVIDENCE_LOCK_CLOSEOUT.md`

没有修改 analyzer、contracts、configs、results 或已有 frozen/paper-ready 结果文件。

## 3. Phase 06A work artifacts

- 是否读取到 `work/v1-restart/phase06a-public-supported-3seed/`：是；
- 是否检查 raw artifacts：是；
- pilot run 目录：36 个；
- 有效 preflight 目录：4 个，均为 `STATUS=preflight_pass`；
- 保留的首次失败 preflight：1 个空目录，无 status marker，不计入有效 preflight；
- 36/36 pilot 必需文件齐全；
- 36/36 status 与 parser 分类一致；
- 40/40 pilot/preflight checksum manifest 通过 `sha256sum -c`；
- 36/36 raw log marker 与分类相符；
- pilot status：35 `falsified`、1 `budget_exhausted`、0 `startup_error`、0 `unknown_error`、0 `incomplete`。

唯一 `budget_exhausted` 是 `echidna-multi / Original / seed 1`，只能表示在给定预算内没有观察到反例，不能写成 property passed、contract safe 或无漏洞证明。

## 4. 工作区和冻结边界

- `git status --short` 显示 `scripts/run_v1_public_smoke_case.sh` 有未提交换行差异；`git diff --ignore-space-at-eol` 无内容差异。本阶段没有覆盖或回退它；提交前需由研究者确认归属。
- 本阶段没有修改 frozen results，也没有重建或刷新任何 frozen checksum。
- `results/matched-random-v1/` 未被修改，继续标记为 `PROVENANCE_UNRESOLVED`、`DO_NOT_USE_FOR_NEW_CLAIMS`、`LEGACY_CONTROL_QUARANTINED`。
- 没有运行 30 seed，没有新增 benchmark，没有运行新的 Echidna/Slither/solc 实验。
- 没有创建新分支，没有自动 commit 或 push。

## 5. Evidence index 计数

`paper-ready/v1/evidence_index.tsv` 共 11 条 evidence：

| status | 数量 |
|---|---:|
| usable | 5 |
| appendix_only | 3 |
| pilot_only | 1 |
| quarantined | 1 |
| needs_review | 1 |

semantic audit 中的 public benchmark 可用性为：

- supported：4 个；
- conditional：1 个；
- excluded：0 个；
- 可进入 supported pooled main table 的当前语义候选：4 个，但都仍需正式批次前完成任务级 native replay/人工复核；
- `exercise2-access-control`：不得进入 supported pooled main table，只能单独作为 conditional appendix/条件分层案例。

## 6. 是否阻塞下一阶段

大阶段 A 的 evidence lock 已完成，没有阻塞大阶段 B 的预登记、人工复核和 native replay 准备入口。

但以下事项阻塞任何未经复核的正式主实验或主表提升：

1. 研究者尚未复核本阶段 4 个新增文件及现有 runner 的未提交换行差异；
2. public benchmark 尚需逐任务 native replay/语义差分记录，尤其是 exercise2 的 caller-controlled replay；
3. Phase 06A 仍是 `pilot_only`，不能直接授权 30-seed 正式运行；
4. `exercise2-access-control` 的 `msg.sender`、address-keyed mapping 和 caller alternation 边界必须保留；
5. matched-random-v1、V2/C2 和其他 quarantine 材料不能用于填充 V1 主表。

## 7. 下一步建议

进入大阶段 B 时，先做预登记和逐任务 native replay，再由研究者决定是否启动正式重复实验。所有新增运行继续写入独立 `work/v1-restart/<run_id>/`，不提升到 frozen results；正式主表只能由固定脚本从已批准、可追溯的来源重建。

请研究者检查无误后，再自行执行针对明确路径的 `git add` / `git commit` / `git push` 到 `develop`；本阶段不会自动提交或 push。
