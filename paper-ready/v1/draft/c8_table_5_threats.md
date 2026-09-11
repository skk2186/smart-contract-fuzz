# 表 5：有效性威胁与缓解措施

| threat | affected claim | mitigation | remaining limitation |
|---|---|---|---|
| controlled benchmarks 外部有效性有限 | 受控结果是否代表一般真实合约 | 固定障碍、属性和分母，定位为 controlled evidence | 场景小且由研究者设计，不能估计生态分布 |
| 真实来源 candidate 数量有限 | adapted real-source evidence 的广泛性 | 报告 4 candidates、120 runs 与 80/40 分层 | 不能推断整个真实合约生态 |
| adapted source 与原始合约存在工程适配 | 真实来源结果的外部有效性 | 记录编译器、属性接口和适配边界 | 适配可能改变入口、初始化或可观察接口 |
| 人工属性接口/标注 | 属性是否表达原任务意图 | 保留属性名、provenance 和可审计记录 | 可能遗漏原始意图或引入表达偏差 |
| Solidity 0.4.25 Harness import-path compile_error | Harness 比较结果是否可解释 | 40 条记录列为 excluded engineering rows | 尚无完善的跨版本 Harness 迁移路径 |
| budget_exhausted 右删失 | 未发现反例如何解释 | 明确写为 right-censored | 不能据此推断安全，需要删失分析 |
| Original/Harness execution-model difference | 两种执行模式能否直接比较 | 只做窄范围、同 candidate/property/预算描述 | caller、回滚、交易边界可能仍不同 |
| 版本与复杂类型覆盖不足 | 对其他 Solidity 版本和复杂参数的适用性 | 报告当前边界并列为未来工作 | 未覆盖全部版本、复杂结构和调用者模型 |
