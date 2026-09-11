# 最终表格包

表格不合并 controlled evidence 与 adapted real-source evidence 的成功率。真实来源部分为 4 candidates、120 runs、80 usable/descriptive records 和 40 compile_error engineering rows；compile_error 不进入比较结果，budget_exhausted 只作为 right-censored 记录。

## 表 1：受控场景任务概览

建议位置：适合主文或实验设置小节

来源：paper-ready/v1/draft/c8_table_1_controlled_tasks.md


该表描述为特定机制障碍设计的 controlled evidence，不代表真实合约生态中的任务分布。B-2 扩展与 formal-main 行保持分组，不作未经说明的 pooled 结论。

| scenario/task | target property | obstacle type | method component tested | run denominator | evidence role |
|---|---|---|---|---:|---|
| branch-value | BranchValueExample; echidna_value_safe | 分支可达性依赖状态值方向 | 属性相关切片 + 状态值写入方向匹配 | 每个方法 30 次 | controlled evidence；机制组件验证 |
| noisy-four-step | NoisyFourStepExample; echidna_value_safe | 四步序列中混入与属性无关的状态路径 | 属性相关性筛选 + 依赖排序 + Top-K | 每个方法 30 次 | controlled evidence；无关路径抑制 |
| reset-example | ResetExample; echidna_value_safe | 状态重置/覆盖使前置状态容易失效 | 写读依赖 + require 条件匹配 + 状态更新方向 | 每个方法 30 次 | controlled evidence；状态演化机制 |
| repeated-call | RepeatedCallExample; echidna_value_safe | 属性违反需要有界重复调用 | 有界重复 + 属性相关路径保留 | 每个方法 30 次 | controlled evidence；重复调用机制 |
| alternative-path | AlternativePathExample; echidna_value_safe | 多个候选阶段路径均可到达目标，且含阶段条件 | require 条件匹配 + Top-K 候选路径排序 | 每个方法 30 次；B-2 扩展 | controlled evidence；扩展案例，单独报告 |
| multi-property | MultiPropertyExample; echidna_value_a_safe 与 echidna_value_b_safe | 同一序列需要覆盖多个显式属性及共享前缀 | 属性相关性聚合 + 依赖切片 + Top-K | 每个方法 30 次；B-2 扩展 | controlled evidence；多属性扩展，单独报告 |

注：受控场景用于解释属性相关筛选、值方向、条件匹配、有界重复和 Top-K 的机制作用；不能单独证明对未覆盖的真实合约类型具有普遍效果。


## 表 2：主实验结果（受控场景）

建议位置：适合主文结果小节；B-2 行保持单独分组

来源：paper-ready/v1/draft/c8_table_2_main_results.md


该表从 machine-readable 受控摘要逐行重建。12 个配置行均为 Full-v1.0、Original/Full-K1、每行 30 次运行，批次为 formal-main 或独立 B-2 扩展；未发现 smoke、pilot、开发、matched-random quarantine 或 incomplete 标记，故行级分母已自动确认。B-2 因环境快照不完整单独报告，不与 formal-main 无条件合并。

| benchmark/scenario | method | batch | runs | falsified_runs | success_rate | median_calls_successful（等价字段） | notes |
|---|---|---|---:|---:|---:|---|---|
| branch-value | Original | formal-main | 30 | 28 | 0.9333 | — | formal-main；纳入 controlled evidence 主结果；Formal main; Original and Harness share testLimit=100000, timeout=30, workers=1, stopOnFail=true; transaction semantics differ |
| branch-value | Full-K1 | formal-main | 30 | 30 | 1.0 | — | formal-main；纳入 controlled evidence 主结果；Formal main; Original and Harness share testLimit=100000, timeout=30, workers=1, stopOnFail=true; transaction semantics differ |
| noisy-four-step | Original | formal-main | 30 | 26 | 0.8667 | — | formal-main；纳入 controlled evidence 主结果；Formal main; Original and Harness share testLimit=100000, timeout=30, workers=1, stopOnFail=true; transaction semantics differ |
| noisy-four-step | Full-K1 | formal-main | 30 | 30 | 1.0 | — | formal-main；纳入 controlled evidence 主结果；Formal main; Original and Harness share testLimit=100000, timeout=30, workers=1, stopOnFail=true; transaction semantics differ |
| reset-example | Original | formal-main | 30 | 27 | 0.9 | — | formal-main；纳入 controlled evidence 主结果；Formal main; Original and Harness share testLimit=100000, timeout=30, workers=1, stopOnFail=true; transaction semantics differ |
| reset-example | Full-K1 | formal-main | 30 | 30 | 1.0 | — | formal-main；纳入 controlled evidence 主结果；Formal main; Original and Harness share testLimit=100000, timeout=30, workers=1, stopOnFail=true; transaction semantics differ |
| repeated-call | Original | formal-main | 30 | 30 | 1.0 | — | formal-main；纳入 controlled evidence 主结果；Formal main; Original and Harness share testLimit=100000, timeout=30, workers=1, stopOnFail=true; transaction semantics differ |
| repeated-call | Full-K1 | formal-main | 30 | 30 | 1.0 | — | formal-main；纳入 controlled evidence 主结果；Formal main; Original and Harness share testLimit=100000, timeout=30, workers=1, stopOnFail=true; transaction semantics differ |
| alternative-path | Original | B-2 | 30 | 30 | 1.0 | — | B-2 扩展；独立环境快照缺失，单独报告；Formal B-2; independent environment snapshot missing; Original seqLen=3 and Harness seqLen=1 |
| alternative-path | Full-K1 | B-2 | 30 | 30 | 1.0 | — | B-2 扩展；独立环境快照缺失，单独报告；Formal B-2; independent environment snapshot missing; Original seqLen=3 and Harness seqLen=1 |
| multi-property | Original | B-2 | 30 | 30 | 1.0 | — | B-2 扩展；独立环境快照缺失，单独报告；Formal B-2; independent environment snapshot missing; stopOnFail=false for both methods to observe both properties |
| multi-property | Full-K1 | B-2 | 30 | 30 | 1.0 | — | B-2 扩展；独立环境快照缺失，单独报告；Formal B-2; independent environment snapshot missing; stopOnFail=false for both methods to observe both properties |

注：源摘要未提供 seed-level calls-to-failure，该列记为“—”，不臆造数值。success_rate 采用源摘要预定义的 success_definition。该表是 controlled evidence，不与 adapted real-source evidence 合并成一个总成功率。


## 表 3：真实来源 adapted candidates 概览

建议位置：适合主文补充小节或附录

来源：paper-ready/v1/draft/c8_table_3_real_source_overview.md


该表概览 adapted real-source evidence 的记录分层。usable/descriptive rows 包含可比较 Echidna-origin、SmartBugs Original-only 描述性记录和 1 条 right-censored 记录；SmartBugs Harness 的 40 条 compile_error 全部列为 excluded engineering rows，不进入比较结果。

| candidate group | total rows | usable/descriptive rows | excluded engineering rows | falsified | budget_exhausted | compile_error | interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| Echidna-origin / flags | 30 | 30 | 0 | 30 | 0 | 0 | Echidna-origin；三种方法均有可解析结果，构成 comparable subset |
| Echidna-origin / multi | 30 | 30 | 0 | 29 | 1 | 0 | Echidna-origin；三种方法均有可解析结果，构成 comparable subset |
| SmartBugs / multifunc | 30 | 10 | 20 | 10 | 0 | 20 | SmartBugs adapted；Original 可描述，Harness compile_error 不参与比较 |
| SmartBugs / onefunc | 30 | 10 | 20 | 10 | 0 | 20 | SmartBugs adapted；Original 可描述，Harness compile_error 不参与比较 |
| 总计 | 120 | 80 | 40 | 79 | 1 | 40 | adapted real-source evidence；不构成大规模真实合约评估 |

注：budget_exhausted 是 right-censored，不表示安全或通过。40 条 SmartBugs Harness compile_error 被排除出 comparative outcomes。


## 表 4：真实来源 candidate × method 结果矩阵

建议位置：适合附录；主文可仅呈现 comparable subset 摘要

来源：paper-ready/v1/draft/c8_table_4_real_source_matrix.md


仅两个 Echidna-origin candidates 的六个 cells 进入 full comparable subset。SmartBugs Original-only 只用于说明 adapted targets 可运行并观测到属性违反；40 条 Harness compile_error 只作为 engineering limitation。Original and Harness are distinct execution models。

| candidate | method | subset role | rows | status summary | falsified | budget_exhausted | compile_error | paper_usable | median calls_to_failure | mean calls_to_failure | median sequence_length | mean sequence_length | median fuzz_seconds | median wall_seconds |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| b5-rs-echidna-flags | Original | comparable_echidna_origin | 10 | falsified=10 | 10 | 0 | 0 | 10 | 5 | 4.9 | 5 | 4.9 | 2.48 | 2.522 |
| b5-rs-echidna-flags | Full-K1 | comparable_echidna_origin | 10 | falsified=10 | 10 | 0 | 0 | 10 | 1 | 1 | 1 | 1 | 2.495 | 2.522 |
| b5-rs-echidna-flags | Full-K5 | comparable_echidna_origin | 10 | falsified=10 | 10 | 0 | 0 | 10 | 1 | 1 | 1 | 1 | 2.44 | 2.472 |
| b5-rs-echidna-multi | Original | comparable_echidna_origin | 10 | falsified=10 | 10 | 0 | 0 | 10 | 6 | 5.8 | 6 | 5.8 | 2.75 | 2.773 |
| b5-rs-echidna-multi | Full-K1 | comparable_echidna_origin | 10 | falsified=10 | 10 | 0 | 0 | 10 | 1 | 1 | 1 | 1 | 6.135 | 6.16 |
| b5-rs-echidna-multi | Full-K5 | comparable_echidna_origin | 10 | falsified=9;budget_exhausted=1 | 9 | 1 | 0 | 10 | 1 | 1 | 1 | 1 | 6.59 | 6.636 |
| b5-rs-smartbugs-multifunc | Original | smartbugs_original_only | 10 | falsified=10 | 10 | 0 | 0 | 10 | 3 | 3.4 | 3 | 3.4 | 1.42 | 1.469 |
| b5-rs-smartbugs-multifunc | Full-K1 | excluded_engineering | 10 | compile_error=10 | 0 | 0 | 10 | 0 | n.a. | n.a. | n.a. | n.a. | n.a. | n.a. |
| b5-rs-smartbugs-multifunc | Full-K5 | excluded_engineering | 10 | compile_error=10 | 0 | 0 | 10 | 0 | n.a. | n.a. | n.a. | n.a. | n.a. | n.a. |
| b5-rs-smartbugs-onefunc | Original | smartbugs_original_only | 10 | falsified=10 | 10 | 0 | 0 | 10 | 2 | 2.3 | 2 | 2.3 | 1.495 | 1.519 |
| b5-rs-smartbugs-onefunc | Full-K1 | excluded_engineering | 10 | compile_error=10 | 0 | 0 | 10 | 0 | n.a. | n.a. | n.a. | n.a. | n.a. | n.a. |
| b5-rs-smartbugs-onefunc | Full-K5 | excluded_engineering | 10 | compile_error=10 | 0 | 0 | 10 | 0 | n.a. | n.a. | n.a. | n.a. | n.a. | n.a. |

注：calls-to-failure、sequence-length、fuzz seconds 和 wall seconds 只对 falsified rows 作描述性统计。不得把不同执行模型的 Total calls 直接写成 speedup。


## 表 5：有效性威胁与缓解措施

建议位置：适合主文 threats to validity 小节

来源：paper-ready/v1/draft/c8_table_5_threats.md


| threat | affected claim | mitigation | remaining limitation |
|---|---|---|---|
| controlled benchmarks 外部有效性有限 | 受控结果是否代表一般真实合约 | 固定障碍、属性和分母，定位为 controlled evidence | 场景小且由研究者设计，不能估计生态分布 |
| 真实来源 candidate 数量有限 | adapted real-source evidence 的广泛性 | 报告 4 candidates、120 runs 与 80/40 分层 | 不能推断整个真实合约生态 |
| adapted source 与原始合约存在工程适配 | 真实来源结果的外部有效性 | 记录编译器、属性接口和适配边界 | 适配可能改变入口、初始化或可观察接口 |
| 人工属性接口/标注 | 属性是否表达原任务意图 | 保留属性名、provenance 和可审计记录 | 可能遗漏原始意图或引入表达偏差 |
| Solidity 0.4.25 Harness import-path compile_error | Harness 比较结果是否可解释 | 40 条记录列为 excluded engineering rows | 尚无完善的跨版本 Harness 迁移路径 |
| budget_exhausted 右删失 | 未发现反例如何解释 | 明确写为 right-censored | 不能据此推断安全，需要删失分析 |
| Original/Harness execution-model difference | 两种执行模式能否直接比较 | 只做窄范围、同 candidate/property/预算描述 | caller、回滚、交易边界可能仍不同 |
| 版本与复杂类型覆盖不足 | 对其他 Solidity 版本和复杂参数的适用性 | 报告当前边界并列为未来工作 | 未覆盖全部版本、复杂结构和调用者模型 |


## 统一表注

controlled evidence 用于机制解释，adapted real-source evidence 用于适用边界检查。SmartBugs Harness 的 40 条 compile_error 属于 excluded engineering rows，不是比较结果。唯一的 budget_exhausted 记录是 right-censored，不表示安全或通过。calls-to-failure、sequence-length、fuzz seconds 和 wall seconds 仅用于 falsified rows 的描述性统计；不同执行模型的 Total calls 不直接构成 speedup。Original and Harness are distinct execution models。
