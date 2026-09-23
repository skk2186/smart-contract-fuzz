# C17 术语统一表

| 原英文术语 | 中文译法 | 首次出现写法 | 后文统一写法 | 是否允许保留英文 | 备注 |
|---|---|---|---|---|---|
| property | 属性 | 显式安全属性 | 属性 | 仅在函数名或字段名中保留 | 中文叙述统一使用“属性” |
| property-specific / per-property | 属性级 / 单属性 | 属性级规划（单属性模式） | 属性级、单属性模式 | 仅在代码字段或实验标签中保留 | PER_PROPERTY 为实验标签 |
| read-set | 读取变量集合 | 属性的读取变量集合 | 读取变量集合 | 代码字段中保留 | 与写入变量集合对应 |
| target function | 目标函数 | 目标函数 | 目标函数 | 代码字段中可保留 | 不写成 target function |
| backward dependency path | 反向依赖路径 | 反向依赖路径 | 反向依赖路径 | 代码实现说明中可保留函数名 | 描述候选结构 |
| bounded repetition | 有界重复 | 有界重复 | 有界重复 | 参数名中保留 | 对应访问次数和展开次数限制 |
| lightweight value evidence | 轻量值证据 | 轻量值证据 | 轻量值证据 | 代码字段中可保留 | 只覆盖常量写入和简单条件 |
| Top-K | 前 K 个候选 | 前 K 个候选（Top-K） | 前 K 个候选 | 实验标签中允许 K | 避免整段英文表达 |
| Harness | 测试封装合约 | 测试封装合约（Harness） | 测试封装合约 | 首次出现后优先用中文 | 函数名和生成器名称可保留 |
| Original Echidna | 原生 Echidna 多交易模式 | 原生 Echidna 多交易模式 | 原生模式 | 结果标签中可保留 Original | 明确交易语义 |
| compile_error | 编译错误状态 | compile_error（编译错误状态） | 编译错误状态 | 状态字段中保留英文 | 工程状态单独统计 |
| budget_exhausted | 预算耗尽状态 | budget_exhausted（预算耗尽状态） | 预算耗尽状态 | 状态字段中保留英文 | 作为右删失观测 |
| right-censored observation | 右删失观测 | 右删失观测 | 右删失观测 | 一般不保留英文 | 统计状态术语 |
| engineering status | 工程状态 | 工程状态 | 工程状态 | 一般不保留英文 | 编译和适配状态 |
| candidate | 候选序列 | 候选序列 | 候选序列 | 变量名中可保留 | 不使用 candidate 作普通名词 |
| rank | 排序位置 | 排序位置 | 排序位置 | 实验字段中可保留 | 与前 K 命中分开解释 |
| seed | 随机种子 | 随机种子 | 随机种子 | 配置字段中可保留 | 运行记录中可写 seed |
