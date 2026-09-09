# B5 Options

## 1. Evaluation scale

下表的成本和价值是相对等级，不是新的实验结果。semantic risk 表示新增工作自身引入的语义错配风险，不表示当前 V1 证据已经失败。

| option | reviewer value | scientific value | implementation cost | execution cost | semantic risk | expected claim improvement | C-venue ROI |
|---|---|---|---|---|---|---|---|
| B5-A: No additional experiment | low | low | low | low | low | 只能保留窄定位、描述性和机制 claim | low |
| B5-B: 全量 10→30 seeds | medium | medium（只改善同一 cell 的波动描述） | low | high（当前 B4 约增加 240 runs） | low | 不能增加 benchmark diversity、baseline 或机制指标；只能让现有描述更细 | low-medium |
| B5-C: 新增 2–4 public benchmarks | high（若来源和模式真正多样） | high | medium-high | medium-high | medium-high（每个新任务要过 semantic gate） | 显著改善 external validity、property pattern diversity 和 reviewer perception | high |
| B5-D: controlled/custom scenario expansion | medium-high | high（直接测机制） | medium | medium | low-medium（可显式控制 caller/atomicity） | 改善 rank、reachability、repeat/value/noise 机制 claim，不能独立证明生态泛化 | high |
| B5-E: lightweight ablation | high | high | low-medium | medium | low | 直接回答 Property/Repeat/Value/Top-K 各自贡献，降低 engineering-glue 风险 | high |
| B5-F: second external baseline | medium（仅在公平时） | medium-high（若能严格对齐） | high | high | high | 可改善 comparative positioning，但也可能制造不可比结果和额外审计负担 | low-medium |
| B5-G: B5-Min 组合 | high | high | medium-high | medium-high | low-medium | 同时补机制归因、非饱和指标和少量外部效度；不追求全面工具竞赛 | highest |

## 2. Option-by-option assessment

### B5-A：No additional experiment

可以进入正文和窄定位投稿准备，但 reviewer 最大的攻击点会集中在“只在小样本和饱和结果上观察到差异”“没有统一 ablation”“4 个 public task 不足以支持外部效度”。它适合时间极端受限的 short-paper attempt，不是风险可接受的 regular C-venue package。最大的优点是零实验成本，科学增益最低。

### B5-B：30-seed expansion

30 seeds 会增加同一任务/属性/配置内的波动描述和区间精度，但不会增加独立 contract/property 数量、不会引入第二 executable baseline、不会修复 Harness/Original 语义差异，也不会消除 118/120 的 ceiling effect。当前同样预算优先投入 2 个新 public task，或 3 个可产生 rank/reachability/trigger 差异的 controlled scenario，reviewer value 更高。因此不推荐当前全量扩展。

### B5-C：2–4 public benchmark expansion

这是降低 external-validity 风险的最直接方式，前提是新增任务来自独立来源、具有不同的 state dependency/require/value/repeat pattern，并完成 license、source closure、property、compiler、adaptation 和 semantic gate。当前 B1 在仓库已有材料中没有发现合格新增 source，所以此选项只能在外部 acquisition 后条件性执行；不得把 PUB06–PUB08 改名纳入。若找到 2 个高质量任务，10 seeds/task-method cell 已足够先形成 B5-Strong，不必同步扩到 30。

### B5-D：controlled/custom scenario expansion

这是当前最适合 PHS 的机制补强方式。建议构造但在 D0 不创建源码：C1 Irrelevant-State Explosion、C2 Deep Repeated Transition、C3 Value-Gated Competing Paths，C4 Noise+Repeat+Value 作为可选组合。所有场景必须标为 controlled/custom/synthetic，预先固定目标 skeleton、预算、成功定义和不纳入规则。它们可以成为论文核心 mechanism layer，而不是为了掩盖 public 数量不足的替代品。

### B5-E：lightweight ablation

这是最便宜且最直接降低 reviewer risk 的实验：Original、Full、-Repeat、-Value，并在竞争路径场景上比较 K1/K5；若口径稳定，再加入 -Property 或 dependency-only control。已有 Formal 组件数据可以被复核和引用，但不能把不同历史预算的结果机械拼成一次新的 factorial 实验。B5 应用固定方法版本、统一指标和独立运行目录重新形成可读的组件归因。

### B5-F：second external baseline

不建议为了表格数量强行加入。SMARTIAN、MuFuzz、IR-Fuzz、Harvey、ConFuzzius 或 SmarTest 只有在实现公开、环境可控、oracle/property、caller、transaction model、budget 和输出定义公平对齐时，才有资格成为 executable baseline。当前仓库的 SMARTIAN 仅有两个简单整数目标，不能升级为广泛排名；其余方法没有足够的公平复现基础。它们应继续作为 literature positioning，除非未来出现低成本且可审计的对齐方案。

### B5-G：组合方案

推荐的组合是 B5-Min = B5-D + B5-E：3 个更深、更难、非饱和的 controlled/custom scenario，加一个轻量组件 ablation；保留 B4 四个 public task 和 Original 主 baseline，不做全量 30 seeds，不强求第二 external baseline。B5-Strong 在此基础上再加 2 个真正独立的 public benchmark、exercise2 的 caller-controlled conditional replay，以及只针对最核心 1–2 个 cell 的窄范围 seed/uncertainty 补强。

## 3. Ranking

1. **最推荐：B5-G（B5-Min）**——最直接闭合 PHS 的机制归因和非饱和指标缺口，成本仍可控。
2. **次推荐：B5-E + B5-C（满足独立来源和语义门控时）**——若能快速获得 2 个高质量 public task，external-validity 增益很高。
3. **可选：B5-D 单独执行**——当时间只能补机制证据时可采用，但要承认 public diversity 仍是限制。
4. **条件性：B5-F**——只有存在真正公平、低成本、可追溯的第二工具实现才做。
5. **不推荐：B5-B 全量 30-seed expansion**——对当前最主要 reviewer 风险的改善最少。
6. **最低成本但高风险：B5-A**——可投稿尝试，但不应被当作 D0 的推荐出口。

## 4. Decision implication

B5 不应修改任何冻结结果，也不应把新结果写进当前 B4 表；新运行必须使用独立的 work/v1-restart/<run_id>/ provenance 协议，之后再由固定脚本生成派生结果。D0 只决定路线，不执行这些实验。
