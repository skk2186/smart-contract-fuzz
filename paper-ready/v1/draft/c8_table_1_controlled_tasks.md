# 表 1：受控场景任务概览

该表描述为特定机制障碍设计的 controlled evidence，不代表真实合约生态中的任务分布。B-2 扩展与 formal-main 行保持分组，不作未经说明的 pooled 结论。

| scenario/task | target property | obstacle type | method component tested | run denominator | evidence role |
|---|---|---|---|---:|---|
| branch-value | BranchValueExample; echidna_value_safe | 分支可达性依赖状态值方向 | 属性相关切片 + 状态值写入方向匹配 | 每个方法 30 次 | controlled evidence；机制组件验证 |
| noisy-four-step | NoisyFourStepExample; echidna_value_safe | 四步序列中混入与属性无关的状态路径 | 属性相关性筛选 + 依赖排序 + Top-K | 每个方法 30 次 | controlled evidence；无关路径抑制 |
| reset-example | ResetExample; echidna_value_safe | 状态重置/覆盖使前置状态容易失效 | 写读依赖 + require 条件匹配 + 状态更新方向 | 每个方法 30 次 | controlled evidence；状态演化机制 |
| repeated-call | RepeatedCallExample; echidna_value_safe | 属性违反需要有界重复调用 | 有界重复 + 属性相关路径保留 | 每个方法 30 次 | controlled evidence；重复调用机制 |
| alternative-path | AlternativePathExample; echidna_value_safe | 多个候选阶段路径均可到达目标，且含阶段条件 | require 条件匹配 + Top-K 候选路径排序 | 每个方法 30 次；B-2 扩展 | controlled evidence；扩展案例，单独报告 |
| multi-property | MultiPropertyExample; echidna_value_a_safe 与 echidna_value_b_safe | 同一序列需要覆盖多个显式属性及共享前缀 | 属性相关性聚合 + 依赖切片 + Top-K | 每个方法 30 次；B-2 扩展 | controlled evidence；多属性扩展，单独报告 |

注：受控场景用于解释属性相关筛选、值方向、条件匹配、有界重复和 Top-K 的机制作用；不能单独证明对未覆盖的真实合约类型具有普遍效果。
