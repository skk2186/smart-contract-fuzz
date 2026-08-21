# RepeatedCallExample 有界重复调用消融实验

## 正确漏洞路径

deposit()
→ deposit()
→ unlock()
→ withdraw(uint256)

## 对比设置

Visits-1 组规定每个函数在一条候选路径中最多出现一次。

Visits-2 组允许每个函数在一条候选路径中最多出现两次。

两组均使用相同的：

- 状态依赖分析；
- 安全属性相关过滤；
- 状态值约束重排序；
- 最大路径长度；
- Top-K；
- Echidna 配置；
- 随机种子数量。

## 路径生成结果

Visits-1 无法生成包含两次 deposit() 的正确交易序列。

Visits-2 能够通过 deposit() 对 depositCount 的自依赖关系生成：

deposit()
→ deposit()
→ unlock()
→ withdraw(uint256)

## 实验结论

禁止函数重复访问会使路径生成器无法表示需要多次调用同一函数才能
推进状态的漏洞路径。

加入有界重复调用支持后，路径生成器能够覆盖该类场景，并自动生成
可触发属性失败的 Echidna Harness。

有界访问次数能够避免无约束循环遍历，但访问上限增大会导致候选路径
数量和搜索空间膨胀，因此后续需要评估 max_function_visits 参数对
候选数量及测试效率的影响。

## 当前限制

当前实现只允许有界重复枚举，并未根据 require(depositCount == 2)
自动推导 deposit() 必须调用两次。

对于复杂循环次数、参数相关递增、跨函数累积状态等场景，仍需要更强
的状态变化分析或动态执行反馈。
