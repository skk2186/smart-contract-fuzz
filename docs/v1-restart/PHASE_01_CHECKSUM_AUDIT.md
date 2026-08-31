# V1 Restart — Phase 01 Checksum Audit

审计日期：2026-08-31  
审计分支：develop  
审计 commit：fde47062acafe64ea192ccfbe83daea35699568a

## Scope and command

本审计只读取冻结记录并重新执行校验，不修改：

- results/paper-data/input-checksums.sha256
- results/paper-data/repository-files.tsv
- results/paper-data/repository-freeze.json

执行命令：

    sha256sum -c results/paper-data/input-checksums.sha256 \
      > /tmp/v1-checksum-audit.txt 2>&1 || true

本次输出包含 1 个缺失项和 11 个 hash 不一致项。以下 Actual SHA 是当前 checkout 的实际值；缺失文件记为 MISSING。

## Findings

| Path | Expected SHA | Actual SHA | Status | Reason |
| ---- | ------------ | ---------- | ------ | ------ |
| baselines/smartian/DEPLOYMENT_STATUS.md | 01c0376e3dd14cb05a9fd25040a4a2e45752a4b49bf516b45fc62430c6366249 | MISSING | EXPECTED_EXTERNAL_MISSING | 独立 SMARTIAN 工作区不在 fresh clone 的主仓库中，且该路径属于外部 baseline。fresh clone 不包含独立 SMARTIAN 工作区，因此不是主仓库冻结证据丢失；不恢复伪文件。 |
| results/formal/formal-candidate-summary.csv | d25f4e0e362efa98d4698f3f0630be18c8b7efbb05c6ec49a0d2fe324333a70c | 04c6d7c63f32bdc693fc6e4b3cd1a364cca0652470eaf1e3dea0a940010bf273 | DERIVED_RESULT_MISMATCH | Formal 候选空间汇总表，可由正式运行/候选输入重建；不是正式运行输入。 |
| results/formal/formal-tie-aware-ranking.csv | e293ee0420deac823077374e364f5d930c53e5516e606b3006ce577e00d660ac | f652d56963a7939e5e67afd8e495fc0f38aad6a83a5754236cc300b5a4ecfc9f | DERIVED_RESULT_MISMATCH | 并列感知排名派生表，可由候选评分和正确路径信息重建。 |
| results/formal/overhead/overhead-detailed.csv | e66caf21b813ed601e3bd02a62bfa58c0bab17a56fb82c9f8f1a17ca4bb36c2e | 8bc0c79fc3d7e84e18743d6c7fc5b8b18d402498c9481e5018e13ec2bb65de09 | DERIVED_RESULT_MISMATCH | 分阶段开销测量明细，属于 overhead 派生数据；原始测量范围和 metadata 仍在仓库。 |
| results/formal/overhead/overhead-summary.csv | 99346e312985ddcf6d00c4313352dc56471580eba2b9027952984f23f1a4177b | 010c0f3574f7206eaf384ef01d44cd118b8077e39df17f4e818208605bdeaa3b | DERIVED_RESULT_MISMATCH | overhead 汇总统计，可由明细测量重建，不是 fuzzing 输入。 |
| results/matched-random-v1/execution-manifest.tsv | e7056c0f8ec4f97be5722c30cefba655a797b9575f1807eb062918a26151404d | 32f99a74f0c5c468d7e2bf27ab17d39898098df138ff11a4e3c2e167998c57f8 | CRITICAL_FROZEN_EVIDENCE_MISMATCH | 这是 control-freeze 的正式运行 provenance manifest，README 明确说明正式运行严格使用它。即使 cases/schedule/Harness 可用于重建，也不能在未确认权威快照前将其 hash 不一致降级为普通派生差异。 |
| results/matched-random-v1/summary-by-benchmark.csv | 8f09f5906f26e96452b4490e18e27e10a364bdc91af6b341323163ed55ab832d | fdcaa4804786ce71a401ef1c97742247de246deb1ed1d8bd0f6bfb3248162e3a | DERIVED_RESULT_MISMATCH | matched-random benchmark 汇总，可由 execution manifest 和 raw runs 重建。 |
| results/paper-data/noisy-four-step/permutation-by-sequence.csv | 713bef963df27a9d499ecb00e236582958f31e1f0496fc651cab991a682ad46e | f3434ef5dcf6144b6480228d6adff90181f29256c635cc4d7e8d7107605ddbe4 | DERIVED_RESULT_MISMATCH | NoisyFourStep 调用顺序对照汇总，可由冻结 permutation runs 重建。 |
| results/paper-data/scalability-proxy.csv | fa743bb5b9f81d3a3d74f2cbc44121d40a916ca7f2999f187b795c7cae25cf3a | 5353b72a3eed9fe3ecd091d0ef3042ee084ee93eddaf2fbff3d598c91107d4ee | DERIVED_RESULT_MISMATCH | 规模 proxy 描述性表，可由源码 inventory 和候选 JSON 重建；不属于运行输入。 |
| results/public-benchmarks/c2-screening/smartian-formal-20260806/summary.csv | 40215c811008d684be040c1ac8bc3e4085601f8108dc0a730f921651e8a6b9ed | feb87304fcc9c6b5b99abcaf1136a5a5b1590fe4f96404115dab1b90314eb4b5 | DERIVED_RESULT_MISMATCH | SMARTIAN 外部基线汇总，可由该目录的 run-status/raw logs 重建；外部部署说明的缺失已单独归类。 |
| results/semantic-applicability/v1/applicability.csv | e692105adc450b99a8e93bb13f6b98f2f7f69c99083714263762af7bb2cee49c | 3d419bdb5558513cdb27a0510daa8598f63f6cdef1f11952b1d1bbe63327ef04 | DERIVED_RESULT_MISMATCH | 语义适用性分类表，可由静态审计和人工复核材料重建。 |
| results/semantic-applicability/v1/trace-replays/trace-replay-summary.csv | 8a0eaeb60fc96fa13091bb3db16dab0315271b492d7ac8cad1f4f0d833ceecda8 | e7dabb30273a60cd11f1cfea930b1dd0b73e5861b992a18e976e81e86dc65866 | DERIVED_RESULT_MISMATCH | 固定路径 trace replay 汇总，可由 trace-replays 原始日志重建。 |

## Git-history reconciliation

上述现存不一致文件的 path history 均显示最后记录为 a84bbf5 初始化；对 a84bbf55b9e869767fac84d4f3dcc60351ff7fd0..HEAD 的逐路径比较没有发现由当前 fde47062acafe64ea192ccfbe83daea35699568a 提交引起的结果文件修改。因此本报告不把它们伪装成 EXPECTED_POST_FREEZE_CHANGE；其中 10 个按文件角色和可重建性归为派生差异，但 execution-manifest 仍按正式 provenance manifest 保守列为 critical。

本次没有发现正式 runs/*.log、正式 benchmark 输入合约、正式 config 或正式 Harness 发生 hash mismatch。results/、正式 Harness 目录及三份冻结记录均未被本审计修改。

## Gate

- EXPECTED_EXTERNAL_MISSING：1
- EXPECTED_POST_FREEZE_CHANGE：0
- DERIVED_RESULT_MISMATCH：10
- CRITICAL_FROZEN_EVIDENCE_MISMATCH：1

Checksum gate: BLOCKED

结论：checksum gate 被 execution-manifest 的 critical hash mismatch 阻塞；另有 1 个 EXPECTED_EXTERNAL_MISSING 和 10 个 DERIVED_RESULT_MISMATCH。不得修改或刷新冻结 checksum，需由研究者确认 matched-random 的权威 manifest 快照后再决定是否解除阻塞。

## Research scope disposition

原机械审计发现保持不变：`results/matched-random-v1/execution-manifest.tsv` 仍为 `CRITICAL_FROZEN_EVIDENCE_MISMATCH`。历史 provenance recovery 未找到原冻结 commit 或后续权威 freeze commit，因此该历史控制实验的 provenance 仍 unresolved。

经研究范围审查，`results/matched-random-v1/` 属于辅助排序控制实验，不是 Phase 02 最小 V1 复现的依赖项。该历史目录标记为：

`LEGACY_CONTROL_QUARANTINED`

处理规则：不删除、不修改、不重新生成历史 checksum，不尝试匹配旧 hash，不作为 Phase 02–05 的已有可信实验结论，也不引用其历史数值作为新的论文证据。后续如需使用 matched-random，应在新的隔离 runner 和新的 Git commit 下重新设计并运行。

因此：

- Checksum historical integrity gate: BLOCKED for matched-random reuse
- V1 Restart execution gate: PASS WITH WARNINGS

原报告中的 `Checksum gate: BLOCKED` 和 `CRITICAL_FROZEN_EVIDENCE_MISMATCH` 机械审计事实保留不变；本节只记录研究范围处置，不把 mismatch 改写为 OK。
