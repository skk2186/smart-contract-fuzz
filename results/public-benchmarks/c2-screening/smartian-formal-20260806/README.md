# SMARTIAN 正式外部基线批次

本目录保存 2026-08-06 按冻结提案执行的 SMARTIAN 外部基线结果，不属于 C2 候选分母。

- 目标：`smartbugs-multifunc`、`smartbugs-onefunc`
- 编译器：Solidity 0.4.25 固定二进制
- SMARTIAN：commit `eca1ed1d60c88ec5402055a05b59174b7288264c`
- 预算：每次 30 秒；每目标 30 次；共 60 次
- 结果：60/60 退出码 0，60/60 完整结束，60/60 产生 `IntegerBug`
- seed：SMARTIAN CLI 未公开 seed 参数，因此使用 run-id 记录重复运行，不声称与 Echidna seed 对齐

文件说明：

- `manifest.txt`：运行环境和成功定义；
- `run-status.tsv`：逐次退出码、耗时、输出计数和路径；
- `summary.csv` / `summary.json`：解析后的分组摘要；
- `inputs/`：0.4.25 编译产生的 bytecode/ABI；
- `runs/`：原始 SMARTIAN 日志、testcase 和 `IntegerBug` 反例。

成功定义仅适用于这两个已完成 oracle 对齐的整数目标。不要把 SMARTIAN 的 `IntegerBug` 数量与其他漏洞类别或未对齐的 Echidna 属性直接合并。
