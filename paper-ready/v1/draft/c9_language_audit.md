# C9 语言与边界审计

## 检查结果

| 检查项 | 结果 | 说明 |
|---|---|---|
| 是否出现内部阶段编号 | NO | 正文副本不含 B5、B5-7、C7、C8、C9、V1、V2 |
| 是否出现 forbidden claims | NO | 未写大规模真实合约评估或生态范围优越性 |
| 是否出现 large-scale real-world evaluation | NO | 仅使用少量 adapted real-source evidence 的边界表述 |
| 是否出现 ecosystem-wide superiority | NO | 保留明确否定和结论边界 |
| 是否把 compile_error 当性能结果 | NO | 40 条记录只作为 engineering limitation |
| 是否把 budget_exhausted 当安全 | NO | 唯一删失记录写为 right-censored |
| 是否把 Original/Harness 写成语义等价 | NO | 明确 Original and Harness are distinct execution models |
| 是否存在明显工程报告口吻 | 基本 NO | 已删除文件、阶段和流水线导向的正文措辞；技术边界仍保留必要术语 |
| 是否存在 AI 味过重段落 | NO | 段落围绕单一论点，减少机械排比和重复转折 |
| 是否术语前后不统一 | 基本 NO | 统一为显式安全属性、属性相关变量、状态读写依赖、条件约束匹配、状态值方向匹配、有界重复、Top-K 候选序列 |
| 是否仍有参考文献风险 | YES，已隔离 | 2 条 high_confidence 需定稿前复核，1 条 unresolved 未进入 BibTeX |

## 必须保留的事实口径

- controlled evidence 是主机制证据。
- adapted real-source evidence 是补充外部有效性证据。
- 真实来源为 4 candidates、120 runs，其中 80 usable/descriptive records，40 compile_error engineering rows。
- SmartBugs Original-only 仅作描述，Harness compile_error 不进入比较。
- budget_exhausted 是 right-censored。
- 不把不同 execution model 的 Total calls 写成 speedup。
