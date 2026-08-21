# C2公平基线本地可行性审计

> 本审计只检查本机已有命令和项目目录；未联网、未下载、未安装，也未运行漏洞发现实验。

## 结论

- 审计比较项：10；
- 外部SOTA候选：5；
- 当前本地具有命令或代码的外部SOTA：0；
- 当前可以直接执行的主基线只有Original Echidna；
- 已有组件消融可以继续使用，但不替代外部SOTA；
- matched random Top-K必须重新设计，现有早期random数据不能进入主比较。

## 环境

- `echidna`：Echidna 2.3.2
- `solc`：Version: 0.8.20+commit.a1b79de6.Linux.g++
- `slither_contract_fuzz`：0.11.5
- `crytic_compile_contract_fuzz`：0.3.11
- `docker`：cli_present_runtime_unavailable

## 比较项

| baseline | kind | command | files | status | oracle alignment |
|---|---|---:|---:|---|---|
| original-echidna | primary_internal | 1 | 0 | ready_with_semantic_caveats | yes |
| dependency-property-ablations | internal_ablation | 0 | 132 | ready_internal_only | yes |
| random-matched-top-k | internal_control | 0 | 10 | requires_new_unconfounded_design | yes |
| smartian | external_sota | 0 | 0 | not_locally_available | no_direct_alignment |
| medusa | external_engineering | 0 | 0 | not_locally_available | potentially |
| foundry-invariant | external_engineering | 0 | 0 | not_locally_available | potentially |
| confuzzius | external_sota | 0 | 0 | not_locally_available | no_direct_alignment |
| ir-fuzz | external_sota | 0 | 0 | not_locally_available | no_direct_alignment |
| mufuzz | external_sota | 0 | 0 | not_locally_available | no_direct_alignment |
| ityfuzz | external_sota | 0 | 0 | not_locally_available | no_direct_alignment |

## Go/No-Go判断

当前不能进行外部SOTA正式比较，因为本地没有SMARTIAN、ConFuzzius、IR-Fuzz、MuFuzz或ItyFuzz代码/命令，SMARTIAN、Medusa和Foundry占位目录均为空。即使后续取得工具，也必须先解决属性预言机、发送者、交易模型和预算对齐，不能直接比较原始漏洞数量。

在外部工具可用前，可以合法推进的工作是：冻结公开候选筛选流程、实现无混杂matched random Top-K，并继续使用Original与组件消融。缺少外部SOTA必须保留为论文限制。
