# 2 Background（中文草稿）

## 2.1 属性模糊测试与 safety property

属性模糊测试把“是否发现问题”表示为一个可以反复检查的程序属性。对智能合约而言，属性通常读取一个或多个状态变量，并在状态不满足预期关系时返回假。例如，属性可以检查两个标志是否同时处于某种状态，计数器是否发生下溢，或一个操作是否不应改变某个安全状态。模糊器生成交易、参数和执行上下文，直到属性观察到反例，或在给定预算内没有观察到反例。

Echidna 的工作方式适合表达这种 safety property。研究者提供合约、属性和执行配置，Echidna 在合约上探索调用并报告属性被违反的输入轨迹。本文使用 `falsified` 表示在声明的执行模型、输入和预算内观察到属性反例；使用 `budget_exhausted` 表示在预算内没有观察到反例。后者不是属性通过、合约安全或不存在漏洞的证明。

## 2.2 状态读写与交易序列

智能合约的函数可以读取或写入状态变量。若函数 A 写入变量 `s`，函数 B 读取 `s`，则 A 可能是到达 B 所需状态的一个候选前驱。这种写读关系可以构造基础的 transaction sequence。然而，读写依赖只是必要线索而不是完整答案：函数写入的数值可能与后续条件方向相反，重置函数可能清除已经建立的状态，或者目标状态需要同一个函数多次访问。

transaction sequence 是一组按顺序执行的合约调用，例如 `register() -> deposit() -> withdraw(x)`。有状态模糊测试需要同时探索顺序和参数。本文所说的 bounded repeat，是允许某个函数在一条候选序列中出现有限次数，例如 `deposit() -> deposit()`，而不是无限制展开搜索。lightweight value evidence 则来自简单的常量写入和 `require` 条件，用来判断某个候选是否更可能满足后续值约束。

## 2.3 Harness 与 Top-K

Harness 是一个为测试而编写的外部合约或调用包装层。本文的 Harness synthesis 将候选 transaction sequence 写入 Solidity wrapper：候选中的函数顺序在生成阶段固定，Echidna 后续主要对 wrapper 参数和属性继续 fuzz。Top-K 表示最终写入 Harness 的候选条目数量。K1 是一个候选 Harness 条目，K5 是五个候选 Harness 条目；它们不是 Original 中等价的交易长度，也不是五笔等量交易的工作量定义。

使用 Top-K 的原因是保留少量备选路径。当仅靠读写依赖时，多条路径可能得分相同，或者目标路径因为值方向、重复访问和 reset 干扰而没有排在第一位。可解释排序让研究者能够检查一条路径为什么被保留：它是否触及属性相关状态，是否包含所需重复，是否满足已知的简单值条件，以及是否属于候选池中的前 K 条。

## 2.4 两种执行模型

本文必须区分 Original multi-transaction model 与 wrapper execution model。Original 由 Echidna 对目标合约进行多笔独立交易探索。每笔调用具有自己的交易边界，sender 可能变化；某笔失败时，通常只回滚当前交易，之前已经提交的状态仍然存在。

Harness wrapper execution model 则在一次外层 wrapper 调用中连续执行候选函数。目标调用通常由同一个 Harness 地址发起，多个函数调用可能共享一次 transaction atomicity；某一步 revert 可能使整个 wrapper 回滚。当前生成器也没有通用的逐步 `msg.value` 或不同 sender 建模。因而，caller、transaction atomicity、rollback scope、`msg.value`、区块环境、external call 和 reentrancy 都需要逐任务审计。本文报告的 Harness 结果准确含义是：在当前 wrapper execution model 下观察到的结果，而不是与 Original 多交易模型完全等价的结果。

这些概念构成本文的方法与评价基础。Property-directed 的含义是围绕属性读取的状态组织候选，而不是声称所有状态依赖都能被完整建模；Harness synthesis 的含义是生成外部 wrapper，而不是修改 Echidna core；Top-K、bounded repeat 和 value evidence 都是有界、可检查的工程机制。
