# SMARTIAN 预言机/属性对齐预检

日期：2026-08-06  
状态：完成 2 个整数样例的独立属性重放和对齐验证；尚未纳入正式 C2。

## 已验证的两个候选

`smartbugs-multifunc` 和 `smartbugs-onefunc` 都按 C-1 manifest 使用 Solidity 0.4.25，属性为
`echidna_count_does_not_underflow: count <= 1`。使用已安装的 0.4.25 编译器二进制直接生成 bytecode/ABI，再用固定 SMARTIAN Release 程序运行 10 秒；两个运行均退出码 0，并生成 `IB` 反例文件。

反例的关键序列为：

- multifunc：`init()` → `run(25)`；
- onefunc：`run(0)` → `run(25)`。

两条序列均会让 `uint256 count` 从初始值 1 发生下溢，因此与 `count <= 1` 被违反的语义一致。随后在隔离环境 `/tmp/echidna-tools` 中使用同一 0.4.25 编译器运行 Echidna（`--test-limit 100`），两个属性均以退出码 1 被明确标记为 `property_falsified`，其最小调用序列分别为 `init() → run(2)` 和 `run(0) → run(2)`。Echidna 的退出码 1 在这里表示发现反例，不是启动失败。

Echidna 输出有 `slither not found` 警告，但属性执行和反例输出均完成；本次没有安装 Slither，也没有修改项目或全局 Solidity 版本。此前用 0.4.23 做的兼容性试跑保留在临时目录，但不计入正式对齐记录。

逐候选字段见 [`smartian-oracle-alignment.tsv`](smartian-oracle-alignment.tsv)，机器可读摘要见 [`smartian-oracle-alignment.json`](smartian-oracle-alignment.json)。运行产物保存在 `/tmp/smartian-oracle-alignment-20260806`。

## 当前阻塞点

两个整数候选的属性重放已通过；当前阻塞转为正式实验冻结：预算、发送者模型、交易语义和是否把这两个已有 C1 legacy 目标纳入新的 C2 分母尚未作出预注册决定。`echidna-multi`、`echidna-flags` 和 `exercise2-access-control` 仍没有 SMARTIAN 原生等价 bug oracle，暂列 blocked。

## 下一道门槛

1. 保存 Echidna 与 SMARTIAN 的完整反例和调用者/交易模型；
2. 冻结预算、初始状态、ABI、编译器和成功定义；
3. 明确这两个 legacy 目标是否允许进入新的 C2 分母，避免追溯性选择；
4. 通过后再把候选状态推进到 `property_validated`/`frozen_for_c2`，当前注册表保持不变。
