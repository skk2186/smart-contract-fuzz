# C3 Revision Notes

## 本阶段做了什么

1. 在不运行实验、不调用 Echidna、不改变已有结果的前提下，基于 C2 草稿和 C1 证据矩阵完成论文文字修订。
2. 新增正式方法名称 PHS：属性定向 Harness 合成方法（Property-directed Harness Synthesis）。
3. 新增去内部化后的标题、摘要、完整中文论文、引言和实验评估。
4. 新增 Related Work 引用槽位与后续核验计划，未下载或编造任何论文引用。
5. 新增风格与主张审计，对方法名、流程词、禁用主张、数字、任务范围和术语进行检查。
6. 修正 C2 closeout 中“是否保留 forbidden claims”的歧义，将其拆分为“是否作为论文主张写入”和“是否保留检查与限制说明”。

## 为什么从 V1 改为 PHS

V1 是研究线和证据目录中的内部版本边界，适合 provenance 和文件组织，但不适合作为论文方法名称。PHS 直接表达方法的核心对象和位置：它围绕显式 property 规划候选 transaction sequence，并以外部 Harness 形式交给 Echidna。论文正文因此使用 PHS 或“属性定向 Harness 合成方法”，内部路径仍可保留 v1 以维持证据管理。

## 哪些主张被强化

- 将贡献从“结果整理”改写为 PHS 的方法组合：property-directed preprocessing、external Harness synthesis、bounded repeat、lightweight value evidence 和 interpretable Top-K。
- 将机制证据组织为四类障碍：无关路径、值方向、重复访问和 reset/候选选择。
- 将公开任务评价明确成四任务、三方法、seed 1–10 的 120-run descriptive comparison。
- 将 artifact、checksum 和 parser/status 结果放入运行链叙事，而不是暗示安全性。
- 将语义边界纳入研究问题，使 caller、transaction atomicity 和 rollback scope 成为结果解释的一部分。
- 将 Related Work 从泛化叙述改为带引用槽位的定位框架。

## 哪些限制被保留

- 120 个运行包含 118 falsified 和 2 budget_exhausted；后者仍表示预算内未观察到反例，不是 property passed 或 contract safe。
- 120/120 artifact complete、120/120 checksum pass、0 parser/status mismatch、0 startup_error、0 unknown_error、0 incomplete 均保持不变。
- Formal controlled benchmarks 只支持受控机制观察，不代表真实生态。
- public benchmark 只有 4 个 supported；exercise2-access-control 保持 conditional。
- Harness wrapper 与 Original multi-transaction model 不默认等价。
- 不使用 Total calls 作为跨模型工作量或加速证据。
- 没有完整可比的 SMARTIAN、MuFuzz、IR-Fuzz 工具级实验。
- provenance 不完整的历史控制实验继续 quarantine，不用于新主张。

## 还不能作为终稿的内容

- Related Work 的作者、年份、会议、版本、论文事实和 BibTeX 尚未逐条核验。
- 表格、图、附录和正文之间尚未建立最终交叉引用。
- 公开任务的 run-level 日志、checksum 和语义审计仍需要作者人工抽查。
- 当前材料不足以支持更宽的生态泛化、工具排名、跨模型等价或运行效率结论。
- 中英文术语、连字符、方法大小写和表格标题仍需按目标投稿格式统一。
- 完整中文稿仍是可人工修改的初稿，不是最终投稿版本。

## C4 建议任务

1. 逐个填充 Related Work 的引用槽位，只使用核验后的原始论文或官方来源。
2. 对 PHS 方法、四个 RQ、结果表和限制段落执行证据逐句映射。
3. 从现有冻结表格制作最终图表和附录，保持 120-run 口径和 conditional 标记。
4. 抽查 run-level manifest、raw log、parsed、status 和 checksum，确认论文表与原始产物一致。
5. 建立术语表并统一 property-directed、transaction sequence、Harness synthesis、wrapper execution model、Original multi-transaction model 和 PHS 的写法。
6. 继续保持不运行新实验的论文修订线；任何 public benchmark、caller-controlled replay 或外部 baseline 都应另行预登记、单独 provenance 和单独结论。
