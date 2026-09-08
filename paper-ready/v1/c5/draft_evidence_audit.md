# C5 Draft Evidence Audit

审计对象是 `paper-ready/v1/c4/full_draft_citation_markup.md`，并与 C3 完整稿、C3 评估稿、C1 claim/RQ mapping、C4 evidence crosswalk、terminology glossary 和已有表格草稿交叉核对。`TODO_VERIFY` 表示本地没有正式核验引用；它不是引用已完成。

| section | claim_or_issue | evidence_status | citation_status | risk | recommended_fix |
|---|---|---|---|---|---|
| 摘要 | PHS 是 Echidna 之前的外部 property-directed preprocessing；报告 120 runs、118 falsified、2 budget_exhausted、120/120 artifact/checksum 和零错误状态 | E06_PHASE04_METHOD_POSITIONING、E20_PHASE_B4_MAIN10_RUN、E22_MAIN10_RESULTS_SUMMARY；数字与主表一致 | Echidna 背景没有正式 citation；CIT-001/002 为 TODO_VERIFY；摘要当前没有可解析的正式 citation marker | 中 | 正式引用放在引言/背景；摘要保留本地结果和预算解释，复核所有数字与 Table 3/4 一致 |
| 1 引言 | 状态依赖、多交易序列和 property-based fuzzing 是问题背景；PHS 作为外部 Harness synthesis 方法 | 方法定位由 E06 支持；语义边界由 E11 支持；公共范围由 E14 支持 | 有 `CITE:STATEFUL_FUZZING`、`CITE:ECHIDNA`、`CITE:ECHIDNA_DOC`，但均未映射到正式 key；CIT-001--004 TODO_VERIFY | 中 | 建立 marker-to-slot/key 映射；核验 Echidna、Harvey、ConFuzzius 来源；避免把一般背景写成 PHS 首创 |
| 2 背景 | safety property、状态读写、transaction sequence、wrapper/Original 差异、Top-K、bounded repeat 和 lightweight value evidence 的定义 | E06 支持方法边界；E11 支持 wrapper/Original 差异；术语由 glossary 支持 | `CITE:SMARTIAN`、`CITE:STATEFUL_FUZZING`、`CITE:SMARTEST`、`CITE:SYMBOLIC_ANALYSIS` 存在语义 marker，但 C4 slots 只有部分一一对应；CIT-005/006/010/011/012 TODO_VERIFY | 中 | 统一 citation marker；核验 SMARTIAN、SmarTest、Mythril、Oyente；明确 value evidence 不等于符号执行 |
| 3 动机 | NoisyFourStep 30->3、BranchValue 0/30 vs 30/30、RepeatedCall 0/30 vs 30/30、Reset 排序观察 | E05_PHASE03_FORMAL_MECHANISM；C1 evaluation material 和 Table 2 草稿支持这些受控观察 | 主要是本地 benchmark claim，不必用相关工作 citation 替代；若说明一般 stateful fuzzing 背景，需 CIT-003/026 | 低-中 | 在表注中写 controlled、purpose-built 和非生态证据；不得把候选减少写成效率结论 |
| 4 方法 | PHS workflow：state extraction -> backward filtering -> candidate construction -> bounded repeat -> value evidence -> Top-K -> wrapper | E06_PHASE04_METHOD_POSITIONING；Figure 1/2 由 E06 和方法材料支持 | 主要本地方法描述；Echidna interface 相关句子仍需 CIT-001/002；当前 figure markers 需要转为正式编号 | 低 | 保持“外部预处理层”定位；在 Figure 1/2 与术语表中统一 `K = Harness 条目数量` |
| 5 实现 | manifest、command、environment、raw、parsed、summary、status、checksum 形成 provenance；budget_exhausted 不是通过 | E20/E21/E22 和 docs/V1_EXPERIMENT_WORKFLOW 支持；E10 支持 quarantine | artifact/reproducibility 背景仍是 CIT-021/022/028 TODO_VERIFY；本地数字不缺证据 | 中 | 补正式 artifact/reproducibility 来源；Table 4 仅描述记录完整性，不写安全或独立复现证明 |
| 6 实验评估 | 4 supported tasks × 3 methods × seeds 1--10 = 120；118 falsified、2 budget_exhausted；120/120 artifact/checksum；零 parser/status/startup/unknown/incomplete | E14 registry、E20/E21/E22 summary、E11 semantic boundary；与 `main10_results_summary.tsv` 对齐 | 主要是本地证据；benchmark 来源和 static gate 背景需要 CIT-018/019/023/025；markup 中 Table markers 尚需最终编号 | 低-中 | 使用 Table 1/3/4；保留 `main_table_usable=conditional`；明确 observed rate 不是安全率，不使用 Total calls |
| 6.4 结果解释与语义限制 | Original 多交易与 wrapper execution model 在 caller、atomicity、rollback、msg.value、block context、外部调用和 reentrancy 上有差异；static gate 不是 native replay | E11_HARNESS_SEMANTIC_BOUNDARY、E15_PHASE_B2_NATIVE_REPLAY_GATE、E14 registry | `FIG:SEMANTIC_BOUNDARY` 和 `TABLE:CLAIM_BOUNDARY` 已有，但 replay/caller 规范来源 CIT-025 TODO_VERIFY | 中 | Figure 3 标注差异而非等价；exercise2 继续 conditional；补官方 replay/语义来源或删去规范性背景句 |
| 7 有效性威胁 | 构造性 benchmark、四个 public tasks、条件性 exercise2、wrapper 语义、static gate、matched-random quarantine 和外部 baseline 缺口 | E10、E11、E14、E15、E20；C1 threats draft 支持 | 主要限制由本地证据支持；artifact/reproducibility 和 benchmark 来源仍 TODO_VERIFY | 低 | 保留 remaining limitation；不要把“已记录威胁”写成“威胁已消除”；Table 6 与正文同词 |
| 8 Related Work | Echidna、Harvey、ConFuzzius、SMARTIAN、IR-Fuzz、MuFuzz、SmarTest、Mythril、Oyente、ILF、ContractFuzzer、sFuzz、EthPloit、SmartBugs/Curated、Daedaluzz 和 artifact guidance 的定位 | 只有 C01/C04 claim boundary 与 E06/C04 local positioning；相关工作事实本身没有本地 evidence | 28 个 citation slots 全部 TODO_VERIFY；markup 中多个 `CITE:*` marker 尚未与 slot/key 对齐；这是当前最大引用风险 | 高 | 逐条人工核验原始论文/官方/benchmark 来源；补正式 BibTeX；在核验前不要提交最终 Related Work |
| 9 结论 | 结论窄定位为机制证据、可审计的 120-run 描述性比较和语义边界；未来工作含更多 benchmark、caller-controlled replay 和公平 baseline | E05、E06、E11、E20/E22；C1 paper decision 支持 | artifact/evidence reporting 的背景引用 CIT-028 TODO_VERIFY；结论数字可由本地表格支持 | 低-中 | 维持“不能支持更宽效果推断”；正式投稿前补 CIT-028 或删除一般性 artifact 方法学句 |

## 交叉问题

1. **Citation marker 不能直接作为正式引用。** C4 markup 中的 `[CITE:...]` 是定位标记，不是 BibTeX key；尤其 `CITE:ECHIDNA_DOC`、`CITE:SYMBOLIC_ANALYSIS`、`CITE:STATEFUL_FUZZING` 等需要建立明确映射或改写。
2. **Evidence ID 与 claim boundary 要分开。** `E06_PHASE04_METHOD_POSITIONING` 是有效 evidence id；`C01_CLAIM_BOUNDARY` 和 `C04_CLAIM_BOUNDARY` 是 claim-evidence matrix 标记，不应当冒充 evidence index id。
3. **正文数字目前对齐。** 主运行数字为 120、118、2、120/120、0 parser/status mismatch、0 startup_error、0 unknown_error、0 incomplete；Table 3 应继续从 `main10_results_summary.tsv` 读取，不从 markup 手工改写。
4. **术语总体一致但需终稿复核。** PHS、safety property、transaction sequence、wrapper execution model、Original multi-transaction model、bounded repeat、lightweight value evidence、budget_exhausted、falsified、provenance、checksum、conditional task 和 static gate 应按 glossary 固定写法。
5. **目前没有发现正文把 budget_exhausted 写成通过或安全。** 相关禁用词在 C3/C4 中都出现在否定、审计或限制语境；仍需在最终排版稿重新扫描。

## 审计结论

C3/C4 draft 可以进入 C6 正文精修。正式投稿仍被引用核验、最终图表人工制作/审图和全文交叉引用一致性阻塞；这些阻塞不要求本阶段运行实验，也不改变 B4 结果。
