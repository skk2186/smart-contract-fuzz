# SMARTIAN 正式批次冻结提案

状态：提案参数已冻结，正式外部基线批次已完成；不属于 C2 分母。

## 范围

建议只把 `smartbugs-multifunc` 和 `smartbugs-onefunc` 作为已完成 C-1 的外部基线对照，不追溯性地把它们改写成新的 C2 候选。`candidate-registry.tsv` 保持 5 个 `legacy_reference`，C2 分母保持 0。

原因：两个目标已经有 C-1 的 Original/Full-K1/Full-K5 数据；把它们重新登记为 C2 会引入选择和重复使用偏差。SMARTIAN 结果可以作为“同一属性上的外部工具对照”，但必须单独标注。

## 建议冻结参数

| 项目 | 冻结值 |
|---|---|
| Solidity compiler | 0.4.25；使用 `/home/skk/.solc-select/artifacts/solc-0.4.25/solc-0.4.25` 直接编译 |
| Smartian binary | `baselines/smartian/src/bin/Release/net8.0/Smartian.dll` |
| Smartian budget | 每个目标 30 秒，与 C-1 `timeout: 30` 对齐 |
| repeats | 每个目标 30 次，run-id 1–30 |
| input | 同源 bytecode + ABI；不把 Solidity 源码直接交给 SMARTIAN |
| Smartian command | `fuzz -p <bytecode> -a <abi> -t 30 -o <output> -v 0` |
| success | 产生 `IntegerBug`，且 bug trace 满足已验证的 `count <= 1` 反例语义 |
| non-success | 完整结束但未产生匹配 `IntegerBug`，记为 budget exhausted；启动/分析失败单独记分母 |
| seed | SMARTIAN CLI 无公开 seed 参数；记录 run-id、完整命令、环境快照，不声称与 Echidna seed 一一对应 |
| primary metrics | falsified/valid、time-to-first-IB、process wall time、静态分析时间、testcase 数 |

## 启动前检查

```bash
python3 analyzer/validate_c2_candidate_registry.py \
  --registry results/public-benchmarks/c2-screening/candidate-registry.tsv

test "$(cat /home/skk/.solc-select/global-version)" = "0.8.20"
test -x /home/skk/.solc-select/artifacts/solc-0.4.25/solc-0.4.25
test -f baselines/smartian/src/bin/Release/net8.0/Smartian.dll
```

全局 Solidity 版本检查是为了确认实验不会悄悄改动用户已有的 0.8.20 环境；实际 0.4.25 编译应调用固定二进制路径。

本批次按“作为 C-1 外部基线运行”的范围执行。如果后续要把目标纳入 C2，则必须先更新候选来源、冻结状态和分母说明，不能直接复用本提案。

## 批次结果

按上述参数完成 60 次运行（两个目标各 30 次）。结果为：

- `smartbugs-multifunc`：30/30 完整运行，30/30 产生 `IntegerBug`；
- `smartbugs-onefunc`：30/30 完整运行，30/30 产生 `IntegerBug`；
- 退出码：60/60 为 0；启动/分析失败：0；预算耗尽但未发现：0。

原始日志、测试用例、manifest、CSV 和 JSON 摘要保存在
`results/public-benchmarks/c2-screening/smartian-formal-20260806/`。这只是同一属性上的外部工具对照，不应与 C-1 的 Echidna seed 结果做 seed 对齐或直接合并统计。
