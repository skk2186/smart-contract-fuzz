# V1 Harness语义适用性研究

本目录用于回答：当前V1生成的Harness在哪些Solidity/EVM语义条件下可以与Original Echidna进行有意义的比较。

当前阶段已经完成保守源码特征筛查、人工复核、语义负面对照和11个固定成功路径重放；这些证据仍不宣称完整语义等价。

文件：

- `targets.tsv`：预先列出的11个正式实验目标；
- `applicability.csv`：机器可读的逐目标风险特征；
- `static-audit-report.md`：静态筛查摘要。
- `manual-review.md`：对条件支持目标及差分验证口径的人工复核；
- `differential/`：调用者交替和回滚边界负面对照；
- `trace-replays/`：11个正式目标的固定成功路径重放。

重建命令：

```bash
python3 analyzer/audit_harness_semantics.py \
  --manifest results/semantic-applicability/v1/targets.tsv \
  --output-csv results/semantic-applicability/v1/applicability.csv \
  --report results/semantic-applicability/v1/static-audit-report.md
```

所有目标都具有`atomicity_caveat=1`：当前Harness把多步目标调用放进一笔wrapper交易，而Original通常跨多笔交易。`supported`仅表示没有再检出其他高风险特征，并不代表已经证明等价。

条件支持目标的人工复核和第一轮差分重放已经完成；后续新增公开目标必须复用同一筛查与重放口径。

纯派生重建也可以使用：

```bash
scripts/rebuild_semantic_applicability_v1.sh
```

该脚本只做Python语法检查、单元测试和静态结果重建，不包含Echidna、solc、Slither、联网或依赖安装步骤。

## 差分语义回归

`differential/`与已有正式实验完全隔离。它使用本地语义fixture验证三个窄命题：同一调用者时结果一致、交替调用者时可能不一致、中间失败时回滚边界不同。

```bash
scripts/run_semantic_differential_v1.sh
```

该命令会本地编译专用fixture，并以Echidna 2.3.2作为EVM属性测试运行器；它不访问链上状态、不连接RPC、不联网，也不对外部合同执行测试。

`trace-replays/`使用固定已知参数重放11个正式目标的直接路径和实际生成Harness。入口为：

```bash
scripts/run_semantic_trace_replays_v1.sh
```

主要结果见`trace-replays/trace-replay-summary.csv`和`trace-replays/differential-report.md`。该重放只验证成功路径的属性相关最终状态，不模拟区块推进或证明所有交易前缀等价。
