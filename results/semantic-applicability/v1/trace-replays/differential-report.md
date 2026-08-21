# V1 Harness差分语义回归报告

## 结论

- 已知固定成功路径重放：11/11通过；
- 静态supported目标：10/10通过固定路径重放；
- conditional目标：1/1在同一调用者关系下通过；
- 通用负面对照确认：调用者交替和wrapper原子回滚会产生可观察差异。

这支持一个窄结论：在固定参数、每一步均成功、没有检出的环境依赖且调用者关系对齐时，现有11个目标的直接调用路径和实际生成Harness得到相同的属性相关最终结果。

它不证明真实跨区块多交易与wrapper单交易完全等价。直接路径是在本地EVM属性检查中以独立外部调用帧重放，不能模拟区块推进、完整交易调度或任意失败前缀。

## 逐目标结果

| cohort | benchmark | compiler | static | replay |
|---|---|---|---|---|
| formal | branch-value | 0.8.20 | supported | passed |
| formal | noisy-four-step | 0.8.20 | supported | passed |
| formal | repeated-call | 0.8.20 | supported | passed |
| formal | reset-example | 0.8.20 | supported | passed |
| formal-b2 | alternative-path | 0.8.20 | supported | passed |
| formal-b2 | multi-property | 0.8.20 | supported | passed |
| public-c1 | echidna-flags | 0.8.20 | supported | passed |
| public-c1 | echidna-multi | 0.8.20 | supported | passed |
| public-c1 | exercise2-access-control | 0.8.20 | conditional | passed |
| public-c1 | smartbugs-multifunc | 0.4.25 | supported | passed |
| public-c1 | smartbugs-onefunc | 0.4.25 | supported | passed |

## 对论文结论的影响

- 10个supported目标可以进入后续公开基准筛选，但必须继续保留atomicity caveat；
- exercise2只能作为同调用者条件下的结果，不能用来隔离纯序列排序收益；
- 当前Harness仍默认不支持payable/msg.value、构造参数及高风险delegatecall/selfdestruct案例；
- 后续公开基准必须先经过静态适用性检查，再决定进入主比较、条件分析或排除流程。
