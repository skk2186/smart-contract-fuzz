# BranchValueExample 同分路径排序验证

## 观察结果

Property-guided 方法生成的正确路径为：

prepareGood()
→ unlock()
→ activate()
→ trigger(uint256)

该路径原始排名为第 5。

## 验证一：调整函数声明顺序

仅将 prepareGood 在 Solidity 源码中的声明位置移动到其他
prepareBad 函数之前，不修改函数名称。

重新生成候选路径后，正确路径排名不变。

说明 Solidity 源码声明顺序不是当前路径排名的主要决定因素。

## 验证二：调整函数名称

修改 prepareGood 的函数名称，使其字典序排在 prepareBad
函数之前。

重新生成候选路径后，正确路径排名发生变化。

## 结论

多个候选路径具有相同的路径长度和依赖得分时，当前实现无法使用
状态语义区分这些路径。最终顺序受到函数名字典序和 DFS 遍历顺序
影响。

因此，现有排名不是基于路径可执行性得出的语义排名，不能可靠地
选择真正能够满足 require 条件的函数调用序列。
