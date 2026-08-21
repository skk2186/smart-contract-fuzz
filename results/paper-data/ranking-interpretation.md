# Formal 候选空间与排名解释

`formal-candidate-summary.csv` 中四个正式合成基准的 `dependency_retained_paths` 分别为30、37、18、7，总和92；`property_retained_paths` 分别为3、19、7、2，总和31。减少61条，精确比例为 `61 / 92 = 66.3043478%`。

92和31都是四个基准 retained paths 的逐基准求和，不是：

- DFS 扩展的全部节点数；
- fuzzing运行数；
- 跨基准去重后的全局唯一序列数；
- 公开基准与合成基准的合并路径数。

Full 阶段四条人工确认的正确路径均为唯一Top-1，即 `higher_score_paths=0`、`equal_score_paths=1`。

必须同时解释 display rank 和 tie-aware rank。ResetExample 在 Property 阶段的 display rank 为1，但六条路径同分，tie-aware rank 为1–6；Repeat 阶段 display rank 为5，但18条路径同分，tie-aware rank 为1–18。Full 阶段才通过值匹配把目标路径区分为唯一Top-1。

因此不得把 Reset 描述成严格分数意义的“rank 1下降到5再恢复到1”。准确表述是：

> 重复访问扩大了候选集合及同分集合；值匹配随后将目标路径区分为唯一Top-1。

候选路径由92减少到31只说明候选空间变化，不自动等价于 fuzzing 性能提升。运行结果与候选变化可以并列报告，但不能把观察关联写成未经控制的一般因果结论。
