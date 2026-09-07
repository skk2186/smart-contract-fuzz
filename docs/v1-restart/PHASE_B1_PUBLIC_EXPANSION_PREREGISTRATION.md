# 大阶段 B1：Public Benchmark Expansion Preregistration

## 1. 目的与范围

本阶段目标是为后续 B2 建立不依赖结果选择的 public benchmark 扩充登记，并把候选来源、属性、语义风险、排除原因和下一步动作固定下来。

本次扫描只使用当前仓库已有的源码和登记材料，不联网下载新数据集、不临时复制未知外部合约、不创建 toy 合约、不运行 Echidna/Slither/solc，不修改 `results/` 或历史 quarantine 结果。

这不是 public benchmark 的正式效果实验。候选表中的 `classification` 是预登记筛选判断，不是 fuzzing 结果；任何候选都不能直接进入论文主表。

## 2. 候选来源和扫描范围

已只读扫描：

- `contracts/public-benchmarks/raw/`；
- `contracts/public-benchmarks/adapted/`；
- `contracts/benchmarks/`；
- `configs/`；
- `docs/v1-restart/`、`paper-ready/` 和 `results/` 的登记/审计入口。

扫描确认：当前 public/adapted 范围只有既有 5 个任务；`contracts/benchmarks/` 中可再登记的源文件是内部 Formal/B-2/早期 pilot 设计，不能冒充 public benchmark。为保留完整审计轨迹，本阶段登记其中 3 个最接近序列任务的文件，并明确排除。

## 3. 纳入标准

候选只有在后续人工复核仍满足以下条件时，才可能进入 B2 replay/main-run preparation：

1. Solidity source、路径和来源/许可证可以固定；
2. 有原作者 property，或能依据公开来源按统一规则定义可信 property；
3. 核心目标需要至少两步状态操作，而不是单函数立即失败；
4. 不严重依赖 `msg.sender` alternation、`msg.value`/payable、区块时间、external call/reentrancy 或当前 wrapper 无法保持的语义；
5. 适配不会改变目标状态转移，或适配差异可以逐项记录；
6. 能给出 known path/target goal、参数约束、失败分类和 replay 输出；
7. 在看到 V1 正式结果之前冻结 benchmark、property、K、预算和排除规则。

## 4. 排除标准

以下情况不得进入 supported public pooled table：

- 仅有本仓库自造或专门设计的 formal toy，没有独立 public origin；
- 只是已有 benchmark 的重命名、声明顺序或 Harness 变体；
- 无法定义可信属性、无法恢复依赖或无法固定编译环境；
- 依赖 caller alternation、payable/value、时间、external/reentrancy 或交易回滚语义而没有预登记的可比执行模型；
- 需要根据 V1 成败来决定是否纳入；
- 来自 `results/matched-random-v1/`、V2、C0、smoke 或其他 quarantine 材料。

编译失败、静态审计失败、Harness 生成失败和启动失败都必须在筛选记录中保留，不能无痕删除或从分母中排除。

## 5. 已有 5 个任务的状态

| benchmark | current status | B1 decision | reason |
|---|---|---|---|
| `echidna-flags` | supported / Phase 06A `pilot_only` | 保留，先 native replay | 已有适配源码和 property；固定路径需要检查参数约束与 wrapper atomicity |
| `echidna-multi` | supported / Phase 06A `pilot_only` | 保留，先 native replay | 已有三步状态链；需要记录精确参数和逐步成功 |
| `smartbugs-multifunc` | supported / Phase 06A `pilot_only` | 保留，先 native replay | 已有 0.4.x 适配和 property；需要固定 unchecked arithmetic 语义 |
| `smartbugs-onefunc` | supported / Phase 06A `pilot_only` | 保留，先 native replay | 已有适配和 property；主要验证 runner/public integration 与固定重复访问 |
| `exercise2-access-control` | conditional | 继续 conditional，caller-controlled replay | `msg.sender`、address-keyed mapping 和 caller alternation 使 Harness 与 Original 不能直接 pooled |

四个 supported 任务在 registry 中标为 `needs_replay`，不是正式 main-table `yes`；exercise2 在 replay 前后都不进入 supported pooled。

## 6. 新候选逐项审计

本阶段发现并登记 3 个候选条目，均来自仓库内 `contracts/benchmarks/`。它们具备可读 source 和 Echidna property，但都明确属于本项目内部 formal/扩展设计，没有独立 public origin。因此“候选记录数”为 3，“建议进入 B2 的新增 public candidate 数”为 0。

| candidate_id | benchmark_name | source_path | property_or_expected_property | source_type | public_origin_or_reason | static_support_status | caller_sensitive | address_mapping_sensitive | payable_or_value_sensitive | time_or_block_sensitive | external_or_reentrancy_sensitive | revert_or_atomicity_sensitive | classification | reason | b2_action |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `PUB06` | `alternative-path-internal` | `contracts/benchmarks/AlternativePathExample.sol` | `echidna_value_safe`; `openRouteA/B -> confirm -> execute(x)` | internal_formal_toy | 无独立 public origin；仓库已有 Formal-B2 AlternativePath | source/property 可静态读取；不是 public provenance | no | no | no（仅普通函数参数 `x`） | no | no | yes（stage require；wrapper rollback 需单独记录） | excluded_candidate | 专门设计的多路径 Formal toy，不能作为 public expansion 或真实生态外部有效性证据 | exclude |
| `PUB07` | `multi-property-internal` | `contracts/benchmarks/MultiPropertyExample.sol` | `echidna_value_a_safe` 与 `echidna_value_b_safe`; `prepare -> authorize -> execute(x,y)` | internal_formal_toy | 无独立 public origin；仓库已有 Formal-B2 MultiProperty | source/property 可静态读取；不是 public provenance | no | no | no（仅普通函数参数 `x,y`） | no | no | yes（stage require；同一序列影响两个 property） | excluded_candidate | 专门设计的多属性 Formal toy，不能与 public benchmark 混称或 pooled | exclude |
| `PUB08` | `three-step-internal` | `contracts/benchmarks/ThreeStepExample.sol` | `echidna_value_safe`; `register -> deposit -> withdraw(x)` | internal_formal_toy | 无独立 public origin；仓库已有早期 ThreeStep/pilot 材料 | source/property 可静态读取；不是 public provenance | no | no | no（仅普通函数参数 `x`） | no | no | yes（stage require；早期受控示例） | excluded_candidate | 内部早期受控 toy，重复已有机制证据，违反 public expansion 的非自造来源要求 | exclude |

`BranchValueExample*` 的重命名、声明顺序和测试变体没有另列为候选，因为它们是同一 Formal toy 的内部消融/稳健性材料；matched-random Harness 也没有被当作候选。

## 7. B2 建议集合和动作

建议进入 B2 native replay/main-run preparation 的集合只有已有 4 个 supported 任务，但必须先完成逐任务 replay、人工复核和独立 manifest。它们不是本阶段授权的 10-seed main run。

建议单独进行 caller-controlled replay 的任务是 `exercise2-access-control`；它继续作为 conditional appendix/条件分层案例，不得进入 supported pooled main table。

本阶段新增候选 `PUB06`–`PUB08` 全部 `exclude`。在当前仓库素材范围内，没有可以诚实标记为 `supported_candidate` 或 `conditional_candidate` 的新增 public source；不应为了达到数量目标而把 Formal toy、matched-random 或 quarantine 材料改名纳入。

## 8. 对外部有效性的帮助

本登记的直接贡献是暴露数据集边界：当前仓库仍只有 5 个 public task，且新增扫描没有产生可纳入的独立 public source。这能防止把内部 Formal/B-2 机制案例误写成外部泛化证据，并为后续真正收集外部来源时固定纳入/排除规则。

它不能增加 public benchmark 数量，不能证明 V1 对真实合约总体有效，也不能替代未来按相同规则获得并冻结的外部 source、属性来源、许可证、适配补丁和失败记录。

## 9. 风险与限制

- 本阶段没有联网下载，因此没有声称扫描 SmartBugs、DAppSCAN 或其他外部数据集的新增条目；
- 内部候选即使静态上可生成 property，也不具备 public provenance，必须排除；
- `exercise2-access-control` 的 caller 语义仍是条件支持，不得 pooled；
- Native replay 只检验预先固定序列，不能证明随机搜索过程等价；
- `budget_exhausted` 仍不是 property passed；
- `results/matched-random-v1/`、V2、C0、Phase 06A pilot 和 frozen results 未被重新纳入或修改；
- B2 10-seed 仍需要研究者在 replay、manifest 和工作区复核后单独决定。
