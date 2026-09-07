# 5 Implementation（中文草稿）

## 5.1 输入与处理组件

实现输入包括 Solidity 合约及其依赖、显式 Echidna safety property、编译器和 Echidna 配置，以及候选 Top-K 和重复访问上限。V1 的分析管线由状态读写提取、基础依赖序列生成、属性相关序列生成、重复感知序列生成、值约束提取、值引导排序和 Harness 生成组件组成。方法版本和输入路径必须写入运行 manifest，不能用新方法版本重新解释旧日志。

处理器依次生成读写摘要、候选路径 JSON、值约束记录和 K1/K5 Harness。runner 负责预检、编译、执行、原始日志留存、解析和汇总。Original 使用 Echidna 的 Original multi-transaction model；Harness 方法使用固定候选的 wrapper execution model。两者的调用层次和语义边界必须同时记录。

## 5.2 provenance 与状态分类

每个运行目录保留 manifest.tsv、command.txt、environment.txt、generated/、raw/、parsed/、summary/、status/ 和 checksum 文件。manifest 至少记录 run id、commit SHA、方法版本、benchmark、property、配置、编译器、seed、testLimit、timeout、workers、stopOnFail 和输出根目录。command 与 environment 分别记录实际命令、开始/结束时间和工具版本；raw 保留不可手工编辑的原始输出，parsed/summary 由固定程序生成。

运行状态分为 falsified、budget_exhausted、startup_error、unknown_error 和 incomplete。falsified 表示观察到属性反例；budget_exhausted 表示在声明预算内没有观察到反例，不等于 property passed、contract safe 或漏洞不存在。启动错误、未知错误和不完整运行不能从分母中静默删除。parser/status mismatch 是阻塞项，必须在提升为论文证据前解决。

## 5.3 可复现性与 quarantine

runner 在生成、编译和执行阶段保留输入与关键输出的 SHA-256，并通过逐运行 checksum 审计检查产物是否仍与记录一致。固定配置、工具版本、seed 和方法版本使后续人工复核可以从结果摘要回到原始日志。新实验即使未来获准，也必须使用独立运行目录，不能覆盖冻结 evidence。

results/matched-random-v1/ 保持 provenance unresolved、DO_NOT_USE_FOR_NEW_CLAIMS 和 legacy control quarantine 标记。本稿不使用它的新数字，不将其与四个 supported public tasks pooled。相同原则适用于 V2、smoke、C0 和没有完整 provenance 的历史材料。完整产物链回答的是“证据是否可追溯”，不回答合约是否安全。
