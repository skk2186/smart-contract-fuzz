# 轻量级状态值约束分析范围

## 当前支持

### 常量状态写入

- uint/int 十进制常量；
- 十六进制整数；
- address 常量；
- bool 常量；
- 简单显式类型转换中的常量。

示例：

- gate = 7；
- stage = uint8(1)；
- enabled = true。

### 简单 require 条件

- x == constant；
- x != constant；
- x > constant；
- x >= constant；
- x < constant；
- x <= constant；
- require(booleanVariable)；
- require(!booleanVariable)。

## 当前不支持

- 状态变量写入函数参数；
- 算术表达式写入；
- 多变量组合条件；
- mapping 和数组索引；
- 内部函数调用返回值；
- 哈希与加密运算；
- 跨函数符号传播；
- 跨合约状态约束；
- OR 条件和复杂嵌套布尔表达式。

## 设计原则

当前分析用于候选路径重排序，而不是完整证明路径可执行性。

对于无法识别的表达式，结果标记为 unknown，不直接删除对应路径，
以降低静态分析误判导致有效路径丢失的风险。
