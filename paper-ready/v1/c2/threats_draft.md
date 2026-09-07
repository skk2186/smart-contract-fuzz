# 7 Threats to Validity（中文草稿）

## 7.1 Internal validity

内部效度首先受到配置和执行模型不对称的影响。Original 使用 Echidna 的 Original multi-transaction model；Full-K1 和 Full-K5 使用外部 wrapper Harness。Original 的 seqLen=4 与 Harness 的 seqLen=1 位于不同调用层次，不能看作相同长度或相同工作量。两个 SmartBugs 任务使用 Solidity 0.4.x 的 unchecked arithmetic，另两个公开任务使用 solc 0.8.20；这些编译器和语言语义差异属于任务配置的一部分。因此，结果只能在各自预登记配置下作任务级描述性解释。

公开主批次固定为四个 supported public tasks、三种方法和 seed 1–10，共 120 runs。没有依据结果删除失败运行，也没有把 conditional 或 excluded 项补入分母。120/120 个运行保留完整 artifact set，120/120 checksum pass，parser/status mismatch 为 0，startup_error、unknown_error 和 incomplete 均为 0，这些审计降低了缺失产物、事后删行和解析错配造成的内部威胁，但不能消除配置不对称。

两个 budget_exhausted 运行必须单独保留。它们表示在声明预算内没有观察到反例，不表示 property passed、contract safe 或漏洞不存在。若将其当作成功、通过或安全，会直接改变状态构念并造成内部效度威胁。

## 7.2 External validity

public benchmark 只有 4 个 supported，样本数量和合约规模都有限，不能代表真实合约生态。任务来源、属性形态、调用者关系和状态依赖类型并不覆盖资金、时间、外部调用、重入或复杂权限逻辑。smartbugs-onefunc 主要提供重复单函数的集成证据，不能被包装成一般多交易排序证据。四个任务的 120 runs 是 seed 层面的重复观察，不是 120 个独立合约。

exercise2-access-control 因 msg.sender、owner equality、caller alternation 和 address-keyed mapping 依赖保持 conditional，不能进入 supported pooled 结果。它需要 caller-controlled native replay，至少分别检查 same-caller 和 alternating-caller schedule。alternative-path-internal、multi-property-internal 和 three-step-internal 是内部或受控材料，不是额外 public benchmark。若要扩大外部效度，应优先增加不同来源、不同调用者/状态映射和更大规模的 public benchmark，而不是只增加同一任务的 seed。

## 7.3 Construct validity

falsified 表示在给定执行模型、输入和预算内观察到属性反例；budget_exhausted 表示在预算内没有观察到反例。observed falsification rate 是 falsified/runs 的描述性比率，不是属性通过率、安全概率或无偏的漏洞发现概率。artifact completeness、checksum pass 和 parser/status agreement 衡量证据链完整性，不是语义正确性和安全性证明。

候选路径数量减少也不能自动说明端到端 fuzzing 变快，因为静态分析、Harness 生成、编译、wrapper 调用和参数搜索的成本可能不同。Original 与 Harness 的 Total calls 处在不同外层计数层次，本研究不使用它构造 speedup，也不将其作为等量工作指标。B2 是 static gate，不是完整 native EVM replay；static_gate_pass 只能说明静态审计条件满足，不能替代动态语义复核。

## 7.4 Semantic validity

Harness wrapper 与 Original multi-transaction model 在 caller、transaction atomicity 和 rollback scope 上存在结构性差异。Original 的不同外层交易可能由不同 sender 发起，某笔失败通常只回滚该笔交易；wrapper 内的目标函数通常由同一个 Harness 地址调用，多个函数调用可能合并在一次外层交易中，一步 revert 可能影响整个 wrapper。msg.value、payable behavior、block.timestamp、block.number、external calls、reentrancy、constructor/deployer 和 address-keyed state 也不能默认对齐。

固定成功路径上最终属性相关状态一致，只能作为窄条件下的 replay consistency 观察，不能证明完整随机搜索过程、sender 搜索、失败前缀或回滚行为等价。因而，Harness 的 falsified 必须解释为 wrapper 模型下的反例观察，不能自动改写为 Original 语义下的同一结果。

## 7.5 Reproducibility

复现链记录了 benchmark、property、method、seed、配置、编译器、testLimit、timeout、workers、stopOnFail、实际命令、工具版本和 commit SHA。每个运行保存 manifest、command、environment、raw、parsed、summary、status 与 checksum；120/120 完整，120/120 checksum pass。未来重跑应使用独立 run 目录，不能覆盖冻结 evidence，也不能用新方法版本重新解释旧日志。

matched-random-v1 的 provenance unresolved，保持 quarantine，不用于新主张或 pooled 统计。V2、C0、smoke、历史 pilot 及无法证明完整执行的材料同样不能被悄然升级为主结果。可复现的文件链能让读者回到原始产物，但不能改变数据规模和语义适用范围。

## 7.6 Baseline comparison limitations

本文没有完整、可比的 SMARTIAN、MuFuzz 或 IR-Fuzz 工具级实验。现有 SMARTIAN 材料只覆盖两个简单整数目标，不能支持广泛竞品排名；也不能据此写 V1 普遍优于这些工具。本文的 Original 是公开任务中的执行对照，而不是与 Harness 具有完全相同交易语义的等量基线。Echidna 是本文依托的既有属性模糊器，V1 是其上的前处理和外部 Harness synthesis，而不是替代品。

## 7.7 Implication

上述威胁不阻塞窄定位的论文初稿，但决定了结论必须停留在机制证据、运行链可审计性和四个 supported public tasks 的描述性观察。若要提出更宽的生态、加速、等价或工具排名结论，仍需更多 public benchmark、caller-controlled replay、更公平的外部 baseline、规模记录和更精细的 Harness/Original 语义对齐。
