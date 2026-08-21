# 从这里开始：智能合约状态依赖引导模糊测试

## 一句话说明

本项目研究：能否先静态分析智能合约与安全属性之间的状态依赖，自动挑选更值得测试的函数调用顺序，再把这些顺序包装成 Echidna 可调用的 Harness，从而减少随机模糊测试在无关交易序列上的探索。

项目当前完成的是 **V1 方法的受控机制验证和有限公开基准验证**。它不是已经证明对所有智能合约都有效的通用漏洞检测器，V2 也仍属于开发材料。

## 研究动机

多交易状态问题通常需要按特定顺序调用多个函数，例如：

```text
register() -> deposit() -> approve() -> withdraw()
```

原始 Echidna 可以随机生成交易序列，但当合约中存在大量无关函数、错误状态写入或必须重复调用的函数时，正确序列的搜索空间会迅速增大。

V1 的核心想法是：先利用 Slither 提取状态读写关系，再根据安全属性筛选、扩展和排序候选路径，最后自动生成 Harness，让 Echidna 主要搜索参数而不是完全随机搜索顺序。

## 方法流程

```mermaid
flowchart LR
    A[Solidity 合约与 Echidna 属性] --> B[提取函数状态读写]
    B --> C[生成状态依赖路径]
    C --> D[属性相关性过滤]
    D --> E[有界重复调用扩展]
    E --> F[值约束匹配与排序]
    F --> G[选择 Top-K 路径]
    G --> H[自动生成 Harness]
    H --> I[Echidna 多 seed 运行]
    I --> J[日志解析统计和解释]
```

各阶段的含义：

- **Dependency**：根据函数对状态变量的写入和读取生成可能的调用链。
- **Property**：优先保留最终会影响安全属性所读取状态的路径。
- **Repeat**：允许同一函数在一条路径中被调用多次，例如两次 `deposit()`。
- **Value**：用常量写入和简单 `require` 条件判断状态值方向是否匹配。
- **Full**：组合 Property、Repeat 和 Value 后的完整 V1 方法。
- **Top-K**：只把排序前 K 条候选路径写入 Harness；K1 表示只保留第一条。

## 四个核心合成案例

| 基准 | 专门验证的问题 | 观察结果 |
|---|---|---|
| NoisyFourStep | 无关状态路径过多 | 属性过滤将候选从30条降到3条，并将目标路径变为唯一 Top-1 |
| BranchValue | 依赖关系相同但写入值方向不同 | Property-K1 为0/30，Value/Full-K1 为30/30 |
| RepeatedCall | 漏洞需要重复调用同一函数 | 不允许重复为0/30，完整方法为30/30 |
| ResetExample | 重复扩展造成候选和同分集合增大 | Value 将处于大同分集合的目标路径区分为唯一 Top-1 |

这里的合成合约是为组件障碍专门设计的，因此适合证明“机制能解决该障碍”，不适合单独证明对真实合约总体有效。

## 已完成的正式实验

### 六个合成基准主比较

- Full-K1：180/180 次运行发现反例。
- Original：171/180 次运行发现反例。
- 这180次由6个基准、每组30个 seed 组成。
- MultiProperty 的一次成功要求同一运行中的两个指定属性都产生反例。

数据来源：[synthetic-six-benchmark-summary.csv](../results/paper-data/synthetic-six-benchmark-summary.csv)。

### 五个公开基准 C-1

- Full-K5：149/150。
- Original：144/150。
- Full-K1：120/150。
- Full-K1 的主要失败来自 `exercise2-access-control`：正确路径排名第2，不在 K1 中，因此0/30；K5包含它，因此30/30。

数据来源：[public-c1-group-summary.csv](../results/public-benchmarks/c1/public-c1-group-summary.csv) 和 [C-1统计报告](../results/public-benchmarks/c1/statistics/public-c1-statistical-report.md)。

### 候选路径与开销

- 四个正式合成基准的 Dependency retained paths 合计92条。
- Property retained paths 合计31条。
- 减少61条，即66.3043478%。
- 四个小型合成合约从分析到 Harness 编译的总准备时间中位数约为1.30–1.32秒。

候选数据来源：[formal-candidate-summary.csv](../results/formal/formal-candidate-summary.csv)。

开销口径来源：[measurement-scope.md](../results/formal/overhead/measurement-scope.md)。

## 1050次正式运行应该怎样理解

当前保存的正式运行包括：

- Formal 主批次：450次，包含 Original、Full 和组件对照。
- Formal-B2：150次，包含 Original、Full-K1 和 AlternativePath 的 Full-K2。
- C-1：450次，包含 Original、Full-K1 和 Full-K5。
- 合计：1050次运行日志。

但1050次运行不等于1050个独立合约。seed 用于测量同一合约上随机搜索的波动；衡量外部泛化时，更重要的是合约数量和合约多样性。目前真正的公开基准只有5个。

## 当前能支持的结论

- V1 能在六个指定合成基准中自动生成有效的候选 Harness。
- 属性过滤、值匹配和重复访问在对应受控障碍中发挥了可观察作用。
- 候选排序和 Top-K 会决定有限预算下是否包含有效路径。
- V1 能兼容五个经过筛查和必要适配的公开基准，但结果显示 K1 并不稳定。
- 当前数据足以支撑开题、毕业论文的实验基础和受控机制研究。

## 当前不能支持的结论

- 不能声称 V1 对任意智能合约普遍优于 Original Echidna。
- 不能把5个公开基准外推成广泛真实合约总体。
- 不能把 `budget_exhausted` 写成属性通过或合约安全。
- 不能直接用 Original 与 Harness 的 `Total calls` 声称等量工作下加速。
- 不能把显著的 log-rank p 值自动解释为 Harness 更快。
- 不能把候选路径减少自动解释成 fuzzing 性能必然提升。
- 不能把 `results/v2/` 当作已验证的正式方法结果。

## Harness 的关键语义限制

Original Echidna 的多步序列由多笔独立交易组成；当前 Harness 会把候选函数顺序封装在一次外部 wrapper 调用内。因此二者可能在以下方面不同：

- 目标函数观察到的调用者；
- 多步调用是否处于同一笔交易；
- 中间一步回滚时的回滚范围；
- 每次 Echidna 外层调用包含的目标函数调用数。

这意味着 Harness 结果描述的是当前执行模型下的实际表现，不是与 Original 完全等价的底层工作量比较。第一轮[语义适用性研究](../results/semantic-applicability/v1/README.md)已确认11/11条固定成功路径的属性相关最终结果一致，也实证展示了调用者交替和整体回滚的差异；因此限制被进一步刻画，但没有被消除。

## 阅读顺序

1. 本文档：先建立全局认识。
2. [DIRECTORY_GUIDE.md](DIRECTORY_GUIDE.md)：知道文件放在哪里、哪些能动。
3. [EXPERIMENTS.md](EXPERIMENTS.md)：逐项了解实验目的、分母和结论。
4. [ranking-interpretation.md](../results/paper-data/ranking-interpretation.md)：理解并列排名。
5. [C-1统计报告](../results/public-benchmarks/c1/statistics/public-c1-statistical-report.md)：理解公开基准统计与限制。
6. [CCF-C差距审计](CCF_C_GAP_ANALYSIS.md)：理解当前证据距离完整会议论文还差什么。
7. [最低补强实验方案](MINIMUM_EXPERIMENT_PLAN.md)：理解8月20日前的执行顺序与停止条件。

## 自测：能回答这些问题才算理解了项目

1. 为什么仅有状态读写依赖仍不足以选择正确路径？
2. Property、Repeat 和 Value 分别解决什么问题？
3. 为什么 BranchValue 的 Property-K1 是0/30，而 Value-K1是30/30？
4. 为什么 RepeatedCall 必须允许同一函数重复出现？
5. 为什么 Reset 的 display rank 5不能解释为严格排名下降？
6. 为什么 Full-K1 在 exercise2 上失败，而 Full-K5成功？
7. 为什么1050次运行不能等同于1050个泛化样本？
8. 为什么 Original 与 Harness 的调用次数不能直接比较？
9. 92→31具体统计的是什么？
10. 当前最需要补强的是更多seed，还是更多外部基准、竞品和语义验证？
