# RepeatedCallExample 当前方法限制

## 正确漏洞序列

deposit()
→ deposit()
→ unlock()
→ withdraw(uint256)

其中 deposit() 必须重复执行两次。

## 当前路径生成结果

普通状态依赖和 Property-guided 分析均能够识别：

- deposit 写入并读取 depositCount；
- unlock 读取 depositCount；
- withdraw 最终写入属性变量 value。

但是当前 DFS 为避免循环，不允许同一个函数在一条路径中重复出现，
因此无法生成正确的重复调用序列。

Property+Value 方法只能对已有候选路径进行重排序，不能恢复在路径
生成阶段被遗漏的序列。

## 对照验证

手工构造的重复调用 Harness 可以触发属性失败：

deposit → deposit → unlock → withdraw

而只调用一次 deposit 的 Harness 无法触发属性失败。

## 结论

当前方法对简单无环交易序列有效，但不能处理需要重复调用同一函数
才能推进状态的漏洞场景。后续需要加入有界重复调用支持，同时控制
循环路径导致的候选空间膨胀。
