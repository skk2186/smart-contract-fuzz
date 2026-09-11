# 参考文献最终复核审计

## Registry 统计

- registry 总数：13
- verified：10
- high_confidence：2
- unresolved：1
- 正式 BibTeX 只包含 verified 或 high_confidence 条目，unresolved 条目不进入正式引用。

## high_confidence 条目

- ferreira2020smartbugs：SmartBugs: A Framework to Analyze Solidity Smart Contracts。需要在定稿前从 ACM/IEEE/DBLP 正式导出复核。
- qian2024mufuzz：MuFuzz: Sequence-Aware Mutation and Seed Mask Guidance for Blockchain Smart Contract Fuzzing。需要在定稿前从 ACM/IEEE/DBLP 正式导出复核。

high_confidence 不等于最终 verified。定稿前必须重新核验，不得补造 DOI、页码、会议或年份。

## unresolved 条目

- daedaluzz：Daedaluzz: A Benchmark Generator for Smart-Contract Fuzzers。当前不进入正式 BibTeX；需确认作者、年份、venue 和引用格式。

## 人工复核建议

- 使用 DBLP 核对作者顺序、会议和页码。
- 使用 ACM Digital Library 核对 ACM 论文的正式元数据与 DOI。
- 使用 IEEE Xplore 核对 IEEE 论文的正式元数据与 DOI。
- 使用 Google Scholar 辅助确认预印本与正式出版版本的对应关系。
- 使用作者主页或项目主页确认工具、仓库和 benchmark 的推荐引用格式。

本审计不新增文献，也不将 Daedaluzz 等 unresolved 项目写入正式 BibTeX。
