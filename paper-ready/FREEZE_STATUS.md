# 2026-08-06 实验冻结状态

## 冻结结论

本次冻结以 Full-v1.0 为论文主方法，Formal、B-2、C-1 为主证据，matched-random、语义差分和 SMARTIAN 两目标批次为控制或附录证据。V2、smoke、C0、历史pilot和无完整 provenance 的 overhead-v2 不进入 V1 主结论。

## 已同步状态

- 六个合成目标：Full-K1 180/180，Original 171/180；
- 五个 C-1 公开目标：Full-K5 149/150，Original 144/150，Full-K1 120/150；
- matched-random：87/270，配对 Full-K1 为240/270；
- 语义审计：10 supported、1 conditional；固定成功路径重放11/11一致；
- SMARTIAN：2个已对齐整数目标、每目标30次，60/60完成并发现IntegerBug；
- C2新增公开候选：0；
- 规模证据：当前11个目标为32–79行、retained paths为1–33，仍不足以证明大型真实合约可扩展。

## 文件与环境冻结

- `paper-ready/manifest.tsv`：论文证据角色和唯一来源；
- `results/paper-data/input-checksums.sha256`：所有白名单主文/附录输入的逐文件SHA-256；
- `results/paper-data/repository-files.tsv`：除主仓库`.git/`和两个自引用输出外，工作区全部普通文件的路径、大小、SHA-256和范围分类；
- `results/paper-data/repository-freeze.json`：文件计数、总体摘要、本地.NET版本和SMARTIAN提交；
- Git冻结提交与本地tag：项目管理范围的权威快照。

本地工具链、SMARTIAN嵌套仓库及其Git元数据、Python缓存、历史checkpoint和可重建生成物会进入全工作区inventory，但不作为论文证据，也不重复提交到主仓库。

本次盘点记录24,188个普通文件、1,147,013,923字节；其中项目管理范围14,485个文件。本地.NET版本为8.0.423，SMARTIAN固定提交为`eca1ed1d60c88ec5402055a05b59174b7288264c`。具体分类和总体digest以 `repository-freeze.json` 为准。

## 已知边界

- Harness单交易wrapper与Original多交易执行仍有调用者、原子性和回滚边界差异；
- SMARTIAN结果只覆盖两个简单整数属性，不能写成广泛SOTA排名；
- `results/formal/overhead-v2/` 虽有结构完整的960行数据，但缺少可证明一次性完整执行的completion marker，继续排除；
- 当前公开任务仅5个、C2新增任务为0，因此冻结的是当前阶段证据，不是完整CCF-C论文出口。
