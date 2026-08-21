# Formal-B2 provenance 与分母

现存150份日志均明确记录：

- `FORMAL_EXPERIMENT_VERSION=Full-v1.0`；
- `FORMAL_BATCH=B-2`；
- benchmark、method、seed、合约和配置路径；
- `FORMAL_B2_RUN_COMPLETED=1`。

Formal-B2 没有独立的环境快照。因此无法由当前证据恢复或确认实际使用的 Echidna、Slither 和 solc 二进制构建版本，也不得根据 Formal 主批次环境事后猜填。运行级汇总以 `environment_snapshot_status=missing_independent_snapshot` 明确记录这一限制。

AlternativePath 的分母是一组30次运行；一次运行发现目标属性反例即为成功。

MultiProperty 每种方法有30次运行，每次运行产生两个指定属性结果，即每种方法60个 property outcomes。运行级成功要求两个属性在同一次运行中均产生反例。`both_properties_failed` 是运行级复合指标，不是第三个属性，也不能把60个属性结果写成60次独立运行。
