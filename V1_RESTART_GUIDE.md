# V1 重启实验包

本目录是从 Git 标签 `experiment-freeze-20260806` 整理出的 V1 实验快照，供重新开展实验使用。原始工作区仍保留在同级的 `smart-contract-fuzzing/`，本目录不依赖其未提交改动。

## 推荐入口

1. 阅读 `docs/START_HERE.md`，了解方法、实验口径和语义限制。
2. 阅读 `docs/EXPERIMENTS.md`，确认每个实验的目的、分母和可支持结论。
3. 从 `analyzer/`、`configs/` 和 `scripts/prepare_formal_full.sh` 开始重建 Formal 主实验。
4. 使用 `results/formal/`、`results/formal-b2/`、`results/public-benchmarks/c1/` 和 `results/paper-data/` 对照冻结证据。

## 保留内容

- V1 核心流程：状态读写提取、属性路径筛选、有界重复、值约束匹配、Top-K 和 Harness 生成。
- 六个合成基准及其 Formal/B-2 结果。
- 五个 C-1 公开基准及适配、路径预检、统计和原始日志。
- matched-random 候选池控制实验和 Harness 语义审计。
- 论文数据入口、方法文档和可重建脚本。

## 明确排除

V2/native-corpus 开发线、8 月 17–20 日 C2/公共候选扩展、research-cycles、大型 checkpoint、smoke/启动记录以及被后续 Formal 批次替代的旧结果没有复制进来。

## 重要解释

`budget_exhausted` 不是“属性通过”；Original 的多交易执行与 Harness 的单交易 wrapper 也不能直接视为完全等价。V1 最有价值的证据是受控障碍上的机制分解、候选空间压缩和可审计的路径选择，而不是对所有真实合约或外部工具的普遍优越性声明。
