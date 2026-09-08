# C6 Decision

## 当前判断

| 决策项 | 判断 |
|---|---|
| 是否可以进入 C7 | **可以**，但 C7 应继续作为正文精修与引用替换阶段 |
| 是否可以最终投稿 | **不可以** |
| 是否必须人工补引用 | **必须**；28 个 citation slots 仍为 `TODO_VERIFY` |
| 是否必须制作图表 | **必须**；Figure 1--4 尚未生成和人工审图 |
| 是否建议现在补实验 | **不建议**；C6 不需要新实验，现有 B4 结果足以支持当前窄定位 scaffold |
| 是否建议补 benchmark | **可选但有价值**；若时间允许，B5 补 2--4 个 public benchmark 比盲目扩展同一任务 seed 更有信息增益 |
| 是否建议英文改写 | **建议**；在引用和图表稳定后进行论文级英文改写，不做机械逐句翻译 |

## C7 应该做什么

1. 逐条人工核验 C6 mapping template 中的原始论文、官方文档、benchmark repository 和 artifact/reproducibility guidance。
2. 形成正式 BibTeX，并把正文 marker 映射到真实 key；在完成前保持 `TODO_VERIFY`，不提交正式 references。
3. 依据 C6 production checklist 制作 Figure 1--4 和 Table 1--6，人工复核 caption、语义边界、conditional、quarantine 和 `main_table_usable=conditional`。
4. 以 C6 cleaned draft 为底稿进行逐段中文精修，删减重复防守句，保留必要证据限制和 `budget_exhausted` 定义。
5. 选择目标 venue 后套用模板，确定页数、摘要、引用、附录、匿名化和 artifact 规则。
6. 完成英文版或英文投稿版本后，对摘要、正文、图注、表注和附录重新执行 forbidden-claim 与数字一致性扫描。

## 两条投稿路径

### 当前最短投稿路径

适用于时间紧的窄定位投稿尝试：

- 保持 PHS 为 Echidna 之前的外部 Harness synthesis preprocessing；
- 先完成核心 Echidna、stateful fuzzing、主要邻近工具和 benchmark 来源的人工核验；
- 制作 Figure 1--4，压缩 Table 1--6 到 venue 允许的正文/附录布局；
- 以四个 supported public tasks 的 120-run descriptive comparison 为主结果；
- 明确不做工具级排名、效率结论、语义等价或生态泛化；
- 将 B5、caller-controlled replay 和更广 baseline 作为 future work 或独立附录计划。

该路径仍必须在正式引用和图表完成后才能投稿。

### 当前最稳投稿路径

适用于有更多准备时间的投稿：

- 先完成全部引用核验与 Related Work 重写；
- 完成 Figure 1--4、Table 1--6、Appendix A1--A3 和 artifact/reproducibility 说明；
- 对 exercise2-access-control 设计独立 caller-controlled conditional replay appendix，但不自动并入 supported pooled 表；
- 若目标会议重视外部效度，独立预登记 B5，补 2--4 个不同来源、调用者/状态语义或规模类型的 public benchmark；
- 再根据目标 venue 决定是否增加可比的外部 baseline，所有新结果与当前证据独立管理。

这条路径的信息增益高于直接为当前四个任务追加 30 seed，但会增加实验与审计工作，不能作为 C6 的默认前置动作。

## 不变的边界

- 不把 `references_todo.bib` 当正式参考文献，也不把 `TODO_VERIFY` 改为 `VERIFIED`。
- 不改变 120 runs、118 falsified、2 budget_exhausted、120/120 artifact/checksum 和零错误计数。
- 不把 `budget_exhausted` 写成通过、安全或无漏洞。
- 不使用 Total calls 构造效率/加速结论。
- 不把 Harness 与 Original 写成完全等价，不把 static gate 写成 native replay。
- 不把 exercise2、matched-random-v1、V2 或 excluded internal candidates 并入当前 pooled 结果。

## 结论

C6 结论为：**可以进入 C7 正文精修与引用替换；不能最终投稿。** 当前最短路径是完成核心引用、图表和 venue 格式后进行窄定位投稿尝试；当前最稳路径是在此基础上再考虑 caller-controlled conditional replay 和独立 B5 benchmark。当前不建议直接运行 30 seed。
