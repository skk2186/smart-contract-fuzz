# 06 外部基线与 C-2 进展

## SMARTIAN 当前状态

SMARTIAN 已部署在 [`baselines/smartian/`](../../baselines/smartian/)，部署、构建和 submodule 处理记录见 [`DEPLOYMENT_STATUS.md`](../../baselines/smartian/DEPLOYMENT_STATUS.md)。

已完成的可审计批次在 [`results/public-benchmarks/c2-screening/smartian-formal-20260806/`](../../results/public-benchmarks/c2-screening/smartian-formal-20260806/)：两个简单整数目标（multifunc、onefunc），每个 30 次、30 秒预算，共 60 次；60/60 完成并发现 `IntegerBug`。共同预言机和限制见：

- [`SMARTIAN_CALIBRATION.md`](../../results/public-benchmarks/c2-screening/SMARTIAN_CALIBRATION.md)；
- [`SMARTIAN_ORACLE_ALIGNMENT.md`](../../results/public-benchmarks/c2-screening/SMARTIAN_ORACLE_ALIGNMENT.md)；
- [`SMARTIAN_VS_C1_REPORT.md`](../../results/public-benchmarks/c2-screening/SMARTIAN_VS_C1_REPORT.md)；
- [`SMARTIAN_FORMAL_FREEZE_PROPOSAL.md`](../../results/public-benchmarks/c2-screening/SMARTIAN_FORMAL_FREEZE_PROPOSAL.md)。

## C-2 结论

当前 [`candidate-registry.tsv`](../../results/public-benchmarks/c2-screening/candidate-registry.tsv) 中 5 行均为 legacy reference，新增 C2=0。SMARTIAN 的 60 次运行证明了部署、对齐和日志链路可执行，但覆盖面不足以写成广泛外部竞品排名。不要把 SMARTIAN 的两个简单目标和 C-1 的五个目标混成同一个总体分数。

## 下一步优先级

若继续冲刺完整论文，优先新增可执行且语义可对齐的公开属性任务，再扩大外部工具覆盖；不要继续为同一 SMARTIAN 目标重复 seed。
