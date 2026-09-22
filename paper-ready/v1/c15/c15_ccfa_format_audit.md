# C15 CCFA 格式审计报告

## 技能与执行路径

本机搜索了仓库、WSL 用户目录和常见技能路径。WSL 中未发现可直接执行的 CCFA 命令包；在 Codex 主机 Windows 技能根目录中发现并读取了 ccf-humanization、ccf-common、ccf-paper-writer 及 documents 的技能说明和相关引用文档。本轮按其人性化、证据保留、canonical 输出目录和 python-docx 创建要求执行；结构检查已通过，渲染尝试因当前环境缺少 LibreOffice soffice.exe 而停止。

## 审计表

| 项目 | 结果 | 说明 |
|---|---|---|
| 标题 | PASS | 标题《面向显式安全属性的智能合约多交易序列规划》聚焦问题与方法。 |
| 摘要 | PASS | 含问题、方法链、per-property isolation 核心数字和证据范围；投稿版按模板进一步压缩。 |
| 关键词 | PASS | 已加入智能合约、显式安全属性、多交易序列、属性定向规划、状态依赖、Harness。 |
| 章节层级 | PASS | 摘要、引言、相关工作、问题定义、方法、实验、讨论、威胁、结论和适用范围层级清楚。 |
| 表格 | NEEDS_MINOR_TEXT_PATCH | per-property isolation 表已标为表 1；正式模板需统一题注位置和交叉引用。 |
| 图 | NEEDS_MINOR_TEXT_PATCH | 监督稿暂无图片；投稿版可补充方法流程图，本轮不新增证据。 |
| 参考文献 | NEEDS_MINOR_TEXT_PATCH | cite key 保留；SMARTIAN、ConFuzzius、Harvey、MuFuzz、IR-Fuzz、SmarTest 的正式元数据需定稿前核验。 |
| 内部阶段痕迹 | PASS | C13/C14 等内部编号未进入 C15 正文。 |
| 英文术语 | NEEDS_MINOR_TEXT_PATCH | 保留变量、状态和方法名所需英文；投稿版统一首次释义与大小写。 |
| 否定边界句式 | PASS | 边界改写为证据范围、状态分类、执行模型和独立验证需求。 |
| Claim 审计 | PASS | 数字与边界回溯到 C11 evidence matrix、research contract 和 summary.json。 |

## Word 版式

Word 初稿包含标题、摘要、关键词、Heading 1/2、正文、项目符号和表 1；结构检查已通过。中文正文优先使用宋体，英文和数字使用 Times New Roman；表格含表头样式和可读列宽。

需要人工确认：投稿模板页边距、页眉页脚、页数、中文字体替换、表题和图题编号、参考文献条目、方法流程图位置，以及在具备 LibreOffice 或 Word/WPS 的环境中完成最终视觉渲染检查。

## 结论

C15 适合作为导师审阅初稿。图形补充、引用元数据、投稿模板设置和一次可用环境中的视觉渲染检查属于定稿工作，不构成新增实验理由。
