# 9 Conclusion（中文草稿）

本文研究了一种面向属性模糊测试的智能合约 transaction sequence Harness synthesis 方法。方法位于 Echidna 之前，从显式 safety property 读取的状态变量出发，反向过滤相关写入，构造候选 transaction sequence，加入有界重复和轻量值约束证据，并以可解释的 Top-K 规则生成 Solidity wrapper Harness。候选顺序由前处理固定，参数与属性探索仍由 Echidna 完成，因此该方法是外部 preprocessing，而不是新的 fuzzer 或 Echidna-core 替代品。

受控 Formal benchmarks 对无关路径、值方向、重复访问和 reset/Top-K 障碍提供了范围内机制证据。四个预登记 supported public tasks 上的三方法、seed 1–10 比较包含 120 个运行，其中 118 个为 falsified、2 个为 budget_exhausted；120/120 个 artifact set 完整，120/120 checksum pass，parser/status mismatch、startup_error、unknown_error 和 incomplete 均为 0。这里的 budget_exhausted 只表示在声明预算内没有观察到反例，不表示属性通过或合约安全。

这些结果不能支持显著优越性、Total calls speedup、Harness/Original 完全等价或真实生态泛化。Original multi-transaction model 与 wrapper execution model 在 caller、transaction atomicity、rollback scope、value、区块环境和 external-call 语义上可能不同；exercise2-access-control 因 caller 与 address-keyed mapping 依赖继续保持 conditional，matched-random-v1 继续 quarantine。当前证据应被理解为窄定位的机制和可审计性证据。

后续工作包括补充更多不同来源和规模的 public benchmark，完成 caller-controlled replay，建立任务、预算和 oracle 更公平的外部 baseline，细化 Harness 与 Original 的语义对齐，并把候选分析与生成成本扩展到更大规模真实合约。上述扩展都应使用独立 provenance 和预登记，不覆盖当前 V1 证据。
