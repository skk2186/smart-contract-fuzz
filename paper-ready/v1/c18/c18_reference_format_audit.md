# C18 参考文献格式审计

## 统计

- 原始 C18 学术稿中的 citation key 数量：12 个引用出现，12 个唯一 key。
- 已转换为编号引用的数量：12 个编号条目，正文中共 8 处编号引用位置。
- 已有完整 BibTeX 或 registry 信息的条目：10 个。
- 待核验引用数量：2 个，分别为 IR-Fuzz 和 SmarTest。
- 疑似伪造引用：未发现。10 个完整条目均来自仓库已有 BibTeX/registry；2 个缺失条目被明确标记为待核验。
- [@xxx] 残留：规范稿中应为 0。
- 裸 cite key 残留：规范稿中应为 0；论文正文只保留文献名称和编号。

## 编号映射

| 编号 | 文献 | 当前状态 |
|---:|---|---|
| [1] | Echidna | registry verified |
| [2] | ContractFuzzer | registry verified |
| [3] | sFuzz | registry verified |
| [4] | ILF | registry verified |
| [5] | QuickCheck | registry verified |
| [6] | Harvey | registry verified |
| [7] | ConFuzzius | registry verified |
| [8] | SMARTIAN | registry verified |
| [9] | MuFuzz | registry high_confidence，定稿复核 |
| [10] | IR-Fuzz | 待核验 |
| [11] | SmarTest | 待核验 |
| [12] | SmartBugs | registry high_confidence，定稿复核 |

## 后续人工核验

优先核验 IR-Fuzz 和 SmarTest 的完整元数据与引用上下文；随后从 IEEE Xplore/ACM/DBLP 复核 MuFuzz 和 SmartBugs 的作者顺序、出版信息和 DOI。C18 未使用仓库外检索结果，也未编造缺失字段。
