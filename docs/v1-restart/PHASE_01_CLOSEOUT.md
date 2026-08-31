# Phase 01 Closeout

审计日期：2026-09-01  
审计分支：develop  
当前 HEAD：fde47062acafe64ea192ccfbe83daea35699568a

## Final status

`PASS WITH WARNINGS`

`PHASE_02_ALLOWED=1`

该状态表示 V1 Restart 的新实验执行门已通过范围隔离；不表示历史 checksum mismatch 已被修复，也不表示 matched-random 历史证据已恢复。

## Trusted baseline

| 项目 | 结果 |
| --- | --- |
| 当前 branch | `develop` |
| HEAD SHA | `fde47062acafe64ea192ccfbe83daea35699568a` |
| Python | 3.11.15，来自 `contract-fuzz` conda 环境 |
| Slither | 0.11.5 |
| solc | 0.8.20+commit.a1b79de6 |
| Echidna | 2.3.2 |

已确认 Git 基线正确、develop 工作线建立、contract-fuzz 环境完整，Python / Slither / solc / Echidna 可用。isolated restart runner 已建立，Original dry-run 与 Full-K1 dry-run 均通过。

## New experiment governance

新入口：

    scripts/run_v1_restart_case.sh

所有新实验只能写入：

    work/v1-restart/<run_id>/

每个 run 目录必须记录 manifest、environment、command、generated inputs、raw log、SHA-256 和 completion status。runner 从脚本位置解析仓库根目录，拒绝不安全或已存在的 run-id，不写入冻结 `results/`，并保持每个实验单元的输入、输出和 provenance 隔离。

本次 Closeout 不运行 Echidna、Slither、solc 或任何实验。

## Legacy evidence quarantine

    results/matched-random-v1/

状态：

    PROVENANCE_UNRESOLVED
    DO_NOT_USE_FOR_NEW_CLAIMS
    LEGACY_CONTROL_QUARANTINED

其 `execution-manifest.tsv` 无法与 2026-08-06 冻结 checksum 记录一致，原冻结 Git history 也不可用。该历史控制实验不删除、不修改、不重新生成 checksum，不作为新的论文证据。若未来确需使用，必须在新的隔离 runner 和新的 Git commit 下重新设计并重新运行。

历史 checksum integrity gate 对 matched-random reuse 仍为 BLOCKED；该问题不属于 Phase 02 最小 V1 复现的输入依赖。

## Phase 02 scope

只允许执行一个最小、可检查的 V1 复现单元：

- Benchmark: `NoisyFourStepExample`
- Run: Original seed 1
- Run: Full-K1 seed 1

目的不是比较性能，而是恢复研究者对 V1 完整实验链的理解：

    contract
    → RW
    → property/repeat/value
    → Top-K
    → Harness
    → Echidna

Phase 02 不读取 `results/matched-random-v1/`，不把历史 matched-random 数值纳入新结论。

## Forbidden in Phase 02

- 30 seed
- public C1
- B2
- matched-random
- SMARTIAN
- V2
- 修改 V1 算法
- 调参数
- 修改 frozen results

Phase 02 已获准，但本次没有进入或启动 Phase 02；后续启动前仍需由研究者复核新 run 的 manifest、command、environment、status 和 checksums。

