# C15 Word 与正向化生成说明

## 文件

- Markdown：paper-ready/v1/c15/c15_positive_supervisor_draft.md
- Word：paper-ready/v1/c15/c15_supervisor_draft.docx
- 审计：paper-ready/v1/c15/c15_ccfa_format_audit.md

## 生成方式

本轮读取并遵循 CCFA 人性化、通用产物契约、论文写作和文档生成技能说明。WSL 中没有可直接导入的 python-docx，因此 Word 使用 bundled Windows Python 环境和 python-docx fallback 生成；内容来自 C15 正向化 Markdown。结构检查通过。

## 转换范围与人工确认

已转换标题、摘要、关键词、一级/二级标题、正文、项目符号、引用占位文字和表 1。Markdown 的粗体、反引号和英文状态名按可读纯文本处理。已尝试使用文档技能的 render_docx.py 渲染，但当前环境缺少 LibreOffice soffice.exe，未产生 PNG/PDF；仍需在 Word/WPS 或具备 LibreOffice 的环境中确认页边距、页眉页脚、页数、字体、题注编号、交叉引用、流程图和正式参考文献。

本轮未修改 results/，未新增 benchmark、seed、baseline 或 Echidna run。是否继续新增实验：no。
