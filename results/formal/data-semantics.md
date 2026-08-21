# Formal 派生数据语义

- `falsified`：日志中存在指定 Echidna 属性的反例。即使同一日志也含测试预算终止消息，仍优先归为 `falsified`。
- `budget_exhausted`：没有反例，且日志明确含 `Test limit reached. Stopping.`。它只表示当前预算内未发现反例，不表示性质已被证明或合约安全。
- `passed`：没有反例和预算耗尽证据，但属性明确输出 `passed` 或 `passing`。
- `startup_error`：正式测试前出现已识别的编译、路径、配置或编译器兼容性错误。
- `incomplete`：无法由以上证据确认结果。

`valid_runs` 包含 `falsified`、`budget_exhausted` 和 `passed`，不包含 `startup_error` 或 `incomplete`。`success_rate = falsified_runs / valid_runs`。

Formal Original 使用 `seqLen=4`，Harness 使用 `seqLen=1`。Harness 的一次外层调用可能在同一交易中封装多个目标函数调用；Original 则由 Echidna 构造多个独立目标交易。二者在调用者、原子回滚边界及每次外层调用包含的目标操作数上不同。因此日志中的 `Total calls` 只能解释为 Echidna 外层调用，不能作为等量底层目标函数调用，也不能据此直接计算等工作量加速。

四个合成基准是为属性噪声、状态值约束、重复调用和干扰路径等机制构造的受控案例。它们能够支持范围明确的机制验证，不能直接证明方法对外部或任意智能合约的泛化能力。
