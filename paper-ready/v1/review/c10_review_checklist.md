# 导师审阅 Checklist

## 研究定位

- [ ] 选题是否像 C 会论文，而非单纯工程工具报告。
- [ ] 标题是否准确体现“显式安全属性”和“多交易序列生成”。
- [ ] 摘要是否同时交代问题、方法、主实验和证据边界。
- [ ] 是否明确 controlled evidence 是主机制证据。

## 方法与创新

- [ ] 属性相关变量、状态读写依赖和反向切片是否定义清楚。
- [ ] 条件约束匹配、状态值方向匹配、有界重复和 Top-K 候选序列是否形成连贯方法。
- [ ] 创新点是否成立，是否需要进一步避免与既有 data-flow/sequence fuzzing 工作重叠。
- [ ] 是否避免声称完整静态证明或所有路径都能恢复。
- [ ] 原生执行与 Harness 执行边界是否表述充分。

## 实验与结果

- [ ] baseline 是否合适，相关论文是否最终选定。
- [ ] controlled evidence 是否足以作为主实验。
- [ ] 六个受控场景的任务障碍和分母是否清晰。
- [ ] adapted real-source evidence 是否表述克制。
- [ ] 4 candidates、120 runs、80 usable/descriptive records、40 compile_error engineering rows 是否分层正确。
- [ ] B-2 结果放主文还是附录。
- [ ] 真实来源数量是否需要继续补充。
- [ ] 是否没有把 compile_error 当作比较失败或性能结果。
- [ ] 是否没有把 budget_exhausted 当作安全或通过。
- [ ] 是否没有把 Total calls 写成 speedup。

## 表格、引用与投稿

- [ ] 表格是否清晰，主文与附录的分工是否合理。
- [ ] 图表是否符合目标会议模板的尺寸、字体和编号规范。
- [ ] high_confidence 文献是否需要再次导出核验。
- [ ] unresolved 文献是否未进入正式 BibTeX。
- [ ] 是否需要替换或补充 baseline 引用。
- [ ] 是否需要改英文标题或英文摘要。
- [ ] artifact availability、ethics/security disclosure 和匿名投稿说明是否完整。
