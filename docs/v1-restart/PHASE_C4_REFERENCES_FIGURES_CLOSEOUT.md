# C4 References, Figures, and Evidence Closeout

## 基线核验

- 当前分支：develop
- 当前 HEAD：8e30766994416e9eddad27a4c7da5c376a3f04e6
- 初始 git status --short：为空；工作区在 C4 开始时干净。
- 最新提交：8e30766 docs: revise V1 paper draft narrative

## 范围与安全检查

- 是否运行实验：否。
- 是否运行 Echidna：否。
- 是否运行 10 seed 或 30 seed：否。
- 是否修改 results/：否。
- 是否修改 frozen results：否。
- 是否修改 matched-random-v1：否；该证据继续保持隔离，不用于新主张。
- 是否新增 benchmark：否。
- 是否修改 B4 结果：否；120 runs、118 falsified、2 budget_exhausted 及其完整性计数保持不变。
- 是否联网：否。
- 是否发现本地 BibTeX：否；本地搜索未发现 .bib 或已核验 references 文件。

## 交付物

- 是否生成 citation slots：是，paper-ready/v1/c4/citation_slots.tsv，包含至少 20 个待核验槽位。
- 是否生成 references_todo.bib：是；全部条目使用 TODO_ key，并带 TODO_VERIFY note，不作为正式参考文献表。
- 是否生成 Related Work 修订计划：是。
- 是否生成 figure/table plan：是；仅规划，不生成图片或 PPT。
- 是否生成 terminology glossary：是。
- 是否生成 evidence crosswalk：是。
- 是否生成 citation markup full draft：是；基于 C3 修订稿插入 citation、table、figure 和 evidence slot，不改变实验数字和方法边界。
- 是否生成 C4 人工检查清单：是。

## 结论

本阶段完成了引用补全框架、BibTeX 占位、图表数据来源计划、术语统一和正文 claim/evidence 交叉引用。所有外部文献仍需研究者人工核验；当前材料没有把任何待核验候选写成已核实事实。

是否允许进入 C5：是，限于正文精修、正式引用替换、图表制作和交叉引用复核；在这些工作完成前，本文仍不是最终投稿稿。

## 阻塞项

1. 缺少经过原始来源核验的正式 BibTeX、DOI/URL 和引用位置。
2. 图表尚未按真实字段制作和人工视觉检查。
3. caller-controlled replay、Original/Harness 语义对齐和更公平的外部 baseline 仍属于后续工作。
4. 若要扩大 public benchmark 范围，需要另行提出并审核新的研究单元；不得在本阶段补入。

## C5 建议任务

1. 逐条核验 citation slots 并替换 references_todo.bib。
2. 根据 figure/table plan 生成 Figure 1--4、Table 1--5 和 Appendix A1--A3。
3. 在正文中完成 citation slot、table、figure、evidence id 的统一交叉引用。
4. 进行一次全稿数字、术语、forbidden claim 和语义边界审校。
5. 视研究计划决定是否另行开展 B5 public benchmark 扩展或 exercise2 caller-controlled appendix；两者均不得倒灌当前主结果。
