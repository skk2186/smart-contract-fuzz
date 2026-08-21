# C2公平基线本地可行性审计

> 本审计只检查本机已有命令和项目目录；未联网、未下载、未安装，也未运行漏洞发现实验。

## 结论

- 审计比较项：10；
- 外部SOTA候选：5；
- 当前本地具有命令或代码的外部SOTA：1；
- Original Echidna 与 SMARTIAN 均已有可执行入口，但只有 Original 直接对应本项目属性；
- 已有组件消融可以继续使用，但不替代外部SOTA；
- matched random Top-K必须重新设计，现有早期random数据不能进入主比较。

## 环境

- `echidna`：Echidna 2.3.2
- `solc`：Version: 0.8.20+commit.a1b79de6.Linux.g++
- `dotnet`：8.0.423
- `slither_contract_fuzz`：0.11.5
- `crytic_compile_contract_fuzz`：0.3.11
- `docker`：cli_present_runtime_unavailable

## 比较项

| baseline | kind | command | files | status | oracle alignment |
|---|---|---:|---:|---|---|
| original-echidna | primary_internal | 1 | 0 | ready_with_semantic_caveats | yes |
| dependency-property-ablations | internal_ablation | 0 | 278 | ready_internal_only | yes |
| random-matched-top-k | internal_control | 0 | 10 | requires_new_unconfounded_design | yes |
| smartian | external_sota | 0 | 3367 | requires_compatibility_and_fairness_work | no_direct_alignment |
| medusa | external_engineering | 0 | 0 | not_locally_available | potentially |
| foundry-invariant | external_engineering | 0 | 0 | not_locally_available | potentially |
| confuzzius | external_sota | 0 | 0 | not_locally_available | no_direct_alignment |
| ir-fuzz | external_sota | 0 | 0 | not_locally_available | no_direct_alignment |
| mufuzz | external_sota | 0 | 0 | not_locally_available | no_direct_alignment |
| ityfuzz | external_sota | 0 | 0 | not_locally_available | no_direct_alignment |

## Go/No-Go判断

SMARTIAN 已在本地固定版本并通过 Release 构建和 1 秒入口 smoke，但它原生使用 bug oracle，不直接评估任意 Echidna 布尔属性；因此仍不能把原始漏洞数量与本项目直接比较。正式外部SOTA比较还必须解决属性预言机、发送者、交易模型和预算对齐；其他外部候选仍没有本地命令或代码。

在外部工具可用前，可以合法推进的工作是：冻结公开候选筛选流程、实现无混杂matched random Top-K，并继续使用Original与组件消融。缺少外部SOTA必须保留为论文限制。
