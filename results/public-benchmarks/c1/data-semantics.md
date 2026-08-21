# C-1 派生数据语义

- `falsified`：日志中存在 Echidna 属性反例。即使同一日志也包含测试预算终止消息，仍优先分类为 `falsified`。
- `budget_exhausted`：日志未包含属性反例，并明确包含 `Test limit reached. Stopping.`。它只表示在当前预算内未发现反例，不表示性质已被证明。
- `passed`：日志没有反例和预算耗尽证据，但 Echidna 明确输出属性 `passed` 或 `passing`。
- `startup_error`：Echidna 正式测试前出现已识别的编译、路径、配置或编译器兼容性错误。
- `incomplete`：日志不满足以上任何一种可确认状态，包括只有运行完成标记但无法确认属性结果的日志。

`valid_runs` 包含 `falsified`、`budget_exhausted` 和 `passed`，不包含 `startup_error` 或 `incomplete`。`success_rate` 定义为 `falsified_runs / valid_runs`。

日志中的 `Total calls` 是 Echidna 外层调用数，不是统一的底层目标函数调用数。Original 使用 `seqLen=4`，Echidna 可以构造由多个独立目标交易组成的序列；Harness 使用 `seqLen=1`，但一次 Harness 外层调用可能在同一交易内封装多个目标函数调用。因此 Original 与 Harness 的调用者、原子回滚边界及每次外层调用包含的目标调用数不同，二者的 `Total calls` 不能直接解释为等量目标工作。

路径预检中的 `any_known_triggering_path` 只检查当前由人工审计合约逻辑或原始反例确认的已知有效路径。它不会把候选集中结构上存在的所有路径自动视为有效，也不构成完整的语义可达性证明。
