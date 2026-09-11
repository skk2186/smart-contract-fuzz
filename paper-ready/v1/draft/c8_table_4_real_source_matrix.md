# 表 4：真实来源 candidate × method 结果矩阵

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
