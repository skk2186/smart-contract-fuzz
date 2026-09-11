# PHASE C8 References and Tables

## 阶段状态

PASS。参考文献 registry、正式 BibTeX、待核验清单、五个表格草案、三张图规划和带引用/表图占位的论文副本均已生成。起始工作区 clean，本阶段未启动实验。

## 起始状态

- 起始分支：develop
- 起始 HEAD：98141898ef0094e0559326aab291c50b71c92d2c
- 上一提交：exp: C7 draft integration
- 起始工作区：clean

## 输入与输出

输入为既有 C7 论文材料、B5-6 派生 TSV 和 results/paper-data/synthetic-six-benchmark-summary.csv。输出为 paper-ready/v1/draft 下的引用、表格、图规划、带引用初稿和带表图占位初稿，以及本报告。

## 参考文献核验结果

registry 总数 13；verified 10；high_confidence 2；unresolved 1。正式 BibTeX 含 12 条，仅含 verified 或 high_confidence；unresolved 的 Daedaluzz 元数据留在待核验清单。

## 表格生成情况

表 1 覆盖六个受控场景；表 2 从 12 个机器可读配置行生成，每行分母 30，formal-main 与 B-2 分开。表 3 保留 4 candidates、120 runs、80 usable/descriptive、40 excluded engineering rows。表 4 仅将两个 Echidna-origin candidates 的六个 cells 视为 comparable；SmartBugs Original-only 仅描述，40 条 Harness compile_error 仅作 engineering limitation。表 5 汇总威胁与缓解措施。

## 边界与下一步

- 是否新增实验：NO。
- 是否修改旧证据：NO。
- 是否纳入 exercise2：NO。
- 是否出现 forbidden claims：NO。
- controlled evidence 与 adapted real-source evidence 保持分层。
- budget_exhausted 只写为 right-censored。
- Original and Harness are distinct execution models。
- compile_error 不进入 comparative outcomes。
- Decision: GO_TO_C9_FULL_DRAFT_POLISH。

## 当前最薄弱之处

SmartBugs/MuFuzz 高置信度元数据仍需官方导出复核；表 2 的 calls-to-failure 在源摘要中不存在而保留为“—”；B-2 环境快照不完整，最终应决定其主文或附录位置。当前证据不要求本阶段补充真实来源数量。
