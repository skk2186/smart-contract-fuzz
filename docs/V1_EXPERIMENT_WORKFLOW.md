# V1 实验工作流

本文档用于解决两个实际问题：实验运行产生大量文件，以及代理在错误目录中创建或覆盖文件。它不改变已有 V1 结果，只规定从现在开始的新增实验如何运行。

## 1. 三个区域

| 区域 | 作用 | Git 策略 |
|---|---|---|
| 源码区 | analyzer/、contracts/、configs/、scripts/ | 代码和配置可审查、可提交 |
| 运行区 | work/v1-restart/<run_id>/ | 临时输出，默认忽略，不进入论文表 |
| 证据区 | 已冻结的 results/、paper-ready/ | 只读；派生数据只能由固定脚本重建 |

不要把“运行区”和“证据区”混用。运行时产生的日志、临时 Harness、JSON、中间 CSV、编译导出和启动记录都放在运行区。

## 2. 运行目录协议

建议使用如下命名：

    v1-YYYYMMDD-<benchmark>-<method>-s<seed-range>

例如：

    work/v1-restart/v1-20260821-noisy-full-k1-s1-3/

目录内至少包含：

    manifest.tsv       # 本次运行的唯一声明
    command.txt        # 实际执行命令，逐行记录
    environment.txt    # 工具版本、OS、Python/Conda环境
    generated/         # 本次生成的Harness、路径JSON、值约束JSON
    raw/               # 原始标准输出/错误输出，不手工修改
    parsed/            # 由解析器生成的逐运行数据
    summary/           # 由固定脚本生成的汇总
    status/            # 完成标记、错误分类和校验值

manifest.tsv 至少包含：

    run_id
    commit_sha
    method_version
    benchmark
    contract_file
    contract_name
    property
    config_file
    compiler
    seed
    test_limit
    timeout
    workers
    stop_on_fail
    output_root

## 3. 一次实验的生命周期

### A. 预登记

在运行前固定：

- 研究问题和假设；
- 合约清单、属性、方法组和 Top-K；
- Solidity/solc、Echidna、Slither 版本；
- seed 范围、预算、timeout、workers、stopOnFail；
- 成功、预算耗尽、启动失败和未知失败的定义；
- 哪些文件进入主结果、附录或排除项。

不能先看结果，再改变合约清单、K、预算或排除规则。

### B. 生成

把读写分析、属性路径、重复路径和值约束的输出写入 generated/。先检查：

- 属性读取的状态变量是什么；
- 候选边和路径数量如何变化；
- Top-K 路径是什么；
- 是否包含必要重复调用；
- 是否存在值约束冲突或 UNKNOWN；
- Harness 是否只包含声明的候选路径。

### C. 编译预检

编译本次生成的 Harness，并把编译器输出写入 raw/ 或 status/。编译失败要区分：

- 源码/依赖失败；
- 编译器版本失败；
- Harness 生成失败；
- 方法没有生成候选路径。

编译失败不能静默地从分母中删除。

### D. 小规模回归

新增算法或配置第一次运行时，只执行一个基准、1–3 个 seed。先确认输出和旧 V1 的口径一致，再扩大到 30 seed。不要直接启动全量批次。

### E. 正式运行

正式运行必须：

- 固定 commit SHA；
- 使用预登记的 manifest；
- 每个 seed 单独保存原始日志；
- 写入明确完成标记；
- 中断后可安全续跑；
- 不覆盖已完成且带完成标记的运行；
- 保留 startup error、unknown error 和 budget exhausted。

### F. 派生和提升

解析、汇总、统计必须由固定脚本完成。只有满足以下条件，才允许把运行区结果提升为论文证据：

1. 运行目录完整；
2. 输入和输出 checksum 可复核；
3. 失败运行没有被删除；
4. 方法版本与旧结果明确区分；
5. 结果表由脚本重建；
6. 论文主张没有超出证据。

## 4. V1 重启的推荐顺序

1. 只读检查冻结 V1 代码、配置和环境；
2. 用 NoisyFourStep 跑 1 个 Original 和 1 个 Full-K1 seed；
3. 人工阅读 rw.json、属性路径 JSON、Full JSON、生成 Harness 和两份日志；
4. 再对四个 Formal 主基准各跑 3 个 seed；
5. 若候选路径、编译和日志口径一致，再决定是否跑 30 seed；
6. 之后再做公开基准，不要同时修 V2；
7. 公开任务正式运行前，先冻结纳入表、属性、适配补丁和排除原因；
8. 最后再做统计和论文表。

这条顺序的目的不是追求更多日志，而是先恢复用户对每个实验对象和结论的掌控。

## 5. 允许写出的结论

V1 可以围绕以下问题组织：

- 属性相关过滤是否减少与目标属性无关的候选路径？
- 值约束是否能纠正仅按变量依赖排序产生的错误 Top-1？
- 有界重复是否能覆盖必须多次调用同一函数的路径？
- Full-K1/K5 在预声明的公开属性任务上是否比 Original 更稳定？
- matched-random 是否说明收益来自候选池内部排序，而非任意 Harness 化？
- Harness 的支持范围和语义限制是什么？

不要把以下内容当作已证实结论：

- V1 普遍优于所有智能合约模糊器；
- 候选路径减少必然带来端到端加速；
- Harness 与 Original 的多交易语义完全等价；
- 1050 次运行等于 1050 个独立合约；
- V2 的开发结果已经支持论文主张。

## 6. V1/V2 出口条件

V2 只有同时满足以下条件才允许进入新的正式比较：

- 六个 V1 回归基准的正确路径仍可生成；
- RepeatedCall 的必要重复没有被错误删除；
- AlternativePath 的多条可行路径没有被错误合并；
- MultiProperty 的两个属性仍分别可验证；
- 新方法相对 V1 有预先声明的可测改进；
- 语义适用性没有扩大到当前 Harness 不支持的范围；
- 新结果有独立目录、独立方法版本和独立 manifest。

如果 V2 不能满足这些条件，它仍然可以作为未来工作或失败分析保留，但不应阻塞 V1 论文线。
