# Threats to Validity

受控机制场景具有明确的障碍设计和较小的合约规模，因此能够有效隔离属性相关筛选、状态值匹配和有界重复等机制的作用，但其外部有效性有限。受控场景不能代表真实合约的函数数量、状态空间、依赖复杂度或编译环境。相应结果应被解释为机制证据，而不是对开放生态分布的抽样估计。

适配真实来源实验的 candidate 数量有限。本文只在 4 个 adapted real-source candidates 上执行 120 条预注册运行，其中 80 条结果可用于描述性分析。两个 Echidna-origin candidates 构成可比较子集，SmartBugs Original-only 结果仅用于说明 adapted targets 的可执行性和属性违反可观测性。因此，这些结果不能支持大规模真实世界评估，也不能外推为生态级性能优势。

真实来源任务经过编译器、属性接口或依赖路径适配，适配过程可能改变源代码组织、调用入口或部分执行环境。论文应报告每个任务的适配内容，并将结论限定在 adapted source setting。适配后的可执行性不能自动证明与原始合约语义完全一致。

SmartBugs Full-K1 和 Full-K5 的 40 条记录在 Solidity 0.4.25 下出现 import-path compile_error。这 40 条 compile_error 不参与比较。它们没有进入可比较的模糊测试执行，因此不应作为发现失败率、检测失败或性能负面结果。该问题应作为跨版本 Harness 生成与导入支持不足的工程限制单独报告。

唯一的 budget_exhausted 记录是 right-censored。它表示在声明预算内没有观测到属性违反，不表示属性通过、合约安全或不存在漏洞。相关记录可以用于完整性与删失说明，但不能转化为安全标签。

Original 与 Harness 使用的执行模型不同，调用者身份、交易原子性、回滚范围和外层调用结构可能存在差异。因此，本文不声称 Original 与 Harness 语义等价，也不使用 Total calls 直接推导 speedup。calls-to-failure、sequence-length、fuzz seconds 和 wall seconds 仅作为 falsified rows 上的描述性观测。

未来工作应扩展更多真实合约和更多属性任务，优先增加合约与来源的多样性，而不是只增加同一 candidate pool 的种子数。同时，需要完善跨 Solidity 版本的 Harness 生成、依赖导入和编译验证流程，以减少工程性排除项，并在语义对齐后再开展更广泛的比较。
