# C19 投稿前自检报告

## 检查结果

- 是否新增实验：no。未运行 Echidna、Slither 或 solc，未新增 benchmark、seed、baseline 或 Echidna run。
- 是否修改 `results/`：no。C19 只写入 `paper-ready/v1/c19/`。
- 是否仍像技术文章：no。正文保持论文体，按研究问题、方法、证据层级、结果和有效性威胁组织；未回退为脚本说明或工程日志。
- 是否仍有大量工程字段：no。未发现 `property_function`、`value_matches`、`value_conflicts`、`--max-function-visits`、`--max-expansions` 等工程字段回流正文。
- 是否仍有大量英文夹杂：no。普通叙述已保持中文，仅保留必要的工具名、函数名、状态名、方法名和文献元数据。
- 是否仍有重复参考文献标题：no。正文末尾只保留一个“参考文献”章节。
- 是否仍有 Markdown cite key：no。未发现 `[@xxx]` 或裸 cite key；正文引用使用编号格式。
- 是否已生成 Word：yes。已生成 `c19_submission_precheck_draft.docx`，内容来源为 C19 清理版 Markdown；结构检查通过。自动页面级渲染因环境缺少 `soffice.exe` 未完成。

## 仍需人工完成的事项

1. 在 Word 或 WPS 中进行页面级确认，重点检查中文字体替换、表格分页、表题、参考文献换行和 `[10]`、`[11]` 的可见性。
2. 在定稿前核验 IR-Fuzz 和 SmarTest 的完整元数据；MuFuzz 和 SmartBugs 仍建议按 C18 清单进行正式记录复核。
3. 由导师或作者确认论文题目、摘要、关键词、引用格式和最终投稿模板要求。

上述事项不需要新增实验，也不改变 C19 已保留的实验数字和结果结论。

