# C16 Word 复核说明

## 文件与生成方式

- Word 文件：paper-ready/v1/c16/c16_supervisor_draft.docx
- 内容来源：c16_strict_positive_supervisor_draft.md
- CCFA-skills：已读取并遵循 CCF 人性化、共同规范、论文写作与文档生成要求；当前 WSL 环境未提供可直接调用的 CCFA 专用排版命令。
- 生成方式：使用本机已验证的 Windows Python python-docx fallback，设置中文正文优先宋体、英数字体优先 Times New Roman，并对标题、摘要、关键词、层级标题、列表和表格设置基础样式。

## 复核状态

已完成 docx 非空检查、段落/表格/章节结构检查和核心数字检查。已尝试调用文档渲染工具；当前环境缺少可用的 LibreOffice soffice.exe，因此未生成页面 PNG/PDF 预览。建议在 Word/WPS 中人工确认页边距、分页、表 1 的宽度与换行、表题/交叉引用、参考文献格式和中文字体替换。

## 建议发给导师的文件

1. paper-ready/v1/c16/c16_strict_positive_supervisor_draft.md：可检索的正文版本。
2. paper-ready/v1/c16/c16_supervisor_draft.docx：可直接批注的导师版 Word。
3. paper-ready/v1/c11/claim_evidence_matrix.md：逐条 claim 与证据映射。
4. paper-ready/v1/c11/research_contract.md：论文定位、范围和禁用解释。
5. paper-ready/v1/c15/c15_ccfa_format_audit.md：既有格式审计输入。
6. results/per-property-isolation/summary.json：per-property isolation 的机器可读原始汇总。

## 实验决策

本阶段未新增实验，后续仍建议暂缓新增实验；当前优先级是导师对标题、引用核验、表格版式和执行模型表述进行确认。
