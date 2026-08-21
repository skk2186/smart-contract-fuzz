# 02 主结果

## 唯一数据入口

论文制表优先从 [`results/paper-data/`](../../results/paper-data/) 读取，尤其是：

- [`dataset-whitelist.csv`](../../results/paper-data/dataset-whitelist.csv)：主结果、附录和排除项的白名单；
- [`synthetic-six-benchmark-summary.csv`](../../results/paper-data/synthetic-six-benchmark-summary.csv)：六个合成基准主比较；
- [`synthetic-six-overall-descriptive.csv`](../../results/paper-data/synthetic-six-overall-descriptive.csv)：异质批次的描述性总计；
- [`scalability-proxy.csv`](../../results/paper-data/scalability-proxy.csv)：当前目标规模起点，不是大型项目扩展性证明；
- [`input-checksums.sha256`](../../results/paper-data/input-checksums.sha256)：冻结输入的校验值。

## Formal 主批次

[`results/formal/`](../../results/formal/) 包含四个正式合成案例的原始日志、解析结果、候选 JSON、Top-K 排名和开销测量。论文主表使用 `formal-group-summary.csv`、`formal-candidate-summary.csv` 和 `formal-tie-aware-ranking.csv`；`runs/` 是不可修改的原始证据。

## B-2 扩展

[`results/formal-b2/`](../../results/formal-b2/) 包含 AlternativePath 和 MultiProperty。它们可以作为扩展实验或附录；由于缺少独立环境快照，论文中应保留 provenance 限制，不要把 MultiProperty 属性结果当成独立运行数。

## 结果解释

六个合成基准的 Full-K1 为 180/180，Original 为 171/180。候选空间在四个 Formal 案例中由 92 条 Dependency 路径降到 31 条 retained 路径，但候选减少本身不是性能提升的充分证明；性能结论必须与运行级反例发现率一起报告。
