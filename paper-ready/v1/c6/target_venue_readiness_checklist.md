# C6 Target-Venue Readiness Checklist

目标 venue 尚未指定。本清单因此检查通用投稿条件，不假定某个会议的页数、匿名化、引用格式或 artifact policy。

## 当前状态总览

| 项目 | 状态 | 说明 |
|---|---|---|
| 研究主张范围 | ready | PHS 被定位为 Echidna 之前的外部 property-directed Harness synthesis preprocessing |
| 当前正文精修 | ready | C6 已提供 cleaned draft scaffold；仍需人工逐段改写 |
| 方法定位 | ready | 不称为新的完整 fuzzer，不扩大为生态级结论 |
| B4 实验结果 | partial | 120-run 结果和审计字段对齐，但 final table 与 venue 版式尚未定稿 |
| 实验规模/外部效度 | partial | 四个 supported public tasks、每组 10 seed；不能代表广泛生态 |
| 引用 | blocked | 28 个 slots 均为 `TODO_VERIFY`，没有 verified references |
| 图表 | partial | Figure 1--4 和 Table 1--6 已有制作输入，尚未生成和人工审图 |
| 附录 | partial | run-level、manifest、evidence index 字段已有来源，版式和取舍未定 |
| 可复现性 | partial | provenance 字段和 120/120 审计已有；独立复现与 native replay 仍有限 |
| 写作格式 | blocked | 未确定目标 venue，尚未套用官方模板 |
| 匿名化 | blocked | 未根据目标 venue 检查作者、仓库、artifact 链接和自引用匿名化 |
| 伦理/合规 | partial | 当前材料未发现新增风险，但仍需按目标 venue 的 artifact、数据集和软件许可要求复核 |
| 禁用主张控制 | ready | C5 scan 为 PASS；最终排版和英文版仍需复扫 |
| 最终投稿 | blocked | 正式引用、图表、格式和匿名化尚未完成 |

## 研究主张

- [ready] 首次定义使用“属性定向 Harness 合成方法（Property-directed Harness Synthesis，PHS）”，后续统一使用 PHS。
- [ready] 明确 PHS 是外部 preprocessing/Harness synthesis layer，不是新的完整智能合约模糊器。
- [ready] 受控 benchmark 只支持机制性、范围内的观察。
- [ready] 四个 supported public tasks 只支持 120-run descriptive comparison，不作为生态代表性证明。
- [ready] `budget_exhausted` 明确表示预算内未观察到反例，不是通过或安全。
- [ready] Original/Harness 的 caller、atomicity、rollback 和 context 差异保留。
- [ready] exercise2-access-control 继续是 conditional；matched-random-v1 继续 quarantine。
- [partial] 将所有 claim 与 evidence id、table/figure marker 和最终引用逐句对齐。

## 实验结果

- [ready] 主结果数字锁定为 120 runs、118 falsified、2 budget_exhausted。
- [ready] 120/120 artifact complete、120/120 checksum pass、0 parser/status mismatch、0 startup_error、0 unknown_error、0 incomplete 保持一致。
- [ready] `main_table_usable=conditional` 不变。
- [partial] Table 3/4 需要按最终 venue 宽度重新排版，并复核表注。
- [partial] run-level details 不放完整正文，应放附录或 artifact package。
- [partial] 任何英文版、图注或摘要修改后都要重新核对上述数字。

## 引用

- [blocked] 人工核验 C1--C28 citation slots。
- [blocked] 为每个 marker 填写 verified title、authors、year、venue、DOI/URL；C6 template 目前全部留空。
- [blocked] 生成正式 references 文件前，不能把 `references_todo.bib` 改名或替代。
- [blocked] 复查 Echidna、Harvey、ConFuzzius、SMARTIAN、IR-Fuzz、MuFuzz、SmarTest、SmartBugs 等方法边界。
- [partial] 完成 marker-to-BibTeX-key 映射后，扫描正文是否存在未映射 marker。

## 图表

- [partial] Figure 1：检查 PHS/Echidna 分界和 K 的含义。
- [partial] Figure 2：检查 Dependency/Property/Repeat/Value/Top-K 不是可达性或效率证明。
- [partial] Figure 3：检查 Original/wrapper 双时间线、caller、rollback 和 static gate。
- [partial] Figure 4：检查 provenance chain、checksum 和 quarantine 分支。
- [partial] Table 1：分开 supported、conditional、excluded。
- [partial] Table 2：只放 controlled mechanism evidence。
- [partial] Table 3：保留 10-seed、120-run、budget_exhausted 和 conditional。
- [partial] Table 4：作为 provenance/status audit，不写成安全表。
- [partial] Table 5：作为 claim boundary，不当作结果。
- [partial] Table 6：保留 threat、mitigation 和 remaining limitation。
- [blocked] 尚未完成最终矢量制图、caption 定稿和人工审图签字。

## 附录

- [partial] Appendix A1：只展开 `main10_results_by_run.tsv` 和 evidence index 真实提供的字段。
- [partial] Appendix A2：保留 manifest、command、environment、tool/config、seed 和状态字段。
- [partial] Appendix A3：保留 evidence id、source、status、allowed use 和 quarantine note。
- [partial] 不增加不存在的 run-level 字段，不从 `work/` 手工补数据。
- [partial] 说明 static gate、conditional task 和 matched-random quarantine 的边界。

## 可复现性

- [ready] 输入、命令、环境、raw、parsed、summary、status 和 checksum 的 provenance 结构已定义。
- [partial] 需要把正式 artifact package 的路径、版本和复现入口按 venue 要求写入附录。
- [partial] 需要说明 artifact complete/checksum pass 不等于独立复现、安全或语义等价。
- [partial] 完整 native replay 与 caller-controlled replay 仍是限制和未来工作。

## 写作格式

- [blocked] 选择目标 venue、官方模板、页数和摘要字数。
- [blocked] 确定引用格式、caption 格式、表格宽度和附录规则。
- [partial] 中文 cleaned scaffold 已生成；若目标 venue 为英文，需进行论文级英文改写。
- [partial] 统一 property-directed、Harness synthesis、transaction sequence、wrapper execution model、Original multi-transaction model 和 PHS 的大小写/连字符。
- [ready] 已删除内部阶段叙述方向，正文不把 C5/C6 等流程编号作为论文内容。

## 匿名化

- [blocked] 检查作者、机构、仓库 URL、artifact DOI、提交记录和自引用是否需要匿名处理。
- [blocked] 确认图表、代码包和补充材料不会暴露不允许的信息。
- [partial] 当前 scaffold 未新增作者或机构信息。

## 伦理/合规

- [partial] 检查 Echidna、SmartBugs/Curated、benchmark source 和适配文件的许可证与再分发要求。
- [partial] 说明公开 benchmark 的来源、适配和 property 改动，不暗示对原始数据集的完整覆盖。
- [partial] 按 venue 要求填写 artifact、数据集、软件版本和可复现性声明。
- [ready] 本阶段没有下载新论文、运行新实验或新增外部数据。

## 最终风险判断

当前最主要风险不是 B4 数字，而是：

1. 正式引用仍未核验；
2. 图表尚未制作和人工审图；
3. 目标 venue 格式、英文版和匿名化尚未确定；
4. 四个 supported tasks 和 wrapper 语义仍限制外部效度与跨模型解释。

因此，当前判断为：**正文精修 ready；引用 blocked；图表 partial；实验规模 partial；方法定位 ready；禁用主张控制 ready；最终投稿 blocked。**
