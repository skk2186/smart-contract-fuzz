# C5 Forbidden Claim Scan

## 扫描范围与方法

扫描范围为 `paper-ready/v1/c3/` 和 `paper-ready/v1/c4/` 的 Markdown/TSV/BibTeX 文本，覆盖用户指定的禁用词与工具级比较词。WSL 环境没有 `rg`，本次使用递归固定字符串/正则文本搜索完成只读扫描；未修改被扫描文件。

本扫描区分：

- **论文主张**：正文以肯定句把禁用内容作为本文结论或结果解释；这是问题。
- **否定/限制语境**：正文明确说“不能”“不支持”“不是”，或出现在 glossary、checklist、crosswalk、threats、forbidden wording 中；这不算问题。
- **相关工作待核验名称**：SMARTIAN、MuFuzz、IR-Fuzz 等作为 citation candidate 出现；本身不是工具级优越主张。

## 扫描结果

| 禁用项 | 发现位置/语境 | 是否为论文主张 | 风险判断 |
|---|---|---|---|
| 显著优于 | C3 style audit、C4 crosswalk、evaluation/claim boundary 中以否定或禁止写法出现 | 否 | PASS |
| 普遍优于 | C3 style audit、C4 crosswalk 和限制段落中以否定或禁止写法出现 | 否 | PASS |
| `speedup` / 加速 | C3/C4 明确说不使用 Total calls 作 speedup/加速证据；glossary/checklist 也作禁止项 | 否 | PASS |
| 完全等价 | C3/C4 只用于否定 Original/Harness 等价或说明禁止写法 | 否 | PASS |
| `property passed` | 用于定义 `budget_exhausted` 不是通过；出现在否定句、术语表或 checklist | 否 | PASS |
| `contract safe` | 用于说明 budget_exhausted 不是安全结论 | 否 | PASS |
| 安全证明 | C4 图表 caveat 和方法边界中明确说不提供安全证明 | 否 | PASS |
| 无漏洞 | 仅在否定预算耗尽含义或 forbidden wording 中出现 | 否 | PASS |
| 真实生态代表 | C3/C4 明确说四个任务不代表真实生态 | 否 | PASS |
| 大规模真实合约 | 仅作为未来规模评估或限制语境，未作为当前结果主张 | 否 | PASS |
| 修改 Echidna core | 正文表述为“不修改 Echidna core”；C4 计划把“修改”列为禁止主张 | 否 | PASS |
| 新的通用模糊测试器 | 相关语义只用于否定 PHS 是新的完整/通用 fuzzer；未作为贡献声称 | 否 | PASS |
| 30 seed | 未发现把 30 seed 写成当前 C5/B4 结果；`30/30` 仅是受控机制运行计数，不是 30-seed 主批次 | 否 | PASS |
| SMARTIAN/MuFuzz/IR-Fuzz 工具级优越 | 只作为相关工作候选或明确声明“未完成工具级比较”；没有正向优越性句 | 否 | PASS |

## 需要人工保持的边界

- C4 `related_work_revision_plan.md`、`citation_slots.tsv` 和 `references_todo.bib` 中有大量工具名称和禁止写法，这是审计材料，不是论文主张。
- C3/C4 正文中关于 `property passed`、`contract safe`、speedup、生态代表性和 Original/Harness 等价性的出现均为限制说明；最终排版稿仍应再做一次扫描。
- 受控结果中的 `0/30`、`30/30` 是每个机制对照的运行计数，不能被表述为新的 30-seed 公开实验。

## 最终结论：PASS

未发现禁用内容作为论文允许主张写入 C3/C4 正文。扫描通过；正式引用缺口、图表审图和最终交叉引用仍是独立的投稿阻塞项，不改变本次 forbidden-claim 扫描结论。
