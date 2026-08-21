# 05 语义适用范围与威胁

## 语义审计

[`results/semantic-applicability/v1/`](../../results/semantic-applicability/v1/) 包含静态审计、人工复核、差分重放和 trace replay。当前 11 个目标中 10 个为 supported、1 个为 conditional；固定成功路径的属性相关最终结果差分重放为 11/11 一致。

## 必须在论文中披露的差异

当前 Harness 把候选函数顺序封装在一次外部 wrapper 调用中，而 Original 通过多笔独立交易生成序列。因此可能不同：

- 目标函数看到的 `msg.sender`；
- 多步调用是否处于同一笔交易；
- 中间调用回滚的范围；
- 每次外层调用包含的目标函数调用数。

因此结果描述的是当前 Harness 执行模型下的发现率，不是与 Original 完全等价的底层调用量加速。

## 对外主张边界

完整冻结矩阵见 [`results/paper-data/readiness-matrix.md`](../../results/paper-data/readiness-matrix.md)。CCF-C 差距和停止条件见 [`docs/CCF_C_GAP_ANALYSIS.md`](../../docs/CCF_C_GAP_ANALYSIS.md)。
