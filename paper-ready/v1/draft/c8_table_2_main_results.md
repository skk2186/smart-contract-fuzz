# 表 2：主实验结果（受控场景）

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
