# 4 Method（中文草稿）

## 4.1 Overview

本文方法是位于 Echidna 之前的 property-directed Harness synthesis preprocessing。输入是 Solidity 合约、显式的 Echidna safety property、编译与测试配置，以及用于控制候选展开的参数。输出不是一个独立的 fuzzer，而是一组带有来源和评分证据的 transaction sequence 候选，以及由这些候选生成的 Solidity wrapper Harness。Echidna core 不被修改，仍负责对 Harness 的外层参数、可达状态和 safety property 进行后续探索。

方法的处理顺序为：提取属性相关状态，建立函数状态读写摘要，沿依赖关系反向过滤相关写入，构造基础候选序列，在声明的上限内扩展必要的重复访问，匹配简单值约束，按可解释证据排序，选择 Top-K，并生成 Harness。Full 方法把这些组件组合起来；Property、Repeat、Value 和 Top-K 也可以分别用于机制对照。

## 4.2 Property-related state extraction

第一步从显式 safety property 中识别其读取的状态变量。对于直接访问状态字段、通过简单表达式比较状态，或由属性函数返回的状态关系，分析器记录变量名、读操作所在属性和可能的比较方向。这里的“相关”首先指属性直接观察到的状态，而不是所有合约状态的完整语义闭包。

随后，分析器为每个可调用函数生成读写摘要，包括函数读取的状态集合、写入的状态集合、可见性和可用于 Harness 调用的签名。该摘要为后续路径构造提供静态线索。对于复杂别名、动态索引、外部调用和环境变量，若当前分析器不能可靠解析，则不应把未知结果当作已证明无关，而应在适用性审计中保留风险。

## 4.3 Backward filtering of relevant writes

给定属性相关状态集合，方法从属性的最终读取点向前追溯可能写入这些状态的函数。若函数 A 写入的状态被函数 B 后续读取，或者 A 写入的状态通过已记录的依赖关系影响属性读取，则 A 可以作为 B 或属性前缀的候选。反向过滤会删除无法连接到目标属性状态的路径，同时保留能够建立前置状态的写入。

这一过程的目的不是证明完整可达性，而是减少明显无关的候选。过滤结果会保存 retained path 数量、被删除路径和每条保留路径的依赖证据，因而可以回答“为什么该路径仍在候选池中”。在 Formal controlled benchmarks 上，四个主要受控基准的 Dependency 候选合计 92 条，Property 阶段保留 31 条；这一变化用于描述候选空间和机制行为，不直接转化为端到端性能结论。

## 4.4 Candidate transaction-sequence construction

在过滤后的函数图上，方法从可能的初始化或状态建立函数开始，沿写读依赖向属性观察点扩展候选 transaction sequence。每个候选保存函数顺序、签名、路径长度、涉及状态、前后依赖关系和可能的失败条件。路径生成必须尊重函数可调用性和已知的简单前置条件；无法判断的条件保留为 unknown，而不是静默地视为满足。

候选序列的顺序在生成阶段固定，但序列中的函数参数不被静态分析器硬编码为单一值。生成 Harness 后，Echidna 仍可以 fuzz wrapper 参数。这样，方法利用静态证据规划调用顺序，同时把参数空间留给属性模糊器探索。对 BranchValue 一类问题，静态值证据用于排序和初始候选选择，并不声称替代完整的符号执行或求解器。

## 4.5 Bounded repetition

若目标状态需要同一函数被多次调用，单次访问的无环路径生成会漏掉必要序列。方法允许在预先声明的访问上限内重复某个函数或函数边。例如，deposit(x) -> deposit(y) 可以表达累计状态逐步变化，run(a) -> run(b) 可以表达第一次初始化、第二次触发的模式。

重复扩展受 bounded repeat 约束，以避免无限展开和候选爆炸。每条重复路径记录重复函数、访问次数和触发原因。若没有证据表明重复是必要的，方法不应为了增加路径数量而无界复制函数。RepeatedCall controlled benchmark 用于检查该组件能否保留声明的重复目标；它不代表所有真实合约都应使用相同的重复上限。

## 4.6 Lightweight value evidence

仅凭变量依赖可能把值方向错误的路径排在正确路径之前。因此，方法从简单常量赋值、简单算术关系以及函数入口的 require 条件中提取 value evidence。例如，若后续函数要求输入等于 12，前置条件要求另一个输入等于 8，候选可以记录这些约束作为路径匹配依据；若某条分支把属性相关标志写成与目标方向相反的值，则该分支获得冲突标记或较低优先级。

这些证据是轻量的、可解释的、局部的。它们帮助区分已知的值方向，不覆盖复杂算术、动态映射、环境值或跨合约数据流。未知或冲突不应被改写成成功条件，而应保存在候选元数据中，供排序和人工审计使用。

## 4.7 Interpretable Top-K ranking

方法把 Property、Repeat、Value 和路径可行性等信息组织为可检查的排序依据。一个候选首先需要与属性相关状态相连；包含必要重复的候选应避免因访问次数而被错误删除；满足简单值条件、没有已知冲突且能到达目标状态的候选获得更高优先级。排序结果同时保留 display rank、并列或不确定标记，使人工检查可以区分严格排序和同分集合。

Top-K 是对候选 Harness 条目的截断。K1 表示只写入排序前的一条候选 Harness 条目，K5 表示写入前五条候选 Harness 条目。它们不是 Original 中等价的交易长度，也不代表相同的底层工作量。选择 K5 的含义是保留更多静态候选，不能解释为一定比 K1 安全或一定更快。Formal 结果中的 Top-K 行为用于说明候选选择障碍和机制证据；公开任务中 K1/K5 的差异只作描述性报告。

## 4.8 Solidity Harness synthesis

对每个选中的候选，生成器创建一个外部 Solidity Harness，并把目标合约实例化或连接到声明的测试对象。wrapper 暴露供 Echidna 调用的入口；入口内部按候选记录的顺序调用目标函数，并把需要 fuzz 的参数传入对应位置。生成器同时输出候选 JSON、状态和编译相关记录，以便检查 Harness 是否只包含声明的 Top-K 路径。

固定候选顺序意味着方法把一部分交易序列搜索转化为静态候选选择，但并没有固定所有参数。Echidna 仍然承担参数 fuzzing、属性检查和反例报告。方法因此是对既有属性模糊测试器的外部 preprocessing，不是新的智能合约 fuzzer，也不替代 Echidna 的执行和判定职责。

## 4.9 Semantic boundary of generated Harness

生成 Harness 时必须显式标记其 wrapper execution model。Original multi-transaction model 由 Echidna 生成多笔独立交易，交易之间 sender 可能变化，一笔交易失败通常只回滚该笔交易。Harness 则可能在一次外层 wrapper 调用内连续执行多个目标函数，目标调用通常由同一个 Harness 地址发起，多个调用共享一次 transaction atomicity；其中一步 revert 可能使整个 wrapper 回滚。

因此，Harness 与 Original 在 msg.sender、caller alternation、transaction atomicity、rollback scope、msg.value、payable 行为、区块环境、external call、reentrancy、constructor/deployer 和 address-keyed state 上不能默认等价。固定成功路径的最终属性相关状态一致，也只能说明窄条件下的可重放性。特别是，若任务依赖 owner 或按地址索引的 mapping，当前 Harness 无法自动模拟不同 sender，必须降为 conditional 或单独复核。

方法结果的准确解释是：在生成的 wrapper 执行模型、声明的输入和预算内观察到的结果。本文不以 Harness 代替 Original，不把 K1/K5 写成等价交易长度，也不使用跨执行层次的 Total calls 推导 speedup。
