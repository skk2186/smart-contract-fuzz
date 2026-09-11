# 投稿前 Claim Checklist

## 可写主张

- 本文提出面向显式安全属性的多交易序列生成方法。
- 属性相关变量反向切片可以把状态读写依赖限制在目标属性相关区域。
- 条件约束匹配、状态值方向匹配、有界重复和 Top-K 候选序列共同构成可解释的路径筛选机制。
- controlled evidence 支持方法在预先定义的受控障碍上提供更聚焦的有效触发前缀。
- 受控实验应作为主机制证据，adapted real-source evidence 应作为补充的外部有效性检查。
- 两个 Echidna-origin candidates 上的 Original、Full-K1、Full-K5 可以构成窄范围 comparable subset。
- SmartBugs Original-only 的 20 条 falsified 记录说明适配目标可运行并能观测属性违反。
- 4 candidates、120 runs、80 usable/descriptive records 和 40 compile_error engineering rows 的分层记录可以作为适用边界与工程限制证据。
- falsified rows 的 calls-to-failure、sequence-length、fuzz seconds 和 wall seconds 可以作为描述性轨迹指标。

## 禁止主张

- 不得写成大规模真实合约实验或完整生态评估。
- 不得声称方法在整个真实合约生态中优于 baseline。
- 不得把 SmartBugs Harness comparative failure 写成方法发现失败。
- 不得把 compile_error 当作性能结果、负面发现率或漏洞未检出。
- 不得把 budget_exhausted 当作安全、通过或没有漏洞。
- 不得声称 Original 与 Harness 语义等价。
- 不得使用不同 execution model 的 Total calls 直接声称 speedup。
- 不得把 controlled evidence 和 adapted real-source evidence 合并成一个总成功率。
- 不得把 exercise2 纳入 supported pool。

## 需要表格支持的主张

- 六个受控场景和逐行分母：表 1、表 2。
- 4 candidates、120 runs、80/40 分层：表 3。
- 两个 Echidna-origin comparable cells、SmartBugs descriptive-only 和 Harness engineering cells：表 4。
- 40 条 compile_error、1 条 right-censored 及其解释：表 3、表 4、表 5。
- 受控证据、补充证据和排除项的关系：图 2、图 3。

## 需要引用支持的主张

- 智能合约模糊测试背景：ContractFuzzer、sFuzz、ILF、Harvey、Echidna。
- 数据流、依赖和静态分析辅助测试：SMARTIAN、ConFuzzius。
- 状态快照和序列感知工作：ItyFuzz、MuFuzz。
- 属性测试背景：QuickCheck 和 Echidna。
- 工具/基准背景：SmartBugs、Olympia。
- high_confidence 文献在定稿前必须完成 ACM/IEEE/DBLP 复核。

## 需要放入有效性威胁的主张

- 受控 benchmark 的外部有效性有限。
- 真实来源 candidate 数量有限，适配不等于原始部署语义。
- 人工属性接口和标注可能带来偏差。
- Solidity 0.4.25 Harness import-path compile_error 是工程限制。
- budget_exhausted 具有 right-censoring 性质。
- Original 和 Harness 的 caller、回滚和交易边界不同。
- Solidity 版本、复杂参数类型和跨合约交互覆盖不足。

## 需要导师确认的主张

- B-2 扩展放在主文结果小节还是附录。
- 表 2 的 calls-to-failure 缺失标记是否符合最终投稿版式。
- 两条 high_confidence 文献是否在定稿前升级为 verified。
- 主文是否保留全部 5 张表，或将表 3–5 移入补充材料。
- 是否在没有新增实验的前提下，将当前结果定位为机制论文而非生态评测论文。
