# Phase C1 Closeout：Paper-Ready Result Organization + Claim Synthesis

## 仓库状态

- 当前分支：develop
- 当前 HEAD：6cda747a29deda4048025a31c8219b0d82ea35b5
- 最近提交：6cda747 test: run V1 public supported 10-seed main
- 初始 WSL Git status：clean
- C1 过程未切换分支，未 reset、checkout、clean，未自动 commit 或 push。

## 阶段边界核验

- 本阶段是否运行实验：否。
- 是否运行 Echidna：否。
- 是否运行 10 seed：否；仅整理已有主运行证据。
- 是否运行 30 seed：否。
- 是否修改 results/ 或 frozen results：否。
- 是否修改 results/frozen/matched-random-v1：否。
- 是否使用 matched-random-v1：否；其 provenance unresolved，仍保持 quarantine。
- 是否新增 benchmark：否。
- 是否修改 benchmark source 或 analyzer 方法逻辑：否。
- 是否保留 semantic caveat：是；正文和表格均保留 wrapper/Original 的 caller、transaction atomicity、rollback、value/block/external-call 边界。

## 新增文件

### 制表脚本

- analyzer/build_c1_paper_ready_tables.py

脚本读取 paper-ready/v1/main10_results_summary.tsv、public_benchmark_registry.tsv 和 evidence_index.tsv，提供 --help、--check、--write。--check 不写文件；--write 只写 paper-ready/v1/c1/，不运行实验，不写 work/ 或 results/。

### paper-ready/v1/c1/

- rq_evidence_map.tsv
- claim_evidence_matrix.tsv
- evaluation_tables.md
- evaluation_section_draft.md
- threats_to_validity_draft.md
- paper_decision.md

其中 evaluation_tables.md 由脚本生成；RQ map 和 claim matrix 也由脚本生成。Evaluation、Threats to Validity 和投稿决策材料均只引用已读取的 V1 证据和 B4 summary。

## 结果一致性

B4 结果没有被改写或重新解释：

- 120 / 120 expected runs；
- 120 / 120 artifact sets complete；
- 120 / 120 checksum pass；
- parser/status mismatch = 0；
- startup_error = 0；
- unknown_error = 0；
- incomplete = 0；
- falsified = 118；
- budget_exhausted = 2。

两个 budget_exhausted 仍是 b4-echidna-multi-original-s1 和 b4-echidna-multi-full-k5-s7。它们表示在声明预算内没有观察到反例，不是 property passed、contract safe 或安全证明。所有分组行的 main_table_usable 仍为 conditional，没有改成 yes。

## 论文决策

允许进入 C2 论文初稿，但投稿主张必须窄。当前材料支持：

- V1 作为 Echidna 之上的 property-directed Harness synthesis preprocessing 的方法定位；
- 受控 Formal benchmarks 上 Property、Value、Repeat 和 Top-K 的机制性、范围内证据；
- 四个 supported public tasks 上 120-run 的完整 provenance 和描述性比较；
- 对 Harness wrapper 语义、conditional 任务和结果状态的明确边界说明。

当前不支持显著优于、Total calls speedup、Harness/Original 完全等价、budget_exhausted 等于通过或安全、四个任务代表真实生态，以及普遍优于 Echidna/SMARTIAN/MuFuzz/IR-Fuzz 的主张。

## 补强建议与阻塞项

- 不建议现在直接补 30 seed。
- 不建议现在硬做 SMARTIAN/MuFuzz/IR-Fuzz 工具级对比。
- 若要补强，优先补 2–4 个 public benchmark，或补 exercise2-access-control 的 caller-controlled appendix；后者至少比较 same-caller 与 alternating-caller，并保持 conditional。
- 对进入窄定位 C2 初稿没有阻塞项。
- 对更宽的生态泛化、工具级排名和等价/加速主张，阻塞项仍是 public benchmark 数量、native/caller-controlled replay、规模证据和可比外部基线。

## 人工复核

在进入正式论文提交前，研究者应复核四个 supported task 的 run-level 表、原始日志、checksum 和 semantic boundary。C1 产物当前是未提交的论文材料；复核后请自行选择性 git add、commit 和 push 到 develop。
