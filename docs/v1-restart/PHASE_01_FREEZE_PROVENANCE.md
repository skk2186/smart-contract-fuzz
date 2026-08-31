# V1 Restart — Phase 01 Freeze Provenance Recovery

审计日期：2026-08-31  
审计分支：develop  
当前 GitHub checkout HEAD：fde47062acafe64ea192ccfbe83daea35699568a

## Freeze metadata

| Field | Value |
| ----- | ----- |
| generated_at | 2026-08-06T23:23:42+08:00 |
| repository_base_commit | 4fb0f71fda37ac5956be2b060250a09bba8b2e90 |
| 当前 GitHub 初始 commit | fde47062acafe64ea192ccfbe83daea35699568a (2026-08-21T21:57:47+08:00, `Add controlled V1 experiment workflow and agent guardrails (#1)`) |
| 当前 GitHub 是否包含旧 freeze history | 否；目标 base commit 在当前仓库不可达 |

当前仓库基线检查结果：分支为 `develop`，HEAD 为 `fde47062acafe64ea192ccfbe83daea35699568a`。工作区中只有此前 Phase 01 审计相关未跟踪文件；本次未修改 `results/` 或其他冻结证据。

## Hash comparison

| Version | SHA-256 |
| ------- | ------- |
| input-checksums expected | `e7056c0f8ec4f97be5722c30cefba655a797b9575f1807eb062918a26151404d` |
| current GitHub | `32f99a74f0c5c468d7e2bf27ab17d39898098df138ff11a4e3c2e167998c57f8` |
| base commit `4fb0f71f` | `NOT_RECOVERED` |
| authoritative freeze commit | `NOT_FOUND` |

目标文件为 `results/matched-random-v1/execution-manifest.tsv`。当前 checkout 的 SHA 与冻结 checksum 中的 EXPECTED_SHA 不一致。

## History recovery

按指令只读执行：

    find /home/skk -maxdepth 6 -type d -name .git -print

共发现 45 个 Git 仓库目录，其中当前仓库之外的 44 个候选仓库均只执行了 `git rev-parse HEAD`、`git remote -v` 和目标提交存在性检查。最相关的旧项目副本为：

    /home/skk/smart-contract-fuzzing-v1

该副本的 HEAD 为 `fde47062acafe64ea192ccfbe83daea35699568a`，远程为 `https://github.com/skk2186/smart-contract-fuzz.git`，但不包含目标提交。其他候选仓库也均未包含：

    4fb0f71fda37ac5956be2b060250a09bba8b2e90

因此没有可用于计算 `BASE_COMMIT_MANIFEST_SHA` 的旧提交，也没有可判定的后续 authoritative freeze commit。未执行旧文件导出、差异比较或任何文件恢复。

## Difference classification

`UNKNOWN`

由于目标 base commit 和权威 freeze commit 均未找到，不能把当前 manifest 与冻结版本的差异归类为换行、空白、行顺序或真实内容变化，也不能推测字段变化。

## Conclusion

`FREEZE_HISTORY_NOT_FOUND`

Phase 01 provenance 仍未解决，Phase 01 继续 `BLOCKED`。本次没有修改任何 `results/` 文件，没有运行 Echidna、Slither、solc 或其他实验，也没有执行 commit、push 或进入 Phase 02。
