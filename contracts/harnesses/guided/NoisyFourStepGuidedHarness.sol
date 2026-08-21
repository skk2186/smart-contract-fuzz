// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../benchmarks/NoisyFourStepExample.sol";

contract NoisyFourStepGuidedHarness {
    NoisyFourStepExample public target;

    constructor() {
        target = new NoisyFourStepExample();
    }

    /*
     * 根据安全属性相关状态依赖生成的调用序列：
     *
     * register 写 registered
     * deposit 读 registered、写 funded
     * approve 读 funded、写 approved
     * withdraw 读 approved、写 value
     *
     * value 又是 echidna_value_safe 读取的属性变量。
     */
    function guided_sequence_1(uint256 x) public {
        target.register();
        target.deposit();
        target.approve();
        target.withdraw(x);
    }

    function echidna_value_safe() public view returns (bool) {
        return target.value() <= 100;
    }
}
