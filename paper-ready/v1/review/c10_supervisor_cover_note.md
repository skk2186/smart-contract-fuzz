# 论文初稿导师审阅说明

## 当前目标

目前已形成一版面向 C 会投稿的中文论文初稿，以及与正文对应的表格、图表规划、引用 registry 和审计材料。本轮工作的目标是把方法叙事和证据边界整理到可供导师集中审阅的状态，不以增加实验数量为前提。

## 论文核心主张

论文研究面向显式安全属性的智能合约多交易模糊测试。核心主张是：将属性读取的状态变量作为序列筛选的起点，并结合状态读写依赖、条件约束匹配、状态值方向匹配、有界重复和 Top-K 候选序列，可以为动态模糊测试提供更聚焦、可解释的交易前缀。该主张主要由 controlled evidence 支撑。

## 方法创新点

方法的价值不在于重新实现一个通用 fuzzing engine，而在于把安全属性语义前置到状态依赖路径筛选中，并把条件、值方向、重复调用和候选排序组织成统一的序列生成流程。同时，论文明确区分原生多交易执行与 Harness 执行，不把路径生成结果等同于语义证明。

## 实验主线

受控场景是主机制证据，用于回答属性相关筛选和组合约束是否能够处理预先定义的状态路径障碍。adapted real-source evidence 是补充性的外部有效性检查，覆盖 4 candidates 和 120 runs，其中 80 usable/descriptive records，40 compile_error engineering rows 作为工程限制单独报告。两个 Echidna-origin candidates 构成窄范围 comparable subset，SmartBugs Original-only 结果只作描述。

## 真实来源实验边界

真实来源材料不是大规模真实合约评估。SmartBugs Harness 的 compile_error 不代表方法检测失败，budget_exhausted 只表示 right-censored，Original and Harness are distinct execution models。论文不据此声称生态范围优越性，也不将不同执行模型的 Total calls 直接解释为 speedup。

## 当前不继续补实验的理由

当前受控证据能够支撑机制层面的论文叙事，真实来源材料能够补充适用边界和工程限制。继续增加相同类型的 seed 数量不能替代更多独立来源、更多 Solidity 版本和更完整的 Harness 语义支持。因此，在导师确认论文定位之前，优先完成主张审阅、引用复核、格式化和图表重绘。

## 希望导师重点审阅的问题

1. 论文题目和方法定位是否足以形成清晰的 C 会投稿主题。
2. 属性相关路径筛选与条件/值方向匹配的创新边界是否需要进一步收窄。
3. baseline 论文是否已经选择到足以支撑相关工作和实验定位。
4. controlled evidence 是否适合作为主机制实验，六个受控场景的分组是否清楚。
5. B-2 扩展结果应放入主文结果小节还是附录。
6. 4 candidates、120 runs 的真实来源材料是否接受作为补充而非主实验。
7. SmartBugs Harness 的 40 条 compile_error 是否需要在正文和 threats to validity 中保留同等篇幅。
8. 真实来源 comparable subset 的统计是否需要仅展示发现轨迹描述，而不做性能排名。
9. high_confidence 参考文献是否需要重新从 ACM、IEEE 或 DBLP 导出。
10. 当前表格和图表占位是否符合目标会议模板，是否需要压缩到主文并将细节移入附录。
