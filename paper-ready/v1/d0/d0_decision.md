# D0 Decision

## 1. Is the current evaluation sufficient for a C-venue submission?

**Not yet sufficient; small B5 required.**

当前评价已经足以支撑窄定位投稿尝试的 scaffold：PHS 定位清楚，四个 Formal benchmark 提供机制证据，四个 supported public tasks 有完整 120-run provenance，且语义限制被明确记录。但若直接把它作为风险可接受的 C 会 regular research paper，reviewer 很容易指出三个缺口：public diversity 只有四个任务、118/120 造成最终 falsification 的 ceiling effect、以及缺少统一的 component ablation 和 target-rank/reachability 主指标。这里需要的是小型补强，不是顶会规模实验。

## 2. Do we start B5?

**YES — GO TO B5.**

本阶段的 YES 只表示启动 B5 的独立预登记与执行准备；本阶段没有运行实验，也没有把未运行的 B5 写入 V1 结果或论文表。

## 3. Recommended B5 package

Decision labels: 30-seed expansion = **NOT RECOMMENDED**; public benchmark expansion = **CONDITIONAL**; controlled/custom scenario expansion = **RECOMMENDED**; lightweight ablation = **RECOMMENDED**; second external baseline = **CONDITIONAL, not required**.

### Required

1. 新增 3 个 controlled/custom scenario：Irrelevant-State Explosion、Deep Repeated Transition、Value-Gated Competing Paths；诚实标为 controlled/custom/synthetic，不与 public pool 合并。
2. 做一个轻量组件 ablation：Original、Full、-Repeat、-Value，在竞争路径场景比较 K1/K5；若实现口径稳定，再加入 -Property/dependency-only control。
3. 将 target candidate rank、Top-K hit、target-state reachability、hard-scenario trigger success/time-to-falsify 和 seed stability 作为主轴；candidate reduction 和 preprocessing overhead 为辅助指标。
4. 每个新 scenario×method cell 推荐 10 seeds；不把现有 B4 全量扩成 30 seeds。新运行必须遵守独立 run directory、manifest、command、environment、raw、parsed、summary、status 和 checksum 协议。
5. Original Echidna 继续作为主实证 baseline；不把第二 external baseline 设为前置条件。

### Optional

- 通过独立 source/license/property/compiler/semantic gate 后新增 2 个 public benchmark，形成 B5-Strong；
- 对 exercise2-access-control 做 same-caller 与 alternating-caller 的 caller-controlled conditional replay，但结果继续单列；
- 仅对 B5 中最核心、最不饱和的 1–2 个 cell 做窄范围 seed/uncertainty 补强；
- 只有出现真正公平、低成本且可审计的实现时，才加入第二 executable baseline。

### Explicitly Not Recommended

- 当前全量 10→30 seed expansion；
- 为了数量强行复现 SMARTIAN、MuFuzz、IR-Fuzz、Harvey、ConFuzzius 或 SmarTest；
- 把 PUB06–PUB08、matched-random-v1、V2 或 conditional task 并入 supported pooled result；
- 继续增加与现有 Formal 同构且不能产生新指标的 toy；
- 使用 Original/Harness Total calls 直接声称 speedup，或把 budget_exhausted 写成 property passed/safe。

## 4. Main empirical baseline

**Original Echidna**。它最直接回答“在同一属性测试框架中，加上 PHS preprocessing 是否有价值”，并且是当前能公平说明、可执行和可追溯的比较对象。Full-K1/Full-K5 是 PHS 的配置敏感性，不是独立外部 baseline。

## 5. Primary evaluation dimensions / Main paper improvement dimensions

1. target candidate rank / Top-K hit；
2. target-state reachability；
3. hard-scenario time-to-falsify 或 fixed-budget trigger success；
4. seed-to-seed stability。

候选数量减少、repeat coverage、value-guided rank improvement 和 preprocessing overhead 作为 mechanism/secondary metrics。当前不能安全使用 Total calls speedup、pooled safety probability、跨语义模型等价或普遍 superiority。

## 6. Minimum Viable C-venue Path

保留当前 B4，增加 3 个非饱和 controlled/custom scenario 和轻量 ablation；用 10 seeds/新 cell 收集 rank、reachability、trigger/time 和 stability；以 Original Echidna 为主 baseline；完成后只做范围内、任务级、执行模型限定的机制和 public applicability claim。

## 7. Stronger C-venue Path

B5-Min 之外，再增加 2 个独立 public benchmark、exercise2 caller-controlled conditional appendix，以及对 1–2 个核心 cell 的窄范围 uncertainty 补强；不做全量 30 seeds，不强求第二 external baseline。

## 8. Go / No-Go judgment

**GO TO B5.**
