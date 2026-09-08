# C5 Decision

## 当前判断

| 决策项 | 判断 | 依据 |
|---|---|---|
| 是否可以进入 C6 正文精修 | **可以** | C3/C4 草稿已有窄定位、证据 crosswalk、术语边界和 B4 数字；C5 已生成逐节审计输入 |
| 是否可以进入最终投稿 | **不可以** | 28 个 citation slots 全部仍为 `TODO_VERIFY`；最终图表尚未人工制作和审图；citation marker/key 仍需统一 |
| 是否需要补引用 | **需要，且是投稿前硬阻塞** | 仓库没有 verified references，Related Work 和 Echidna/background claims 尚未正式核验 |
| 是否需要补图表 | **需要制作和人工审图** | C5 已提供 Figure 1--4 输入规格与 Table 1--6 草稿，但尚未生成图片或正式排版表 |
| 是否需要补实验 | **C5 不需要** | 当前任务是证据整合与审计；B4 结果已存在且本阶段禁止运行实验 |
| 是否现在做 30 seed | **不建议** | 当前主要阻塞是正式引用、图表和语义/外部效度；不能用更多同类 seed 替代这些工作 |

## 当前可进入的论文路线

最现实路线是把论文定位为：

> 面向既有属性模糊器的属性定向交易序列 Harness 合成方法，以及受控机制证据、有限公开任务描述性评价和执行语义边界审计。

C6 应优先完成：

1. 根据 `verified_reference_checklist.tsv` 逐条人工核验原始论文、官方文档、benchmark repository 和 artifact guidance。
2. 生成正式 references 文件，并保持 citation slot、正文 marker、BibTeX key 的一一映射。
3. 依据 `figure_input_specs.md` 制作 Figure 1--4，人工检查 PHS/Echidna 边界、Original/wrapper 语义和 quarantine 分支。
4. 将 `final_table_drafts.md` 转成目标 venue 的最终表格，保留 Table 3 的 `conditional`、budget_exhausted 注释和审计字段。
5. 对 revised full draft、citation markup、图表和结论再做一次 forbidden-claim scan 与数字对齐检查。

## 是否补 B5 benchmark

B5 是否补充 benchmark 取决于目标会议、时间和可执行的语义方案；它不是 C5 的前置条件，也不能把新结果混入当前 V1/B4 表。若决定补，应另行预登记、使用独立 provenance、声明纳入规则并保持与 V1 主线分离。

优先级上，若目标是扩大论文外部效度，补 2--4 个不同来源、调用者/状态语义或规模类型的 public benchmark 比继续增加当前任务 seed 更有信息增益。exercise2-access-control 可作为单独 caller-controlled conditional appendix 研究，但即使完成也不应自动进入四任务 pooled 表。

## 不能改变的边界

- 不能把 `references_todo.bib` 或 citation slot 当作正式引用。
- 不能把 `budget_exhausted` 写成 property passed、合约安全或无漏洞。
- 不能把 `main_table_usable=conditional` 改成 yes。
- 不能使用 Total calls 构造效率/加速结论。
- 不能把 Harness 与 Original 写成完全等价，也不能把 static gate 写成完整 native replay。
- 不能把 SMARTIAN、MuFuzz、IR-Fuzz 变成没有公平实验支撑的工具排名。
- 不能把 matched-random-v1、V2 或 excluded internal candidates 并入当前主结果。

## 结论

C5 结论为：**允许进入 C6 正文精修；不允许进入最终投稿。** 最大阻塞是正式引用和最终图表制作/人工审图，而不是 B4 结果复核。C5 不要求新增实验，当前不建议直接做 30 seed。
