# 投稿准备 Checklist

## 论文基本信息

- [ ] 中文标题和英文标题含义一致，且不含内部工程编号。
- [ ] 摘要处于目标会议要求的长度范围，包含背景、问题、方法、实验和保守结论。
- [ ] 关键词覆盖 smart contract、multi-transaction fuzzing、explicit security property、state dependency 等核心概念。
- [ ] 作者、单位、基金和致谢信息完成匿名/非匿名版本切换。

## 正文与实验

- [ ] controlled evidence 作为主机制证据。
- [ ] adapted real-source evidence 作为补充边界检查。
- [ ] 真实来源明确写为 4 candidates、120 runs、80 usable/descriptive records、40 compile_error engineering rows。
- [ ] comparable subset 只包含两个 Echidna-origin candidates。
- [ ] SmartBugs Original-only 仅作描述。
- [ ] Harness compile_error 不进入比较结果。
- [ ] budget_exhausted 保留 right-censored 解释。
- [ ] 不以不同 execution model 的 Total calls 声称 speedup。
- [ ] 不出现 large-scale real-world evaluation 或 ecosystem-wide superiority 结论。

## 图表与参考文献

- [ ] 表 1–5 的主文/附录位置确定。
- [ ] 图 1–3 按目标模板重绘并完成图注。
- [ ] 表注说明 compile_error 排除、right-censoring 和执行模型差异。
- [ ] cite key 与 BibTeX 一致。
- [ ] high_confidence 条目完成定稿前复核。
- [ ] unresolved 文献未进入正式引用。

## Artifact 与合规

- [ ] artifact availability statement 已根据公开仓库和匿名评审要求调整。
- [ ] 不发布不必要的私人路径、用户名或本地环境信息。
- [ ] 不提交大型 raw artifact。
- [ ] ethics/security disclosure 已说明不进行真实攻击部署。
- [ ] 附录包含配置、受控任务、真实来源适配和工程排除项说明。
- [ ] 匿名审稿版本移除 GitHub 用户名、仓库链接、作者信息和本地路径。
- [ ] 代码、配置、结果摘要和分析脚本的公开方式经过研究者确认。
