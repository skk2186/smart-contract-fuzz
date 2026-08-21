# V1 Harness语义适用性静态审计

> 本报告是保守的源码特征筛查，不是Original多交易执行与Harness单交易执行的语义等价证明。

## 汇总

- 审计目标：11
- supported：10
- conditional：1
- unsupported：0
- 所有目标均带有`atomicity_caveat=1`，因为Harness把多步调用合并在一次wrapper交易内。

## 逐目标结果

| cohort | benchmark | classification | reasons |
|---|---|---|---|
| formal | branch-value | supported | atomicity_caveat |
| formal | noisy-four-step | supported | atomicity_caveat |
| formal | repeated-call | supported | atomicity_caveat |
| formal | reset-example | supported | atomicity_caveat |
| formal-b2 | alternative-path | supported | atomicity_caveat |
| formal-b2 | multi-property | supported | atomicity_caveat |
| public-c1 | echidna-flags | supported | atomicity_caveat |
| public-c1 | echidna-multi | supported | atomicity_caveat |
| public-c1 | exercise2-access-control | conditional | address_keyed_mapping;msg_sender |
| public-c1 | smartbugs-multifunc | supported | atomicity_caveat |
| public-c1 | smartbugs-onefunc | supported | atomicity_caveat |

## 分类含义

- `supported`：未检出额外高风险源码特征，但仍需验证交易原子性差异。
- `conditional`：检出调用者、区块环境、外部交互等特征，只有在逐合同人工分析或差分重放后才能纳入可比实验。
- `unsupported`：当前生成器不能忠实处理，或风险过高；默认不得进入Harness与Original性能比较。

## 限制与下一步

该检查器采用保守的源码模式匹配并递归读取本地import。它可能漏掉继承构造函数、经库封装的环境读取或复杂外部调用，也可能标记与目标属性无关的代码。下一步必须对条件支持目标进行人工复核和差分执行。
