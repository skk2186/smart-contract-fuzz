# C7 下一步决策

## Decision

Decision: GO_TO_C8_REFERENCES_AND_TABLES

## 依据

完整中文论文初稿已经形成，包含方法、实验设计、controlled evidence、adapted real-source evidence、结果、讨论、有效性威胁和结论。既有边界已固化：

- 四个 adapted real-source candidates、120 条预注册运行、80 条可用/描述性记录和 40 条工程限制记录；
- 两个 Echidna-origin candidates 组成窄范围 comparable subset；
- SmartBugs Original-only 20 条 falsified 仅作可运行性与属性违反观测说明；
- SmartBugs Harness 的 40 条 compile_error 不参与比较；
- 1 条 budget_exhausted 仅为 right-censored；
- 不声称 Original 与 Harness 语义等价，不使用 Total calls 直接声称 speedup；
- exercise2 未执行且未纳入 supported pool；
- 未运行新实验，未修改旧证据。

## C8 工作重点

1. 核验 [R1]–[R4] 真实参考文献并统一引用格式。
2. 从正式 machine-readable CSV/TSV 生成表 1–表 5 的最终排版版本。
3. 补充受控场景逐任务统计、真实来源 candidate 适配说明和表注。
4. 检查摘要、正文、图表和 Threats to Validity 的术语与分母一致性。
5. 由研究者复核所有真实来源结论仍限定为 adapted real-source evidence。

## 其他决策

- 不进入 C7R：初稿结构已完整。
- 暂不进入 B6：现有受控机制证据与窄范围真实来源补充足以形成初稿；是否扩充真实合约可作为审稿后或后续实验计划，不是当前初稿整合的前置条件。
