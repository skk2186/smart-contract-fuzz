# 最终图示提示词

## 图 1：面向显式安全属性的多交易序列生成框架

- 中文图题：面向显式安全属性的属性定向交易序列生成框架。
- English caption：An Explicit-Property-Guided Framework for Multi-Transaction Sequence Generation.
- 画面结构：自左向右六个处理模块，依次为 property extraction、dependency slicing、condition/value matching、bounded repetition、Top-K ranking 和 seed instantiation/path execution。
- 关键元素：显式安全属性、属性相关变量、状态读写依赖图、require 条件、状态值方向、重复上限、候选序列和动态模糊测试器。
- 箭头关系：属性读取变量指向反向依赖切片，切片结果指向条件和值方向匹配，匹配结果指向有界重复与 Top-K 排序，排序结果指向种子实例化和路径执行。
- 语义边界：在执行端用虚线分开 native multi-transaction execution 和 external Harness/replay，并标注 Original and Harness are distinct execution models。
- 禁止含义：不能画成完整静态证明器，不能表示所有依赖都能精确恢复，不能暗示 Harness 与原生执行完全相同。
- 可复制绘图提示词：绘制一张黑白加蓝色强调色的学术系统框图，自左向右展示显式安全属性解析、属性相关变量识别、状态读写依赖切片、require 条件和状态值方向匹配、有界重复、Top-K 候选排序以及序列实例化；右端分出 native execution 与 external Harness/replay 两条虚线分支，标注 distinct execution models，不添加性能百分比或安全保证符号。

## 图 2：证据分层与结论边界

- 中文图题：受控机制证据、适配真实来源证据与工程排除项的证据分层。
- English caption：Evidence Stratification for Controlled Mechanism Results and Adapted Real-Source Boundary Checks.
- 画面结构：顶层 evidence 分为 controlled evidence 和 adapted real-source evidence；真实来源分支进一步分为 comparable Echidna-origin、SmartBugs Original-only descriptive 和 excluded Harness engineering rows。
- 关键元素：六个受控场景、4 candidates、120 runs、80 usable/descriptive records、40 compile_error engineering rows、59 falsified comparable rows、20 descriptive rows 和 1 right-censored row。
- 箭头关系：controlled evidence 指向主机制结论；adapted real-source evidence 指向补充边界结论；compile_error 分支指向 engineering limitation，不指向方法失败。
- 语义边界：用不同颜色或线型明确 comparative、descriptive-only 和 excluded engineering 三种角色。
- 禁止含义：不能绘制跨层 pooled success rate，不能把 compile_error 画成漏洞发现失败，不能把 Original 与 Harness 画成同一语义路径。
- 可复制绘图提示词：绘制一张分层树图，根节点为 evidence，分出 controlled evidence 和 adapted real-source evidence；真实来源分支显示 4 candidates、120 runs、80 usable/descriptive records 与 40 compile_error engineering rows，并以绿色、灰色和红色虚线区分 comparable、descriptive-only 和 engineering exclusion，所有分支标注 claim boundary。

## 图 3：结果概览与可比性边界

- 中文图题：受控结果与适配真实来源结果的可用性和可比性概览。
- English caption：Overview of Controlled Results, Usable Real-Source Records, and Comparability Boundaries.
- 画面结构：上半部分用逐场景结果卡片展示 controlled evidence；下半部分将真实来源 120 runs 分为 80 usable/descriptive records 和 40 compile_error engineering rows，再显示 60 Echidna-origin comparable rows、20 SmartBugs Original-only descriptive rows 和其中 1 条 right-censored。
- 关键元素：Full-K1 180/180、Original 171/180、79 falsified、1 right-censored、40 compile_error，以及 falsified-only descriptive metrics。
- 箭头关系：受控结果指向机制解释；真实来源可比较子集指向窄范围描述；Original-only 指向可运行性描述；compile_error 指向工程限制。
- 语义边界：在图注中说明 Original and Harness are distinct execution models，所有 calls-to-failure、sequence-length 和时间指标只针对 falsified rows 作描述性说明。
- 禁止含义：不绘制 pooled success rate，不比较 compile_error 性能，不将 right-censored 标成安全，不将 Total calls 绘制成 speedup。
- 可复制绘图提示词：绘制一张两层论文信息图，上层为六个 controlled evidence 场景结果卡片，下层为 120 条 adapted real-source records 的分组条形图或 Sankey 图，分出 80 usable/descriptive records 与 40 compile_error engineering rows，并在 80 中标出 60 comparable、20 descriptive-only 和 1 right-censored；使用克制配色，不加入大规模生态或排行榜视觉隐喻。
