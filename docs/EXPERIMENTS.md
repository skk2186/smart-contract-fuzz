# 已完成实验总账与结果解释

## 1. 正式实验总览

| 实验族 | 基准数 | 组数 | 每组seed | 运行数 | 作用 |
|---|---:|---:|---:|---:|---|
| Formal main | 4 | 15 | 30 | 450 | 完整方法与组件对照 |
| Formal-B2 | 2 | 5 | 30 | 150 | 多可行路径与多属性扩展 |
| Public C-1 | 5 | 15 | 30 | 450 | 公开基准兼容性与有限外部验证 |
| 合计 | 11 | 35 | — | 1050 | 不可作为一个同质总体合并推断 |

Formal main包含组件组，B2包含Alternative的Full-K2，C-1包含Full-K5。因此1050次不是单一Original/Full比较的分母。

## 2. Formal main：四个合成基准

数据入口：[formal-group-summary.csv](../results/formal/formal-group-summary.csv)。

| 基准 | 方法 | falsified | budget exhausted | 目的 |
|---|---|---:|---:|---|
| BranchValue | Original | 28 | 2 | 原始基线 |
| BranchValue | Property-K1 | 0 | 30 | 不使用值匹配 |
| BranchValue | Value-K1 | 30 | 0 | 验证值匹配 |
| BranchValue | Full-K1 | 30 | 0 | 完整方法回归 |
| NoisyFourStep | Original | 26 | 4 | 原始基线 |
| NoisyFourStep | Dependency-K10 | 30 | 0 | 基础依赖Top-10 |
| NoisyFourStep | Property-K1 | 30 | 0 | 属性筛选Top-1 |
| NoisyFourStep | Full-K1 | 30 | 0 | 完整方法回归 |
| ResetExample | Original | 27 | 3 | 原始基线 |
| ResetExample | Dependency-K10 | 30 | 0 | 基础依赖Top-10 |
| ResetExample | Property-K1 | 30 | 0 | 属性筛选Top-1 |
| ResetExample | Full-K1 | 30 | 0 | 完整方法回归 |
| RepeatedCall | Original | 30 | 0 | 原始基线 |
| RepeatedCall | Value-no-repeat-K1 | 0 | 30 | 禁止重复调用 |
| RepeatedCall | Full-K1 | 30 | 0 | 加入重复调用 |

Formal总计381次发现反例、69次预算内未发现反例。69次不能称为性质通过。

### BranchValue说明

- Property阶段只知道哪些状态变量相关，但不能区分 `prepareGood()` 与错误值写入。
- 正确路径的display rank为5，实际处于tie-aware 1–5同分集合。
- Value匹配利用简单常量写入和条件关系，将正确路径区分为唯一Top-1。
- 因而 Property-K1为0/30，Value-K1和Full-K1均为30/30。

最窄结论：简单值匹配在该受控模式中能消除依赖同分歧义。

### NoisyFourStep说明

- Dependency retained paths为30，目标路径display rank为6、tie-aware 6–9。
- Property retained paths为3，目标路径成为唯一Top-1。
- Dependency-K10与Property-K1均30/30，因此运行成功率本身不能证明Property更强。
- 主要证据是Property用更小K保留正确路径并删除无关候选。

### RepeatedCall说明

- 目标序列要求 `deposit()` 出现两次。
- Dependency和Property阶段的候选中不存在该重复路径。
- 禁止重复的Value-no-repeat-K1为0/30；Full-K1为30/30。

最窄结论：对于该明确需要重复调用的受控合约，有界重复访问是必要机制。

### ResetExample说明

- Property阶段保留19条路径，正确路径tie-aware rank为1–6。
- Repeat阶段扩展为33条，正确路径display rank为5，但与18条路径同分，即tie-aware 1–18。
- Full阶段通过值匹配将正确路径变为唯一Top-1。
- Property-K1与Full-K1均30/30，因此不能声称Value在此提高了运行成功率。

正确表述：重复扩展增大了候选和同分集合，值匹配随后消除了排序歧义。

## 3. Formal-B2：扩展合成基准

数据入口：[formal-b2-run-summary.csv](../results/formal-b2/formal-b2-run-summary.csv)。

### AlternativePath

- Original：30/30。
- Full-K1：30/30。
- Full-K2：30/30。
- 两条有效路径分别排第1和第2。
- K1只保留第一条；K2同时保留两条。

它证明方法可以识别多条可行路径，但不能证明K2比K1具有成功率优势，因为三组均30/30。

### MultiProperty

- Original：30次运行中30次两个属性均产生反例。
- Full-K1：同样30/30。
- 每种方法是30次运行、60个property outcomes。
- `both_properties_failed` 是运行级复合指标，不是第三个属性。

B2日志带有Full-v1.0和B-2标记，但缺少独立环境快照；不能反推精确工具构建版本。

## 4. 六个合成基准主比较

只选择每个基准的Original和Full-K1：

| 基准 | Original | Full-K1 |
|---|---:|---:|
| BranchValue | 28/30 | 30/30 |
| NoisyFourStep | 26/30 | 30/30 |
| ResetExample | 27/30 | 30/30 |
| RepeatedCall | 30/30 | 30/30 |
| AlternativePath | 30/30 | 30/30 |
| MultiProperty | 30/30 | 30/30 |
| 描述性总计 | 171/180 | 180/180 |

这是跨两个批次和异质配置的描述性总计。B2 Original的seqLen为3，Formal main为4；MultiProperty还使用 `stopOnFail=false`。因此不进行忽略基准异质性的pooled显著性检验。

## 5. Public C-1：五个公开基准

数据入口：[public-c1-group-summary.csv](../results/public-benchmarks/c1/public-c1-group-summary.csv)。

| 基准 | Original | Full-K1 | Full-K5 |
|---|---:|---:|---:|
| echidna-flags | 30/30 | 30/30 | 30/30 |
| echidna-multi | 24/30 | 30/30 | 29/30 |
| exercise2-access-control | 30/30 | 0/30 | 30/30 |
| smartbugs-multifunc | 30/30 | 30/30 | 30/30 |
| smartbugs-onefunc | 30/30 | 30/30 | 30/30 |
| 描述性总计 | 144/150 | 120/150 | 149/150 |

### exercise2-access-control

- 有效路径是 `Owner() -> resume()`，排名第2。
- Top-1是 `Owner() -> pause()`，它保持属性成立。
- K1没有有效路径，因此0/30。
- K5包含rank 2路径，因此30/30。

这是当前最重要的负面结果：Top-1并不总是安全选择。

### smartbugs-multifunc

- 最短已知路径 `init() -> run(uint256)` 排名第3，不在K1。
- K1包含另一条有效路径 `init() -> run(uint256) -> run(uint256)`。
- 因此“最短路径不在K1”不等于“K1没有有效触发路径”。

### echidna-multi

- Original为24/30，K1为30/30，K5为29/30。
- K5唯一未发现反例的是seed 7，它完整运行到testLimit。
- 单个右删失样本不足以证明K5系统性比K1差。
- K5的KM中位操作时间为5.77秒，Original为2.91秒；即使log-rank曲线差异显著，也不能声称K5更快。

## 6. 候选路径实验

数据入口：[formal-candidate-summary.csv](../results/formal/formal-candidate-summary.csv) 与 [formal-tie-aware-ranking.csv](../results/formal/formal-tie-aware-ranking.csv)。

| 基准 | Dependency retained | Property retained | Repeat retained | Full retained |
|---|---:|---:|---:|---:|
| Noisy | 30 | 3 | 3 | 3 |
| Reset | 37 | 19 | 33 | 33 |
| Branch | 18 | 7 | 7 | 7 |
| Repeated | 7 | 2 | 3 | 3 |
| 合计 | 92 | 31 | 46 | 46 |

92→31表示四个基准retained paths求和从92降到31，不是DFS全部节点、运行数或跨合约全局唯一序列数。

## 7. 预处理开销

每个正式合成基准重复测量10次。完整流程包括：

1. 读写依赖提取；
2. Property/Repeat路径生成；
3. 值约束提取；
4. 值引导排序；
5. Harness生成；
6. Harness编译。

四个基准总时间中位数：

| 基准 | 中位秒数 |
|---|---:|
| Branch | 1.310297 |
| Noisy | 1.311646 |
| Repeated | 1.304164 |
| Reset | 1.324163 |

四个中位数的算术平均是1.3125675秒，不是pooled median。流程不含Echidna，也没有大型真实工程实验。

## 8. 附录级实验

| 实验 | 结果 | 正确用途 |
|---|---|---|
| Dependency Top-K | Noisy K1/K3/K5为0，K6/K10为30 | 展示目标路径进入K的重要性 |
| Repeat ablation | visits1为0/30，visits2为30/30 | 重复访问机制证据 |
| Value invariance | 原名、重命名、声明顺序均30/30 | 单一基准上的有限稳健性 |
| Noisy permutation | 正确排列5/5，其余115次均未发现 | 顺序机制演示 |

这些来自不同早期批次，不能与Formal主批次的同名组合并计算。

## 9. 不进入主结论的数据

- V2开发结果；
- C0兼容性筛查和修复前结果；
- smoke和runner-output；
- 手工Harness机制演示；
- ThreeStep和早期10-seed pilot；
- Noisy random混杂基线；
- 早期与Formal同名结果的pooled汇总。

## 10. 当前论文证据强弱

### 较强

- 正式批次每组30个seed且原始日志完整；
- 组件机制有对应受控案例；
- 候选和并列排名可以追溯到JSON；
- C-1保留失败结果并正确处理右删失；
- 数据状态语义、白名单和checksum已经建立。

### 较弱

- 公开基准只有5个；
- SMARTIAN 外部基线目前只覆盖两个简单整数目标，尚不足以支持广泛竞品结论；
- Harness与Original存在调用者和交易原子性差异；
- 没有大型真实工程上的规模实验；
- 合成基准为组件量身设计；
- 当前公开基准成功率结果不足以支持普遍显著优势。

因此后续向CCF-C类完整论文补强时，优先级应是：语义适用范围、外部基准、竞品比较和可扩展性，而不是简单增加更多seed。

新增补强实验与旧正式数据隔离存放。语义适用性研究入口为[results/semantic-applicability/v1](../results/semantic-applicability/v1/README.md)，其静态筛查结果不是语义等价证明，也不进入已有1050次运行的分母。

语义补强的第一轮结果为：11/11个固定已知成功路径在直接调用模型与实际生成Harness之间得到相同的属性相关最终结果；同时，负面对照确认调用者交替和wrapper整体回滚会产生差异。因而该结果支持的是“受限成功路径一致性”，不是完整的多交易语义等价。exercise2仍为条件支持案例。

C2公开基准扩充入口为[results/public-benchmarks/c2-screening](../results/public-benchmarks/c2-screening/README.md)。当前已冻结筛选字段和防选择偏差规则，C2新增候选数仍为0。SMARTIAN 已完成两个 SmartBugs 整数属性的 `IntegerBug`/Echidna 独立重放和 2×30 外部基线批次；该批次作为已有 C-1 目标的外部工具对照，不追溯性纳入正式分母。ConFuzzius、IR-Fuzz、MuFuzz 和 ItyFuzz 仍无本地可用入口。这些外部基线缺失或语义不对齐不能由已有内部消融替代。

为补充内部公平控制，已建立[Matched Random Top-K](../results/matched-random-v1/README.md)预注册：在同一Full候选池内均衡随机选择Top-1，路径调度与Echidna fuzz seed分离。11个目标中9个非退化，270次正式运行已完成；66个去重Harness全部通过编译预检，正式批次为87/270次falsified、183/270次budget_exhausted。该基线只检验候选池内部排序作用，不能替代外部SOTA。
