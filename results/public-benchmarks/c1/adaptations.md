# 公开基准测试用例适配说明

## Echidna Flags 用例

来源：
crytic/echidna/tests/solidity/basic/flags.sol

保留内容：
- flag0 与 flag1 的初始值；
- set0(int256) 函数；
- set1(int256) 函数；
- echidna_sometimesfalse() 属性函数；
- 属性函数内部的事件触发逻辑。

移除内容：
- echidna_alwaystrue() 函数；
- echidna_revert_always() 函数。

这两个函数属于 Echidna 框架的自测属性，与目标状态依赖属性无关。保留它们会引入恒成立属性和恒回滚属性，干扰正式分析的结果。

## SmartBugs 算术合约用例

原始的漏洞状态转移逻辑与 Solidity 0.4.23 的算术语义均完整保留。所有合约文件已做扁平化处理，仅新增了供 Echidna 使用的观测属性函数。

SmartBugs 原始案例声明 `pragma solidity ^0.4.23`。由于 Echidna
不支持低于 0.4.25 的 Solidity 编译器，C-1 实验使用兼容该
pragma 范围的 Solidity 0.4.25。该调整不改变 Solidity 0.4.x
中未检查整数算术行为，目标下溢状态转移保持不变。

使用 Solidity 0.4.23 产生的 180 份启动失败日志保留在
`results/public-benchmarks/c1/invalid-solc-0.4.23/`，仅作为环境
兼容性排查记录，不计入实验成功率分母。
