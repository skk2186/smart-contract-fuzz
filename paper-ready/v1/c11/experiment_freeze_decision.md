# C11 实验冻结决策

## 决策摘要

**最终建议：NO，不建议继续新增实验。**

当前证据已经足以支撑一个收窄后的 CCF-C 论文闭环：方法是 Echidna 前的 property-directed preprocessing/Harness synthesis；核心贡献是属性级候选隔离与可追溯规划；结果分成 controlled mechanism evidence、有限 adapted real-source descriptive evidence 和明确的执行模型边界。`paper-ready/v1/b5/b5_cvenue_sufficiency_review.md` 已将 controlled package 判定为 `SUFFICIENT`，`paper-ready/v1/submission/c10_next_decision.md` 已给出 `READY_FOR_SUPERVISOR_REVIEW`。继续跑实验的主要动机只能是扩大外部有效性，而不是补齐当前核心机制 claim；在当前 C11 的约束下，新增运行会混入新的方法/数据版本，不能改善现有 claim 的可追溯性。

## 正文实验应该保留哪些

1. **受控机制包。** 保留 C10 已审计的 formal/controlled 结果，用于说明 dependency、property、repeat、value 和 Top-K 组件分别在隔离场景中的作用。标题和图注必须使用 `controlled mechanism evaluation`、`synthetic/controlled scenario` 等限定语，不称为真实生态 benchmark。
2. **per-property isolation 结果。** 将 `results/per-property-isolation/summary.json` 作为一个独立的机制级结果，建议单独一张紧凑表或一个小图：LEGACY_UNION 为 3 个变量、3 个 target functions、8 个候选、7 个无关候选、ratio 0.875、target rank 6、Top-1/3/5 均 false；PER_PROPERTY 为 1 个变量、1 个 target function、1 个候选、0 个无关候选、ratio 0、rank 1、Top-1/3/5 均 true。这个结果回答的是“属性级规划是否减少跨属性候选干扰”，不是“fuzzer 是否在真实合约上更快或更安全”。
3. **有限 adapted real-source sanity check。** 主文最多保留一个小表或一段状态分类：4 个 candidate、120 条预注册记录、79 falsified、1 budget_exhausted、40 compile_error；并在同一处写清楚这些记录是 descriptive、候选池很小、适配可能改变语义、Harness 与 Original 不等价。
4. **结果状态和 provenance 规则。** 正文保留对 `falsified`、`budget_exhausted`、`compile_error` 的定义，但不要把状态定义当作性能结果。

## 附录实验应该保留哪些

- 4 个 adapted/public candidate 的逐任务、逐方法、逐 seed 状态；
- 两个 Echidna-origin candidate 的有限可比子集，以及 SmartBugs Original-only 与 Harness compile limitation 的分开记录；
- 完整 candidate sequence、property/read-set/target/path provenance、Top-K 截断配置和 `results/per-property-isolation/summary.json` 的原始机器可读字段；
- formal/controlled 每个场景的路径、排序、repeat/value evidence 和静态 gate 证据；
- manifest、command、environment、raw/parsed/summary/status/checksum 等可追溯材料；
- Harness 生成源代码、property proxy 选择和 compile smoke 的工程日志；这些是复现与边界证据，不是安全性证明。

## 哪些结果不能作为主结果

- `budget_exhausted` 不能计入 property safe、pass 或“未发现漏洞”的安全结论；
- `compile_error` 不能计入 detection failure、false negative 或统一检测率；
- Original 与 Harness 的 falsification rate、Total calls、平均时间不能在没有 caller/transaction/rollback 语义对齐的前提下直接做优劣比较；
- SmartBugs Harness 的 compile limitation 不能变成 Harness 方法的检测失败；
- 118/120、79/120 或任何 observed falsification ratio 都不能被改写成跨生态成功率或统计显著的 superiority；
- 4 个 public/adapted candidate 不能作为真实生态代表；
- `results/matched-random-v1/` 的 quarantine/provenance unresolved 材料不能重新解冻、重算或进入新 claim；
- 仅有两个简单整数目标的 SMARTIAN 材料不能充当公平的第二 executable baseline；
- `MultiPropertyInterference.sol` 的 rank/Top-K 结果不能作为真实合约漏洞发现率或性能表。

## 哪些实验不值得继续做

以下方向已经有明确的低收益或高解释风险，不应作为当前论文收敛条件：

- 把所有 B4/B5 cell 从 10 seeds 机械扩展到 30 seeds，而没有新的非饱和 RQ；
- 为了制造更漂亮的 per-property 数字而修改 `MultiPropertyInterference.sol`、expected sequence、排序输出或候选过滤；
- 继续增加与既有 `NoisyFourStep`、`BranchValue`、`RepeatedCall`、`ResetExample` 同构且不引入新机制信息的 synthetic benchmark；
- 为了“凑 baseline 数量”强行复现 SMARTIAN、MuFuzz、IR-Fuzz、Harvey、ConFuzzius 或 SmarTest；
- 把 public task 改名、重分类或把内部 controlled toy 当成 public benchmark；
- 重新运行或重解释冻结的 `results/` 正式结果以适配当前 planner 代码；
- 在没有语义对齐的情况下继续做 Original/Harness 速度、调用次数或检测率比较；
- 本阶段运行新的 Echidna、扩大 seed、加入新 baseline 或新增 benchmark。

这些判断直接沿用 `paper-ready/v1/d0/experimental_weakness_review.md` 的低收益与边界审计，且符合 `paper-ready/v1/submission/c10_final_audit.md` 的冻结检查。

## 只有在什么条件下才允许新增实验

只有当导师/审稿意见指出一个**当前 claim 无法由已有文件回答的具体关键问题**时，才允许设计新增实验，并同时满足：

1. 先写出单一 RQ、预先定义 expected outcome/metric/status，不能以改善数字为目的；
2. 明确是补机制证据、外部有效性还是公平 baseline，不能把不同目标混成一轮；
3. 对比对象的 property oracle、caller model、transaction budget、rollback/atomicity、seed 和结果编码必须可比；否则只做 descriptive，不做 superiority；
4. 新实验必须使用新的 run/work 目录、记录 commit SHA、配置、命令、环境、状态和 checksum，不覆盖任何 frozen results；
5. 先完成 compile/semantic gate，`compile_error` 和 `budget_exhausted` 的处理规则在运行前固定；
6. 若涉及 Harness，必须先定义它与 Original 的语义差异和可比较指标，不能用总调用数替代 time-to-falsify；
7. 只有结果无论改善或恶化都能回答该 RQ 时才开跑，并在论文中保留失败和不确定性。

这些是未来条件，不是本阶段的行动项。

## 冻结结论

在现有 C10、B5、D0 和 per-property isolation 证据之上，论文应停止“再跑一些”式的实验推进，转入 claim 收窄、表格重排、related work 定位和匿名/模板检查。当前缺少的是更广泛外部有效性或第二个公平 executable baseline，而不是现有属性隔离机制的最小闭环；这些缺口不能通过无目标扩展实验诚实地补齐。因此本阶段建议 **NO：不继续新增实验**。
