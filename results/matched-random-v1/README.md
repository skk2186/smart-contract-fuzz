# Matched Random Top-K内部基线

## 目的

该基线回答：当候选池和Harness数量相同，只把V1的确定性Top-1替换为均衡随机选择时，反例发现表现会怎样。

它使用V1 Full阶段已经保留的同一候选池，因此隔离的是**候选池内部排序和Top-1选择**，不是Property或Repeat的候选保留作用。

## 防混杂设计

- 先于运行冻结完整调度表；
- 调度种子固定为`20260805`；
- 使用SHA-256键排序，不依赖Python `random`实现；
- 30个Echidna fuzz seed为1–30；
- 路径选择由调度表决定，不在运行时使用fuzz seed抽样；
- 采用随机化的循环平衡设计，每个候选入选次数的最大差值不超过1；
- path count为1的目标与Full-K1完全相同，不重复运行。

## 当前状态

调度设计和预注册已完成。生成器按候选选择去重：多个fuzz seed选择同一路径时复用同一Harness。共生成66个去重Harness并全部通过编译预检；冻结的270行正式运行已经完成，结果为87/270次falsified、183/270次budget_exhausted，无startup/incomplete。正式运行严格使用`execution-manifest.tsv`，没有因结果重新抽样。

逐seed配对结果见[`analysis.md`](analysis.md)和[`summary-by-benchmark.csv`](summary-by-benchmark.csv)。该批次只作为候选池内部控制：同一benchmark、同一fuzz seed下，将Full-K1的确定性Top-1替换为均衡随机Top-1；不能替代外部SOTA比较，也不应与V2原生种子消融合并。

## 重建命令

```bash
python3 analyzer/build_matched_random_schedule.py \
  --manifest results/matched-random-v1/cases.tsv \
  --runs 30 \
  --top-k 1 \
  --schedule-seed 20260805 \
  --output-schedule results/matched-random-v1/matched-random-schedule.csv \
  --output-cases results/matched-random-v1/case-summary.csv \
  --report results/matched-random-v1/preregistration-report.md
```

本步骤只读取现有候选JSON并生成派生调度，不联网、不编译、不运行模糊测试。

Harness生成与纯编译预检：

```bash
python3 analyzer/generate_matched_random_harnesses.py \
  --cases results/matched-random-v1/cases.tsv \
  --schedule results/matched-random-v1/matched-random-schedule.csv \
  --output-root contracts/harnesses/matched-random-v1 \
  --harness-manifest results/matched-random-v1/harness-manifest.csv \
  --execution-manifest results/matched-random-v1/execution-manifest.tsv

python3 analyzer/preflight_matched_random_harnesses.py \
  --manifest results/matched-random-v1/harness-manifest.csv \
  --log-root results/matched-random-v1/preflight/logs \
  --output-csv results/matched-random-v1/preflight/compile-preflight.csv \
  --report results/matched-random-v1/preflight/report.md
```

预检只调用固定的本地Solidity编译器，不运行Echidna。

完整重建入口：

```bash
scripts/rebuild_matched_random_v1_preflight.sh
```

结果解析（不重新运行Echidna）：

```bash
python3 analyzer/analyze_matched_random_v1.py \
  --manifest results/matched-random-v1/execution-manifest.tsv \
  --output-summary results/matched-random-v1/summary-by-benchmark.csv \
  --output-paired results/matched-random-v1/paired-runs.csv \
  --report results/matched-random-v1/analysis.md
```
