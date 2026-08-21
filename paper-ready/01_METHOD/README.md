# 01 方法与实现

## 论文中应描述的 V1 流程

```text
状态读写提取 -> Dependency 候选 -> Property 过滤 -> Repeat 扩展
             -> Value 约束匹配/排序 -> Top-K -> Solidity Harness
             -> Echidna 多 seed -> 统一日志解析与统计
```

## 代码入口

| 阶段 | 文件 |
|---|---|
| 状态读写 | [`analyzer/extract_rw.py`](../../analyzer/extract_rw.py) |
| 基础路径 | [`analyzer/generate_sequences.py`](../../analyzer/generate_sequences.py) |
| 属性过滤 | [`analyzer/generate_property_sequences.py`](../../analyzer/generate_property_sequences.py) |
| 重复访问 | [`analyzer/generate_repetition_aware_sequences.py`](../../analyzer/generate_repetition_aware_sequences.py) |
| 值约束 | [`analyzer/extract_value_constraints.py`](../../analyzer/extract_value_constraints.py)、[`analyzer/generate_value_guided_sequences.py`](../../analyzer/generate_value_guided_sequences.py) |
| Harness 生成 | [`analyzer/generate_harness_from_paths.py`](../../analyzer/generate_harness_from_paths.py) |
| 日志解析 | [`analyzer/parse_experiment_logs.py`](../../analyzer/parse_experiment_logs.py) |
| 统计汇总 | [`analyzer/summarize_experiment.py`](../../analyzer/summarize_experiment.py) |

## 版本边界

- V1 的正式入口是 `analyzer/` 根目录脚本、`results/formal/`、`results/formal-b2/` 和 `results/public-benchmarks/c1/`。
- [`analyzer/v2/`](../../analyzer/v2/) 只用于 V2 开发和敏感性研究；它的结果不应覆盖或替换 V1 主结果。
- 方法说明、实验口径和已知限制见 [`docs/START_HERE.md`](../../docs/START_HERE.md)。

## 论文写法建议

把贡献写成“属性定向、可审计的候选交易序列 Harness 合成”，不要把单个组件（状态依赖、重复调用、排序）孤立写成首次提出。组件有效性由 Formal 和 B-2 的受控案例支持，公开基准则用于检验适配性和 Top-K 稳定性。
