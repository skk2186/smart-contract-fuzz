# 相对于 C8 初稿的主要修改

## 摘要

将摘要重写为“背景—问题—方法—证据—结论”结构，直接交代 controlled evidence 与 adapted real-source evidence 的分工，并保留 180/180、171/180、4 candidates、120 runs、80 usable/descriptive records 和 40 compile_error engineering rows 等关键口径。

## 引言

压缩状态空间爆炸和普通状态依赖分析的重复说明，强化“显式安全属性提供目标状态语义”这一动机。贡献收束为四条可验证的研究贡献，不再写成文件或流水线清单。

## 方法章节

统一术语为显式安全属性、属性相关变量、状态读写依赖、条件约束匹配、状态值方向匹配、有界重复和 Top-K 候选序列。补充“排序提供优先级而非可执行性保证”和“方法不是完整静态证明”的边界。

## 实验章节

明确 controlled evidence 是主机制证据，adapted real-source evidence 是补充证据。保留 4 candidates、120 runs、80 usable/descriptive records、40 compile_error engineering rows，单独解释 comparable Echidna-origin、SmartBugs Original-only 和 right-censored 分层。

## 讨论与有效性威胁

将真实来源实验定位为适用边界检查，明确 SmartBugs Harness 的 Solidity 0.4.25 import-path compile_error 是工程限制而非检测失败。保留 Original and Harness are distinct execution models，并禁止由 Total calls 推导 speedup。

## 参考文献与图表占位

保留 C8 cite keys、BibTeX 和 unresolved 清单，新增正文中的表 1–5、图 1–3 引用位置。没有把 Daedaluzz 未核验元数据写入正式引用。

## 没有改动的证据边界

没有新增实验、没有重跑 fuzzing、没有修改任何原始结果或冻结证据、没有纳入 exercise2、没有改变 120 条真实来源记录的 80/40 分层，也没有把 compile_error 或 budget_exhausted 改写为方法性能结论。
