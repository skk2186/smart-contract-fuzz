# C5 Figure Input Specifications

本文件是制图输入规格，不生成图片、PPT、Mermaid 渲染物或 draw.io 文件。所有图都需要人工审图；图中的数字、术语和箭头语义必须与 C1/C4 evidence crosswalk、terminology glossary 和 C5 tables 对齐。

## Figure 1. PHS overview

### 目的

展示显式 safety property 如何经过属性相关状态提取、反向筛选、候选构造、有界重复、轻量值证据和可解释 Top-K 排序，最终生成 Solidity wrapper Harness，并交给 Echidna 继续探索参数与属性。

### 输入文件

- `paper-ready/v1/c1/claim_evidence_matrix.tsv`
- `paper-ready/v1/c1/rq_evidence_map.tsv`
- `paper-ready/v1/c1/evaluation_section_draft.md`
- `paper-ready/v1/c4/terminology_glossary.tsv`
- `paper-ready/v1/c4/evidence_crosswalk.tsv`

### 需要字段

`property`、property 读取的状态变量、相关写入调用、候选 transaction sequence、repeat bound、value evidence、K、生成 Harness、Echidna 参数 fuzz 边界、PHS/Echidna 的接口位置。

### 节点/框图元素

1. Solidity contract + explicit safety property
2. Property-related state extraction
3. Read/write summary
4. Backward filtering of relevant writes
5. Candidate transaction-sequence construction
6. Bounded repeat expansion
7. Lightweight value evidence
8. Interpretable Top-K ranking
9. Solidity wrapper Harness synthesis
10. Echidna parameter fuzzing + property checking
11. Audited raw/parsed/status/provenance outputs（可作为旁路输出）

### 箭头关系

`contract + property -> state extraction -> read/write summary -> backward filtering -> candidate construction -> bounded repeat -> value evidence -> Top-K -> wrapper Harness -> Echidna`。

从候选构造、排序和 Harness 生成节点分别引出一个虚线箭头至 `candidate metadata / provenance`，表示可追溯记录，不表示额外运行阶段。

### Caption

**Figure 1.** PHS 的 property-directed Harness synthesis 流程。PHS 在 Echidna 之前组织候选交易结构并生成外部 Solidity wrapper Harness；参数 fuzz 和 property 执行仍由 Echidna 完成。

### Caveat

不得画成新的 fuzzer core、完整符号执行器、自动安全证明器或 Echidna 替代品。必须标注 `K = Harness candidate-entry count`，不要画成 Original 等价交易长度；`value evidence` 必须标注 lightweight。

### 可用制图方式

Mermaid 或 draw.io 均可；正式论文版建议手工重绘为统一字体、线宽和颜色的矢量图。

### 后续人工审图

需要。重点检查 PHS/Echidna 分界、property 输入位置、Top-K 含义、wrapper 输出和 provenance 旁路是否被误读为同一执行器内部步骤。

## Figure 2. Property-directed sequence planning

### 目的

展开 Figure 1 中的候选规划逻辑，具体表现 Dependency、Property、Repeat、Value 和 Top-K 五类机制如何从函数集合与读写关系产生候选序列。

### 输入文件

- `paper-ready/v1/c1/evaluation_tables.md`
- `paper-ready/v1/c1/evaluation_section_draft.md`
- `paper-ready/v1/c1/rq_evidence_map.tsv`
- `paper-ready/v1/c4/figure_table_plan.md`
- `paper-ready/v1/c4/terminology_glossary.tsv`

### 需要字段

函数集合、读写关系、property 相关状态、Dependency retained paths、Property retained paths、重复上限、require/比较值线索、candidate rank、K、controlled benchmark 标签。

可在图旁用现有受控数字作小标签：`92 -> 31`、`NoisyFourStep 30 -> 3`、`BranchValue Property-K1 0/30 vs Value-K1 30/30`、`RepeatedCall no-repeat 0/30 vs Full 30/30`。若版面不允许，数字放 Table 2，不重复画成性能曲线。

### 节点/框图元素

1. All callable functions / raw dependency graph
2. Property-read state set
3. Dependency candidates
4. Property-related backward filter
5. Repeat-aware expansion
6. Value evidence match/conflict/unknown
7. Interpretable ranking
8. Top-K candidate set
9. Controlled-obstacle annotation：noise、value direction、repeat、reset/tie

### 箭头关系

`callable functions + property reads -> dependency candidates -> property filter -> repeat expansion -> value match/conflict -> ranking -> Top-K`。

从每个机制框引出一条到对应 controlled benchmark 的短虚线：`NoisyFourStep`、`BranchValue`、`RepeatedCall`、`ResetExample`。虚线表示 evidence mapping，不表示 benchmark 在同一运行中串联执行。

### Caption

**Figure 2.** Property-directed sequence planning 的机制分解。Dependency、Property、bounded Repeat、lightweight Value evidence 与 Top-K 分别对应受控障碍上的候选规划证据；这些观察不代表公开生态中的普遍有效性。

### Caveat

不能把候选保留画成可达性证明；不能把排名最高画成全局最优；不能把候选数减少画成 fuzzing 加速；unknown 条件必须保留为 unknown，不得画成满足约束。

### 可用制图方式

Mermaid 适合内部审查，draw.io 或手工矢量绘制适合投稿版。若放入论文，建议把数字与 Table 2 保持一致并在图注中写“controlled mechanism evidence”。

### 后续人工审图

需要。检查五类机制是否被画成可互换模块、Repeat 是否被误解为无限展开、Value 是否被误解为符号求解、Top-K 是否被误解为最优性证明。

## Figure 3. Original vs wrapper execution model

### 目的

并列展示 Original multi-transaction model 与 Solidity wrapper execution model 的语义差异，为结果解释和 conditional benchmark 分类提供可视化边界。

### 输入文件

- `docs/v1-restart/SEMANTIC_BOUNDARY_AUDIT.md`
- `paper-ready/v1/native_replay_gate.tsv`
- `paper-ready/v1/c4/evidence_crosswalk.tsv`
- `paper-ready/v1/c4/terminology_glossary.tsv`

### 需要字段

执行入口、交易边界、caller/msg.sender 来源、caller alternation、失败回滚范围、transaction atomicity、msg.value/payable、block.timestamp/block.number、external call/reentrancy、constructor/deployer、address-keyed state、native replay status/static gate status。

### 节点/框图元素

左列 Original：多笔独立交易、可能变化的 sender、单笔失败回滚、独立 value/block context、外部调用栈。

右列 Harness：一次外层 wrapper 调用、目标函数通常由同一 Harness caller 发起、wrapper 内连续调用、可能整体回滚、当前无通用逐步 msg.value/不同 sender 模拟。

中间或底部增加 `static gate only` 标识，以及 `conditional: exercise2-access-control` 标识。

### 箭头关系

用两条平行的时间线：

- Original：`tx1 -> commit/rollback(tx1) -> tx2 -> commit/rollback(tx2) -> ... -> property`。
- Harness：`outer wrapper tx -> call A -> call B -> ... -> commit/rollback(wrapper) -> property`。

不要使用双向“等价”箭头。可用虚线从每个差异字段指向 `interpretation risk`，例如 caller -> access control risk、rollback -> failed-prefix risk、context -> time/value/reentrancy risk。

### Caption

**Figure 3.** Original 多交易模型与 wrapper 执行模型的语义边界。两者服务于不同实验配置，不能默认视为完全等价；当前 replay 记录是静态门控，不是完整 native EVM replay。

### Caveat

图中不能使用 `equivalent`、`same transaction length` 或 `same work`。`Full-K1`/`Full-K5` 的 K 只表示 Harness 条目数量。exercise2 的 caller/address-keyed mapping 风险必须单独标注，不得被四个 supported tasks 的箭头覆盖。

### 可用制图方式

draw.io 或手工绘制优先，因为需要对齐双时间线和差异注释；Mermaid 可用于先行审查，但投稿版建议改为矢量图。

### 后续人工审图

必须。由熟悉 Solidity 调用者、revert/rollback 和 `msg.sender` 语义的研究者复核，尤其检查是否把 wrapper 内多个目标调用误画成多笔独立交易。

## Figure 4. Provenance pipeline

### 目的

展示从输入和预登记配置到 raw、parsed、summary、status、checksum 与 evidence index 的证据链，说明完整性审计的对象和边界。

### 输入文件

- `paper-ready/v1/evidence_index.tsv`
- `paper-ready/v1/main10_results_summary.tsv`
- `paper-ready/v1/main10_results_by_run.tsv`
- `docs/v1-restart/PHASE_B4_CLOSEOUT.md`
- `docs/V1_EXPERIMENT_WORKFLOW.md`

### 需要字段

`run_id`、Git SHA、method/method version、benchmark、property、seed、testLimit、timeout、workers、stopOnFail、command、environment、raw/parsed/summary/status 路径、checksum、completed/status、evidence_id、quarantine note。

### 节点/框图元素

1. preregistration / registry
2. contract + property + config + compiler/tool environment
3. command and manifest
4. raw log
5. parsed result
6. grouped summary
7. status reconciliation
8. SHA-256 checksum
9. evidence index / paper table
10. quarantine branch for unresolved legacy control

### 箭头关系

`registry + input + environment -> manifest/command -> raw -> parsed -> summary -> status reconciliation -> checksum -> evidence index -> Table 3/Table 4`。

从 `matched-random-v1` 以红色或虚线箭头进入 `quarantine`，并在图中注明 `PROVENANCE_UNRESOLVED / DO_NOT_USE_FOR_NEW_CLAIMS`。不要把 quarantine 箭头接入主表。

### Caption

**Figure 4.** V1 运行工件与派生结果的 provenance 链。该链用于审计记录完整性和来源追踪；artifact complete、checksum pass 和零解析错配不等于属性安全、语义等价或独立复现。

### Caveat

不要从 `120/120 artifact complete` 画出“结果正确”或“property passed”箭头。必须区分原始日志、派生汇总和 evidence index；`main_table_usable=conditional` 应在表格出口处保留。

### 可用制图方式

Mermaid 可表达 pipeline 和 quarantine 分支；正式版可用 draw.io/手工矢量图增加文件层级、审计门和红色 quarantine 分支。

### 后续人工审图

需要。检查每个节点是否有真实来源文件、quarantine 是否与主结果隔离、checksum 是否被误画成结果验证，以及 Figure 4 与 Table 4 的字段名称是否一致。

## Figure 5（可选）：Result summary visual

本阶段不把 Figure 5 纳入必需制作清单。若目标 venue 需要一张结果概览图，可以使用 Table 3 的四个 benchmark × 三种 method 的 `falsified/runs`，采用分组点图或小型热图。

若采用，输入只能是 `paper-ready/v1/main10_results_summary.tsv`，需要字段为 `benchmark_name`、`method`、`runs`、`falsified`、`budget_exhausted`、`falsification_rate` 和 `main_table_usable`。图注必须写明：这是 10-seed、四任务范围内的描述性统计，`budget_exhausted` 不是通过，`main_table_usable` 仍为 conditional；不得显示 Total calls，不得添加显著性标记或效率/加速标记。

建议使用手工绘制或 Vega/矢量图；必须由人工确认两次 budget_exhausted 的位置与 Table 3 一致。若版面不足，优先保留 Figure 1--4，删除 Figure 5。
