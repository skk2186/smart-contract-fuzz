# 论文数据入口与白名单

`dataset-whitelist.csv` 是论文自动制表的唯一数据入口。自动脚本只能读取：

1. `role=main` 且 `inclusion_status=included` 的条目；或
2. 由调用者显式选择的 `role=ablation_or_appendix` 条目，并同时展示其 provenance 限制。

不得递归扫描整个 `results/` 自动发现数据。`exclude_from_main` 条目不得进入主表、总分母或正式方法比较，即使其中存在格式相同的 CSV 或同名 benchmark/method。

Formal 与早期 BranchValue、ResetExample、NoisyFourStep、RepeatedCall 数据来自不同批次，不得因名称相同而 pooled 汇总。C-1 只使用已完成审计的 summary、path preflight 和 statistics；C0、smoke 和 runner-output 不属于正式运行分母。V2 为独立开发材料，不得混入冻结的 Full-v1.0 结论。

所有成功率必须说明分母单位。MultiProperty 的正式分母是运行，每次运行含两个 property outcomes；`both_properties_failed` 是运行级复合条件。`budget_exhausted` 只表示预算内未发现反例。

`input-checksums.sha256` 记录 `paper-ready/manifest.tsv` 中主文和附录证据及其原始日志的逐文件 SHA-256，用于检测后续内容变化。它不能恢复缺失的 Git commit、工具环境或历史 provenance，也不得被解释成这些信息已经存在。

`repository-files.tsv` 和 `repository-freeze.json` 记录冻结时全工作区文件状态与范围分类。它们包含本地工具链和第三方嵌套仓库的盘点信息，但这些环境资产不自动进入论文证据白名单。

当前论文证据的阶段性出口见[`readiness-matrix.md`](readiness-matrix.md)。该矩阵只记录证据边界和 Go/No-Go，不会自动把附录消融并入主表。

当前本地目标的规模代理见[`scalability-proxy.md`](scalability-proxy.md)；它是条件性附录数据，不是大型真实合约的可扩展性证明。
