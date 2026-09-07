# Figure / Table Plan

本文件只规划论文图表，不生成图片、PPT 或绘图产物。每项均指向仓库已有证据文件；最终图表应由研究者在 C5 根据版面和引用格式制作。

## Figure 1：PHS 方法总览图

- purpose：展示 safety property 输入如何经过 property-related state extraction、backward filtering、candidate construction、bounded repeat、lightweight value evidence、interpretable Top-K ranking，最终生成 Solidity wrapper Harness 并交给 Echidna 执行。
- data_source：方法定义与受控机制证据。
- source_file：paper-ready/v1/c1/claim_evidence_matrix.tsv；paper-ready/v1/c1/rq_evidence_map.tsv；paper-ready/v1/c1/evaluation_section_draft.md。
- fields_needed：property；相关状态变量；相关写入调用；候选 transaction sequence；repeat bound；value evidence；K；生成的 Harness；Echidna 参数 fuzz 边界。
- caption_draft：PHS 的 property-directed Harness synthesis 流程。PHS 在 Echidna 之前组织候选交易结构，参数仍由下游模糊执行。
- paper_location：4 方法开头。
- risk_or_caveat：不得画成新的 fuzzer core、完整符号执行器或自动安全证明器；需标注 K 是 Harness 条目数量。

## Figure 2：Property-directed sequence planning 流程图

- purpose：具体表现 property 相关状态提取到候选序列筛选和 Top-K 保留之间的逻辑关系。
- data_source：四个受控机制 benchmark 的机制标签与 C1 方法证据。
- source_file：paper-ready/v1/c1/evaluation_tables.md；paper-ready/v1/c1/evaluation_section_draft.md。
- fields_needed：Dependency、Property、Repeat、Value、Top-K 五类机制；输入函数集合；写读关系；重复上限；require/比较值线索；候选排名。
- caption_draft：从目标属性反向定位候选调用的示意流程；各机制在受控 benchmark 中分别承担可观察的证据角色。
- paper_location：4.2--4.7 方法小节之间，或作为 Figure 1 的展开图。
- risk_or_caveat：小型受控 benchmark 只说明机制可观察性，不代表公开生态中的普遍有效性。

## Figure 3：Original multi-transaction model 与 wrapper execution model 语义差异图

- purpose：并列展示 Original 多交易模型与 Solidity wrapper Harness 在 caller、atomicity、rollback、msg.value、block context、external calls/reentrancy 等方面的差异。
- data_source：语义边界审计与静态 replay gate。
- source_file：docs/v1-restart/SEMANTIC_BOUNDARY_AUDIT.md；paper-ready/v1/native_replay_gate.tsv。
- fields_needed：执行入口；交易边界；调用者来源；失败回滚范围；msg.value/context；外部调用与重入行为；native replay status。
- caption_draft：Original 多交易模型与 wrapper 执行模型的语义边界。两者用于不同实验配置，不能默认视为完全等价。
- paper_location：4.9 方法末尾和 7 有效性威胁。
- risk_or_caveat：图中不能用“等价”箭头；静态 replay gate 不应画成完整原生 EVM 回放。

## Figure 4：Provenance pipeline / artifact chain

- purpose：展示从输入、命令、环境到 raw、parsed、summary、status、checksum 的证据链。
- data_source：证据索引和主实验摘要。
- source_file：paper-ready/v1/evidence_index.tsv；paper-ready/v1/main10_results_summary.tsv；docs/v1-restart/PHASE_B4_CLOSEOUT.md。
- fields_needed：run_id；Git SHA；method；benchmark；seed；testLimit；timeout；command；environment；raw/parsed/summary/status 路径；checksum；完成状态。
- caption_draft：运行工件与派生结果的 provenance 链。该链用于审计记录完整性，不把工件完整性解释为属性安全性。
- paper_location：5 实现末尾或 6 评估 protocol。
- risk_or_caveat：应注明历史控制实验因 provenance 不完整被隔离；不要把 quarantine 结果画入主结果链。

## Table 1：Benchmark registry and semantic classification

- purpose：集中呈现实验对象、任务类型、纳入状态和语义注意事项。
- data_source：公开 benchmark registry 与 native replay gate。
- source_file：paper-ready/v1/public_benchmark_registry.tsv；paper-ready/v1/native_replay_gate.tsv。
- fields_needed：benchmark/task；source；分类；supported/conditional；属性；caller/msg.sender 依赖；replay gate；纳入 pooled 的理由。
- caption_draft：Benchmark registry 与语义分类。四个 supported public tasks 与 exercise2-access-control conditional task 分开列示。
- paper_location：6.1 实验对象。
- risk_or_caveat：不得把 conditional task 并入四个 supported public tasks；不得把 registry 当作生态代表性证明。

## Table 2：Controlled mechanism evidence

- purpose：汇总 Dependency、Property、Repeat、Value、Top-K 的受控机制证据。
- data_source：C1 evaluation tables 和 mechanism evidence。
- source_file：paper-ready/v1/c1/evaluation_tables.md；paper-ready/v1/c1/rq_evidence_map.tsv。
- fields_needed：benchmark；target property；mechanism；comparison configuration；observed outcome；runs；interpretation；scope.
- caption_draft：受控机制 benchmark 上的机制性观察。表中结果用于说明候选规划的可观察机制，不用于生态级性能结论。
- paper_location：6.2 受控机制实验。
- risk_or_caveat：不要添加显著性、p-value 或工具级 superiority；小样本和构造性基准必须在表注中说明。

## Table 3：10-seed public task result summary

- purpose：汇总三种方法、四个 supported public tasks、10 个 seed 的 120-run 描述性结果。
- data_source：主实验汇总和任务 registry。
- source_file：paper-ready/v1/main10_results_summary.tsv；paper-ready/v1/main10_results_summary.md；paper-ready/v1/public_benchmark_registry.tsv。
- fields_needed：method；benchmark；seed range 1--10；run count；falsified；budget_exhausted；artifact_complete；checksum_pass；parser/status mismatch；startup_error；unknown_error；incomplete；main_table_usable.
- caption_draft：四个受支持公开任务上的 120-run 描述性结果。Original、Full-K1 和 Full-K5 均使用 1--10 共 10 个 seed。
- paper_location：6.3 主结果。
- risk_or_caveat：118 falsified 与 2 budget_exhausted 是结果状态计数；budget_exhausted 不是属性通过或合约安全；main_table_usable 保持 conditional。

## Table 4：Allowed vs forbidden claims

- purpose：把论文可支持的窄定位与禁止外推的表述并列，帮助终稿审校。
- data_source：C1 claim-evidence matrix、paper decision 和 C3 claim audit。
- source_file：paper-ready/v1/c1/claim_evidence_matrix.tsv；paper-ready/v1/c1/paper_decision.md；paper-ready/v1/c3/style_and_claim_audit.md。
- fields_needed：claim id；allowed wording；supporting evidence；forbidden wording；reason；paper section.
- caption_draft：主张边界与证据对应关系。表中禁止项用于防止把描述性结果改写成普遍优越性或安全性结论。
- paper_location：可作为主文 Table 4，或放入补充材料。
- risk_or_caveat：这不是实验结果表；不能把“允许”解读成已完成独立复现或投稿级核验。

## Table 5：Threats and mitigations

- purpose：按 internal、external、construct、semantic、reproducibility、baseline comparison 分类呈现限制和缓解措施。
- data_source：C1 threats draft、semantic boundary audit、replay gate、registry。
- source_file：paper-ready/v1/c1/threats_to_validity_draft.md；docs/v1-restart/SEMANTIC_BOUNDARY_AUDIT.md；paper-ready/v1/native_replay_gate.tsv。
- fields_needed：threat type；threat；evidence or symptom；mitigation；remaining limitation.
- caption_draft：有效性威胁、已有缓解措施及仍然存在的限制。
- paper_location：7 有效性威胁。
- risk_or_caveat：不得把“记录了限制”写成“限制已被消除”。

## Appendix Table A1：Run-level 120-run details

- purpose：提供每一条主实验运行的可审计索引。
- data_source：主实验汇总、证据索引和运行工件索引。
- source_file：paper-ready/v1/main10_results_summary.tsv；paper-ready/v1/evidence_index.tsv。
- fields_needed：run_id；method；benchmark；seed；status；counterexample status；artifact completeness；checksum；parser/status check；error fields；source path.
- caption_draft：120 次运行的逐运行摘要与工件索引。
- paper_location：附录 A。
- risk_or_caveat：若源文件只有聚合字段，不能凭空展开缺失的 run-level 字段；应保留“未提供”并由人工补齐。

## Appendix Table A2：Expected run manifest

- purpose：列出每个运行应记录的输入、环境、命令和状态字段。
- data_source：B4 closeout、evidence index、仓库实验工作流约定。
- source_file：docs/v1-restart/PHASE_B4_CLOSEOUT.md；paper-ready/v1/evidence_index.tsv；docs/V1_EXPERIMENT_WORKFLOW.md。
- fields_needed：run_id；Git SHA；method version；contract/property/config/compiler/tool version；seed；testLimit；timeout；workers；stopOnFail；start/end time；status；input/output SHA-256.
- caption_draft：主实验的预期运行 manifest 字段，用于复现与审计。
- paper_location：附录 A。
- risk_or_caveat：这是记录规范，不是额外实验结果；不能以“字段齐全”替代语义验证。

## Appendix Table A3：Evidence index

- purpose：把正文 claims、结果表、审计文件和原始工件入口统一编号。
- data_source：evidence index。
- source_file：paper-ready/v1/evidence_index.tsv；paper-ready/v1/c1/rq_evidence_map.tsv。
- fields_needed：evidence_id；claim/rq；source_file；status；provenance note；allowed use；quarantine note.
- caption_draft：论文证据索引及其可用范围。
- paper_location：附录 A 或 artifact documentation。
- risk_or_caveat：evidence id 是仓库内部追踪标识；正式论文需转成稳定的表、附录或 artifact 链接。
