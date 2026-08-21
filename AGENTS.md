# Agent instructions for smart-contract-fuzz

本仓库用于智能合约状态依赖引导模糊测试研究。当前最重要的原则是：先保证 V1 证据可追溯，再开展新增实验；V2 只能作为独立开发线，不能覆盖或混入 V1 结论。

## 开始任何任务前

按以下顺序阅读：

1. docs/START_HERE.md
2. docs/DIRECTORY_GUIDE.md
3. paper-ready/00_PROJECT_SUMMARY.md
4. paper-ready/FREEZE_STATUS.md
5. 本文件和 docs/V1_EXPERIMENT_WORKFLOW.md

如果用户要求运行某个实验，先用一句话说明：研究问题、输入、输出目录、是否会重新运行 Echidna/Slither/solc，以及是否会产生新文件。一次只推进一个可检查的实验单元。

## 版本边界

- V1/Full-v1.0 是当前稳定研究线，包含 Dependency、Property、Repeat、Value、Top-K 和 Harness 生成。
- results/formal/、results/formal-b2/、results/public-benchmarks/c1/、results/paper-data/ 中已有的正式日志、CSV、manifest、checksum 和审计文件视为冻结证据。
- analyzer/v2/、V2/native-corpus/C2 开发材料是独立线。不能把它们的结果写入 V1 表格，也不能把 V2 结果与 V1 运行结果 pooled。
- 不为了“填满结果表”而增加合成合约、删除失败运行或修改纳入规则。

## 文件写入规则

### 允许直接修改

- 方法实现：analyzer/（但必须增加版本号或记录提交 SHA）
- 实验配置：configs/
- 执行脚本：scripts/
- 合约和 Harness 模板：contracts/
- 研究说明：docs/

### 新实验的临时输出

所有新增运行首先写入被 Git 忽略的：

    work/v1-restart/<run_id>/
      manifest.tsv
      command.txt
      environment.txt
      generated/
      raw/
      parsed/
      summary/
      status/

也可以使用 results/_work/<run_id>/，但不能直接把新日志写入已经冻结的 results/formal/*/runs/、results/public-benchmarks/c1/runs/ 或 results/paper-data/。

临时 Harness、JSON、CSV 和日志先保存在该运行目录中；只有在用户明确确认并完成回归检查后，才将经过筛选的代码或派生结果提升到正式目录。原始日志不能手工编辑。

每个运行目录必须记录：

- run_id、Git commit SHA、方法版本；
- 合约、属性、配置、编译器和工具版本；
- seed、testLimit、timeout、workers、stopOnFail；
- 实际命令和开始/结束时间；
- completed、startup_error、unknown_error 等状态；
- 输入文件和关键输出的 SHA-256。

## 路径和脚本规则

- 脚本必须从脚本位置解析仓库根目录，不能依赖某个旧工作区的绝对路径。
- 新脚本优先使用 bash scripts/resolve_repo_root.sh 获得根目录。
- 运行前检查当前路径、Git 分支和工作区状态。
- 派生 CSV 使用固定重建脚本生成，禁止手工改表。
- 运行脚本前先确认它是“重建派生结果”还是“会启动模糊测试并写日志”。

## Git 和安全规则

- 不使用 git add .、git add -A、git reset --hard 或大范围删除。
- 只提交用户明确要求的路径；混合工作区先列出并确认归属。
- 不覆盖、移动或删除冻结证据；需要归档时先生成清单和 checksum，并保留可恢复路径。
- 不在一次操作中同时修改算法、实验口径和结果表。
- 若方法代码发生变化，旧结果必须保留原方法版本，不得默认为新代码重新解释旧日志。

## 保持用户理解

Codex 可以代跑命令，但不能把实验变成黑箱。每个阶段都要告诉用户：

1. 这条命令验证什么；
2. 输入文件中哪些字段会影响结果；
3. 输出文件如何阅读；
4. 结果支持什么结论、不能支持什么结论；
5. 下一步是否需要用户亲自复核。

budget_exhausted 不能写成“属性通过”；Original 与 Harness 的交易语义、调用者和回滚边界差异必须在解释中保留。
