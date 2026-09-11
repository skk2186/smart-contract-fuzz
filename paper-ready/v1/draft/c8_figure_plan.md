# 图表规划

## 图 1：面向显式安全属性的多交易序列生成框架

- 放置：方法设计章节。
- 要点：property extraction → dependency slicing → require/value matching → bounded repetition → Top-K ranking → seed instantiation/path execution；末端分出 native execution 与 Harness replay。
- 禁止含义：不表示完整静态证明，不表示所有依赖精确恢复，不表示 Harness 与原生执行完全相同。
- 提示词：学术风格自左向右框图，左侧显式属性和状态变量，中间依赖切片、条件/值匹配、有界重复、Top-K，右侧序列实例化，并用虚线分隔 native execution 与 external Harness/replay，标注 distinct execution models。

## 图 2：证据分层与结论边界

- 放置：实验设计章节末尾或结果章节开头。
- 要点：controlled evidence 作为主机制证据；adapted real-source evidence 作为补充边界检查，再分为 comparable Echidna-origin、SmartBugs Original-only descriptive 和 excluded Harness engineering rows。
- 禁止含义：不合并证据层成功率，不把 compile_error 画成发现失败，不表示 Original/Harness 同语义。
- 提示词：分层树图，显示 4 candidates、120 runs、80 usable/descriptive、40 excluded engineering rows，以颜色区分 comparable、descriptive-only 和 compile_error exclusion，标注结论边界。

## 图 3：结果概览与可比性边界

- 放置：实验结果章节。
- 要点：上层逐场景 controlled result；下层真实来源 120 条拆为 80 usable/descriptive 与 40 engineering excluded，其中 60 comparable、20 descriptive-only，60 中含 1 条 right-censored。
- 禁止含义：不画跨层 pooled success rate，不比较 compile_error 性能，不把 right-censored 标成安全，不把总调用量画成 speedup。
- 提示词：两层论文信息图，上层逐场景结果卡片，下层 120 条 adapted real-source records 的分组条形/Sankey，标出 60 comparable、20 descriptive-only、1 right-censored、40 engineering excluded，并标注 falsified-only descriptive statistics 和 distinct execution models。
