# Threats to Validity 草稿

## Internal validity

首先，公开结果的支持范围被固定为四个 supported public tasks、三种方法和 seed 1–10。该范围包含四个任务 × 三种方法 × 十个 seed，共 120 个运行；没有根据观察结果删除失败运行，也没有把 conditional 或 excluded 项目补入分母。所有 120 个运行均有完整 artifact set，checksum 通过，parser/status mismatch 为 0，因而降低了由缺失文件、状态错配或事后筛选造成的内部威胁。

仍然存在配置层面的限制。Original 使用多交易配置，Harness 使用单外层 wrapper 配置；seqLen、调用层次和目标函数执行方式并不相同。两个 SmartBugs 任务使用 Solidity 0.4.x unchecked arithmetic，另两个任务使用 solc 0.8.20，编译器差异属于任务语义和 provenance 的一部分。结果只能在各自预登记配置下比较，不能视为相同底层工作量。

2 个 budget_exhausted 运行必须单独保留。它们表示在声明预算内没有观察到反例，不表示 property passed、contract safe 或不存在漏洞。将其当作成功或安全会直接造成结果分类威胁。

## External validity

外部效度最主要的限制是 public benchmark 数量只有 4 个 supported。四个任务规模小、属性数量有限，其中两个为经过本地 property 适配的 SmartBugs 算术任务；它们不能代表真实合约生态，也不能支撑大型合约上的普遍结论。smartbugs-onefunc 主要验证重复单函数的 public integration，不应包装成一般多交易排序优势。

exercise2-access-control 不属于 supported pooled 结果。它依赖 msg.sender、owner equality、caller alternation 和 address-keyed mapping；在完成 caller-controlled same-caller 与 alternating-caller replay 前，只能作为 conditional appendix。PUB06–PUB08 是内部候选，不是新增 public benchmark。

因此，本评价只支持在已登记的四个任务和当前配置内报告描述性观察。若要扩大外部效度，优先补充 2–4 个不同来源、不同语义依赖和更大规模的 public benchmark，而不是只增加同一任务的 seed。

## Construct validity

falsified 表示在给定执行模型、输入和预算内观察到属性反例；budget_exhausted 表示在预算内未观察到反例。二者都不是合约安全判定。observed falsification rate 是 falsified / runs 的描述性比率，不是漏洞发现概率的无偏估计，也不是属性通过率。

artifact completeness、checksum pass 和 parser/status agreement 衡量的是证据链完整性，不是语义正确性或安全性。B2 是 static gate，不是完整 native EVM replay；static_gate_pass 只能支持源码、配置、已知路径和风险特征的静态可追溯性，不能被写成 replay_pass。

不能使用 Total calls 作为 speedup 构造。Original 的计数主要位于独立目标交易/调用层次，Harness 的多个目标调用被折叠在一次 wrapper 外层调用中；二者并非等量工作指标。候选路径数量减少也不能自动推出端到端 fuzzing 加速。

## Semantic validity

Harness wrapper 语义与 Original 多交易语义存在差异。wrapper 内目标调用通常由同一个 Harness 地址发起，而 Original 可能在交易之间切换 sender；Original 的每笔交易有独立边界，而 wrapper 可能把多个调用合并在一次交易中；某一步 revert 时，Original 和 wrapper 的回滚范围也可能不同。msg.value/payable、block.timestamp、block.number、external call、reentrancy、constructor/deployer 和 address-keyed state 均需要单独确认。

固定成功路径的最终属性相关状态一致，只能支持窄条件下的重放一致性，不能证明完整随机搜索过程、失败前缀、调用者搜索或回滚行为等价。特别是 exercise2-access-control 的 caller 和 mapping 依赖，使其不能进入 supported pooled 结果。

## Reproducibility

公开主运行使用预登记的 benchmark、method、seed、配置、编译器、预算、timeout、workers 和 stopOnFail。每个运行保留 manifest、command、environment、raw、parsed、summary、status 和 checksum；120/120 artifact sets 完整，120/120 checksum 通过。run-level 明细应作为附录或复现材料提供，正文只呈现分组摘要。

复现时应同时保留源文件和配置的版本、方法版本 Full-v1.0.1-compat、Echidna 2.3.2、Slither 0.11.5、Python 3.11.15、对应 solc 版本及执行模型说明。任何未来重跑都必须使用独立 run 目录，不能覆盖冻结 evidence，也不能把新的运行结果默认为当前旧结果的同一版本。

matched-random-v1 的 provenance unresolved，仍保持 PROVENANCE_UNRESOLVED、DO_NOT_USE_FOR_NEW_CLAIMS 和 LEGACY_CONTROL_QUARANTINED 标记。因此它不用于新主张，也不与当前四任务结果 pooled。

## Baseline comparison limitations

本评价没有进行 SMARTIAN、MuFuzz 或 IR-Fuzz 的工具级实验比较，也没有足够一致的执行模型、任务覆盖、预算和 oracle 来支持工具排名。现有 SMARTIAN 材料只覆盖两个简单整数目标，不能改写成广泛竞品优势证据。

同样，不能声称 V1 普遍优于 Echidna。V1 的定位是 Echidna 之上的 property-directed Harness synthesis preprocessing；Original 是当前公开任务中的执行对照，而不是一个与 Harness 具有完全相同交易语义的等量基线。当前结果只支持窄定位 claim：机制在受控障碍上可观察、四个 supported public tasks 上的运行链完整，并可对三种方法作范围内描述性比较。

## Overall implication

这些威胁并不阻塞论文初稿，但限制了投稿主张的宽度。可以进入窄定位的 Evaluation 草稿和结果表；如果目标是更广泛的 CCF-C 方法结论，则仍需更多 public benchmark、caller-controlled conditional replay、规模证据和可比的外部基线。
