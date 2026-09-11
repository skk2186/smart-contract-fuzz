# 表 3：真实来源 adapted candidates 概览

该表概览 adapted real-source evidence 的记录分层。usable/descriptive rows 包含可比较 Echidna-origin、SmartBugs Original-only 描述性记录和 1 条 right-censored 记录；SmartBugs Harness 的 40 条 compile_error 全部列为 excluded engineering rows，不进入比较结果。

| candidate group | total rows | usable/descriptive rows | excluded engineering rows | falsified | budget_exhausted | compile_error | interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| Echidna-origin / flags | 30 | 30 | 0 | 30 | 0 | 0 | Echidna-origin；三种方法均有可解析结果，构成 comparable subset |
| Echidna-origin / multi | 30 | 30 | 0 | 29 | 1 | 0 | Echidna-origin；三种方法均有可解析结果，构成 comparable subset |
| SmartBugs / multifunc | 30 | 10 | 20 | 10 | 0 | 20 | SmartBugs adapted；Original 可描述，Harness compile_error 不参与比较 |
| SmartBugs / onefunc | 30 | 10 | 20 | 10 | 0 | 20 | SmartBugs adapted；Original 可描述，Harness compile_error 不参与比较 |
| 总计 | 120 | 80 | 40 | 79 | 1 | 40 | adapted real-source evidence；不构成大规模真实合约评估 |

注：budget_exhausted 是 right-censored，不表示安全或通过。40 条 SmartBugs Harness compile_error 被排除出 comparative outcomes。
