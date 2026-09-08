# C6 Figure/Table Production Checklist

本清单把 C5 的输入规格转成制作和审图任务。C6 不生成图片、PPT、Mermaid 渲染物或 draw.io 文件；所有产物仍需后续人工制作、审图和按目标 venue 排版。

## Figures

### Figure 1 — PHS overview

- [ ] **应画什么：** `contract + explicit safety property -> state extraction -> read/write summary -> backward filtering -> candidate construction -> bounded repeat -> lightweight value evidence -> interpretable Top-K -> Solidity wrapper Harness -> Echidna parameter fuzz/property checking`。
- [ ] **数据来源：** `claim_evidence_matrix.tsv`、`rq_evidence_map.tsv`、`evaluation_section_draft.md`、`terminology_glossary.tsv`、`evidence_crosswalk.tsv`。
- [ ] **需要字段：** property、相关状态变量、相关写入调用、candidate sequence、repeat bound、value evidence、K、Harness 输出、Echidna 参数 fuzz 边界、provenance 旁路。
- [ ] **不应画什么：** 新的 fuzzer core、完整符号执行器、自动安全证明器、Echidna 替代品或 Original 等价交易长度。
- [ ] **人工检查点：** PHS/Echidna 边界清楚；`K` 标为 Harness candidate-entry count；value evidence 标为 lightweight；provenance 不被画成执行步骤。
- [ ] **Caption 草稿：** “PHS 的 property-directed Harness synthesis 流程。PHS 在 Echidna 之前组织候选交易结构并生成外部 Solidity wrapper Harness；参数 fuzz 和 property 执行仍由 Echidna 完成。”
- [ ] **制图方式：** Mermaid 或 draw.io 可用于内部审查；投稿版建议手工重绘为统一字体、线宽和颜色的矢量图。

### Figure 2 — Property-directed sequence planning

- [ ] **应画什么：** callable functions/raw dependency graph 经 property-read state set、Dependency candidates、Property filter、repeat-aware expansion、value match/conflict/unknown、ranking 到 Top-K candidate set 的逻辑。
- [ ] **数据来源：** `c1/evaluation_tables.md`、`c1/evaluation_section_draft.md`、`c1/rq_evidence_map.tsv`、C4 figure/table plan 和 terminology glossary。
- [ ] **需要字段：** 函数集合、读写关系、Dependency/Property retained paths、repeat bound、require/比较值线索、candidate rank、K、controlled-obstacle label。
- [ ] **可选标注数字：** `92 -> 31`、`NoisyFourStep 30 -> 3`、`BranchValue 0/30 vs 30/30`、`RepeatedCall 0/30 vs 30/30`；与 Table 2 对齐。
- [ ] **不应画什么：** 可达性证明、全局最优排名、效率/加速曲线、unknown 变成满足约束、无限重复。
- [ ] **人工检查点：** 五类机制的边界清楚；虚线到 NoisyFourStep、BranchValue、RepeatedCall、ResetExample 表示 evidence mapping，不表示同一运行串联。
- [ ] **Caption 草稿：** “Property-directed sequence planning 的机制分解。Dependency、Property、bounded Repeat、lightweight Value evidence 与 Top-K 对应受控障碍上的候选规划证据。”
- [ ] **制图方式：** Mermaid 适合内部审查；draw.io/手工矢量图适合投稿版。

### Figure 3 — Original vs wrapper execution model

- [ ] **应画什么：** Original 多笔独立交易时间线与 Harness 单次外层 wrapper 时间线，并并列标注 caller、transaction boundary、atomicity、rollback、msg.value/payable、block context、external call/reentrancy 和 address-keyed state。
- [ ] **数据来源：** `docs/v1-restart/SEMANTIC_BOUNDARY_AUDIT.md`、`native_replay_gate.tsv`、C4 evidence crosswalk、terminology glossary。
- [ ] **需要字段：** sender/caller 来源、caller alternation、失败回滚范围、static gate/native replay status、exercise2 conditional 标记。
- [ ] **不应画什么：** “equivalent” 双向箭头、same transaction length、same work、完整 native replay 或同 caller 结果对所有任务的普遍适用。
- [ ] **人工检查点：** wrapper 内多个目标调用不能被误画成多笔独立交易；exercise2 的 caller/address-keyed mapping 风险必须独立可见；static gate 必须标注为 static gate only。
- [ ] **Caption 草稿：** “Original 多交易模型与 wrapper 执行模型的语义边界。两者服务于不同实验配置，不能默认视为完全等价；当前 replay 记录是静态门控，不是完整 native EVM replay。”
- [ ] **制图方式：** draw.io 或手工绘制优先；Mermaid 仅用于先行审查。

### Figure 4 — Provenance pipeline

- [ ] **应画什么：** registry/input/environment -> manifest/command -> raw -> parsed -> summary -> status reconciliation -> SHA-256 checksum -> evidence index -> paper table 的证据链，并分出 quarantine 支路。
- [ ] **数据来源：** `evidence_index.tsv`、`main10_results_summary.tsv`、`main10_results_by_run.tsv`、B4 closeout、`docs/V1_EXPERIMENT_WORKFLOW.md`。
- [ ] **需要字段：** run_id、Git SHA、method/version、benchmark、property、seed、testLimit、timeout、workers、stopOnFail、command、environment、raw/parsed/summary/status、checksum、completed/status、evidence_id、quarantine note。
- [ ] **不应画什么：** 从 `120/120 artifact complete` 指向“结果正确”或“property passed”；不要把 checksum 画成安全验证；不要把 quarantine 接入主表。
- [ ] **人工检查点：** `main_table_usable=conditional` 保留；matched-random-v1 标为 `PROVENANCE_UNRESOLVED / DO_NOT_USE_FOR_NEW_CLAIMS`；Figure 4 字段与 Table 4 一致。
- [ ] **Caption 草稿：** “V1 运行工件与派生结果的 provenance 链。该链用于审计记录完整性和来源追踪，不等于属性安全、语义等价或独立复现。”
- [ ] **制图方式：** Mermaid 可表达 pipeline/quarantine；投稿版建议 draw.io/手工矢量图。

### Figure 5（可选）

- [ ] 默认不制作 Figure 5；若目标 venue 要求结果概览，只使用 Table 3 的 `falsified/runs` 描述性统计。
- [ ] 不显示 Total calls、显著性标记、效率/加速标记；图注保留 10-seed、四任务、budget_exhausted 和 conditional caveat。

## Tables

### Table 1 — Benchmark registry and semantic classification

- **数据来源：** `public_benchmark_registry.tsv`、`native_replay_gate.tsv`、C5 Table 1 draft。
- **字段：** benchmark ID/name、classification、property、declared path/goal、caller/address-keyed mapping、semantic risk、static gate/replay role、paper role。
- **位置：** 正文实验对象或 Dataset selection；详细 registry 可放附录。
- **风险：** PUB05 conditional 不得进入 PUB01--PUB04 pooled；PUB06--PUB08 excluded；static gate 不得写成 native replay；不能写成生态代表。
- **表注：** 只有 PUB01--PUB04 进入 120-run supported pool；`main_table_usable` 保持 conditional。

### Table 2 — Controlled mechanism evidence

- **数据来源：** `c1/evaluation_tables.md`、`c1/evaluation_section_draft.md`、C1 RQ mapping、C5 Table 2 draft。
- **字段：** benchmark/aggregate、mechanism/contrast、observed outcome、runs（若有）、allowed interpretation、scope boundary。
- **位置：** 正文机制评估；路径细节可放附录。
- **风险：** 92->31、30->3、0/30、30/30 是受控机制观察，不是效率、生态或工具排名证据。
- **表注：** controlled、purpose-built、mechanism evidence；不能把 Top-K 最高项写成全局最优。

### Table 3 — Public supported 10-seed results

- **数据来源：** `main10_results_summary.tsv`、`main10_results_by_run.tsv`、`public_benchmark_registry.tsv`。
- **字段：** benchmark、method、runs、falsified、budget_exhausted、observed falsification rate、artifact complete、checksum pass、parser/status mismatch、main_table_usable。
- **位置：** 正文主结果；120 行 run-level 明细放附录或复现包。
- **风险：** 只能作 descriptive comparison；不得改变 conditional；不得把 budget_exhausted 写成通过/安全；不得使用 Total calls 作跨模型工作量证据。
- **表注：** 四任务 × 三方法 × seeds 1--10 = 120；118 falsified、2 budget_exhausted；两个预算耗尽行需注明具体 task/method/seed。

### Table 4 — Provenance completeness and status audit

- **数据来源：** `main10_results_summary.tsv`、`main10_results_by_run.tsv`、`evidence_index.tsv`、B4 closeout。
- **字段：** expected/represented runs、artifact set、checksum、parser/status mismatch、startup_error、unknown_error、incomplete、seed scope、main-table flag、quarantine。
- **位置：** 正文可放简表；manifest/run-level 字段放附录。
- **风险：** 这是记录链审计表，不是安全性、语义一致性或独立复现证明。
- **表注：** `main_table_usable=conditional` 必须保留；matched-random-v1 不进入新主张。

### Table 5 — Allowed and forbidden claims

- **数据来源：** C1 claim-evidence matrix、C4 evidence crosswalk、C3 style audit、C5 decision/claim boundary。
- **字段：** claim class、allowed wording、forbidden wording/boundary、supporting evidence、section。
- **位置：** 正文可作为 claim-boundary table；也可放补充材料供审稿人和 artifact reviewer 查阅。
- **风险：** 这不是实验结果表；不能把 allowed wording 解释为独立复现已经完成。
- **表注：** “allowed” 只表示在声明范围内可写；citation、evidence 和 semantic caveats 仍需保留。

### Table 6 — Threats and mitigations

- **数据来源：** C1 threats draft、semantic boundary audit、replay gate、registry、C5 Table 6 draft。
- **字段：** threat type、threat、evidence/symptom、mitigation、remaining limitation、相关 Figure/Table。
- **位置：** 正文 Threats to Validity；可将完整字段放附录。
- **风险：** 记录威胁不等于威胁被消除；需保持 external validity、semantic validity、baseline limitation 和 quarantine。
- **表注：** 缓解措施回答“如何限制过度解释”，不把限制改写为结果保证。

## 制作完成条件

- [ ] 所有图表数字与 `main10_results_summary.tsv`、registry 和 evidence index 对齐。
- [ ] 所有 citation marker 仍为 marker，未被临时 TODO BibTeX 冒充正式引用。
- [ ] 图中没有等价、效率、加速或安全证明暗示。
- [ ] Figure 1--4 与正文 marker、Table 1--6 的编号在最终排版中一致。
- [ ] 正式图表制作后再运行一次禁用主张扫描；C6 本身不生成图片或 PPT。
