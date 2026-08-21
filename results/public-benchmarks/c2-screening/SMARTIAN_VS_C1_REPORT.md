# SMARTIAN 与 C-1 的描述性外部基线对照

状态：完成；不属于 C2 正式统计分母。

## 结果

两个已完成 oracle 对齐的整数目标均得到相同的 30/30 发现结果：

| 目标 | C-1 Original | C-1 Full-K1 | C-1 Full-K5 | SMARTIAN |
|---|---:|---:|---:|---:|
| smartbugs-multifunc | 30/30 | 30/30 | 30/30 | 30/30 |
| smartbugs-onefunc | 30/30 | 30/30 | 30/30 | 30/30 |

逐行数据见 [`smartian-vs-c1-descriptive.csv`](smartian-vs-c1-descriptive.csv)，机器可读摘要见 [`smartian-vs-c1-descriptive.json`](smartian-vs-c1-descriptive.json)。C-1 原始统计来自 `results/public-benchmarks/c1/grouped/`；SMARTIAN 原始日志和解析结果来自 [`smartian-formal-20260806/`](smartian-formal-20260806/)。

## 时间与语义限制

C-1 Echidna 的成功运行中位 `fuzz_seconds` 约为 0.45–0.46 秒，SMARTIAN 的过程墙钟中位数为 30 秒。这不是速度比较：两者的执行引擎、启动成本、预算单位、调用模型和随机种子控制不同；SMARTIAN 还没有公开 seed 参数。这里只报告实际运行表现，不计算加速比，也不进行跨工具 seed 配对检验。

SMARTIAN 的成功定义是产生 `IntegerBug` 反例；该告警已经通过同一 0.4.25 编译器下的 Echidna 独立重放和最小调用序列验证，与 `echidna_count_does_not_underflow` 语义一致。因此这两个目标可以作为条件公平的外部工具对照；其它三个 C-1 目标没有 SMARTIAN 原生等价 oracle，不能据此扩展结论。

## 论文可用结论

可以写：在两个简单整数下溢属性上，SMARTIAN 在固定 30 秒预算的 30 次重复中均发现与 Echidna 属性一致的反例，证明该外部工具已能在本地复现并运行。

不能写：SMARTIAN 比 Echidna 更快、更强，或在一般智能合约上具有更高成功率。两个目标的 C-1 方法本身也都是 30/30，结果没有产生区分度。

本报告不改变 `candidate-registry.tsv`，也不把 SMARTIAN 结果并入 C2 分母。
