# 论文结论边界

## A. 可以直接写入论文的结论

1. 本文提出一种面向显式安全属性的交易序列生成方法，通过属性相关性筛选状态依赖路径，并结合条件匹配、状态值写入匹配和有界重复访问生成可审计候选 Harness。
2. 在受控机制场景中，方法能够针对预先定义的无关路径、状态值方向、重复调用、多路径和多属性障碍生成有效触发序列。
3. 六个受控场景的主比较中，Full-K1 在 180 次运行中观察到 180 次属性违反，Original 在 180 次运行中观察到 171 次属性违反。该结果支持受控条件下的机制有效性，不等同于真实生态总体优势。
4. 为补充外部有效性，本文在四个 adapted real-source candidates 上执行了 120 条预注册运行，其中 80 条结果可用于描述性分析。
5. 两个 Echidna-origin adapted real-source candidates 共包含 60 条记录，Original、Full-K1 和 Full-K5 均有可解析的非 compile_error 结果。
6. 在这两个 Echidna-origin candidates 上，Full-K1 和 Full-K5 均保持了观测属性违反的能力。Full-K5 的一个 budget_exhausted 记录按 right-censored 处理。
7. SmartBugs Original-only 的 20 条 falsified 记录表明，相关 adapted targets 可以运行并观测到属性违反。
8. SmartBugs Full-K1/Full-K5 的 40 条 compile_error 记录揭示了 Solidity 0.4.25 下 Harness 生成或导入路径的工程限制。
9. 对 falsified rows 报告 calls-to-failure 和 sequence-length，可以描述发现轨迹的复杂度。
10. 真实来源结果用于说明适用边界，不用于替代受控机制证据，也不用于支持普适性性能排名。

## B. 不可以写入论文的结论

1. 不能写 large-scale real-world evaluation，因为真实来源 candidate 只有 4 个，且 40 条 Harness 记录为 compile_error。
2. 不能写 ecosystem-wide superiority，也不能声称在所有真实合约上优于 baseline。
3. 不能写 SmartBugs Harness comparative failure。40 条 compile_error 不是 Harness 的比较失败率，也不是检测失败。
4. 不能把 budget_exhausted as safe，不能把它写成属性通过、合约安全或没有漏洞。
5. 不能写 Original/Harness semantic equivalence。两者在调用者、交易原子性、回滚边界和外层调用结构上可能不同。
6. 不能写 total calls speedup。Total calls 不能直接代表相同工作量下的执行速度。
7. 不能把 SmartBugs Original-only 的 20 条 falsified 结果扩展为 Harness 的性能结论。
8. 不能把 40 条 compile_error 从分母删除后再声称 Harness 具有较低或较高的发现率。
9. 不能把 120 条 seed-level records 表述为 120 个独立真实合约，或由此声称真实来源实验规模充分。
10. 不能把受控场景的结果直接解释为对任意未适配 Solidity 合约的泛化证明。

## C. 审稿人可能质疑与答复

### 质疑 1：真实来源合约数量是否过少？

答复：是的，真实来源 candidates 数量有限。本文不把该部分定位为大规模生态评估，而将其定位为 adapted real-source evidence，用于检查方法在少量不同来源任务上的适用边界。主结论由受控机制证据支撑，真实来源结果作为外部有效性补充，并在局限性中明确报告候选数量。

### 质疑 2：源代码适配是否改变了任务含义？

答复：适配可能改变编译依赖、属性接口或部分执行环境，因此不能默认与原始任务完全等价。论文应逐项披露适配内容，并将真实来源结论限制为 adapted source setting。适配结果用于说明可执行性和观测属性违反的能力，不用于声称原始生态任务上的无条件性能优势。

### 质疑 3：属性定义和人工标注是否可靠？

答复：纳入的属性、来源说明和适配条件在运行前固定，结果判定依据运行日志中的属性状态，而不是事后根据结果修改标签。人工工作主要用于来源筛选、接口适配和 provenance 记录，不应被描述为独立的漏洞真值证明。未来可通过更多公开属性和独立复核进一步降低该风险。

### 质疑 4：为什么 40 条 compile_error 不算方法失败？

答复：这些行在 Harness 导入或编译阶段没有进入可比较的模糊测试执行，因此无法区分路径生成问题、跨版本依赖问题和属性检测能力问题。将其计为发现失败会混合工程可执行性与检测效能。正确做法是保留记录，作为 Solidity 0.4.25 下 Harness 支持的工程限制单独报告。

### 质疑 5：为什么不把 budget_exhausted 记为通过？

答复：预算耗尽只说明在给定预算内没有观察到反例，属于 right-censored observation。它没有排除更长序列、其他参数或更高预算下的反例，因此不支持安全性或属性通过结论。

### 质疑 6：Original 与 Harness 的比较是否公平？

答复：两者共享声明的预算和属性目标，但执行模型并不相同。调用者身份、交易原子性、回滚范围和每次外层调用包含的目标函数数量可能不同。因此论文只在相同 candidate、property 和声明执行模型边界内报告描述性差异，不声称语义等价或等量工作比较。

### 质疑 7：为什么自定义受控场景可以作为主实验？

答复：受控场景的目的不是模拟生态分布，而是隔离单一机制障碍并验证因果上更清晰的组件作用。它们能够检验属性相关筛选、值匹配和重复访问是否解决预先定义的问题。外部有效性则由适配真实来源补充实验承担，两者的目标和表述边界不同。

### 质疑 8：证据不足是否影响 C 会投稿可行性？

答复：证据不足以支撑大规模真实世界或生态级优越性主张，但可以支撑一篇聚焦属性定向交易序列生成、可审计 Harness 构造和受控机制验证的工具型论文初稿。投稿可行性取决于是否诚实区分机制证据、适配真实来源补充证据和工程限制，并完整报告排除项与语义威胁。

### 质疑 9：未来最有价值的补强是什么？

答复：优先扩展更多未适配或适配成本可记录的真实来源任务，并建立更完善的跨 Solidity 版本 Harness 生成与导入支持。在此之前，不应通过重复同一小型 candidate pool 的 seed 来替代合约多样性。
