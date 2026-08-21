// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../benchmarks/ThreeStepExample.sol";

contract ThreeStepGuidedHarness {
    ThreeStepExample public target;

    constructor() {
        target = new ThreeStepExample();
    }

    /*
     * 根据状态依赖路径生成：
     * register -> deposit -> withdraw
     */
    function guided_sequence_1(uint256 x) public {
        target.register();
        target.deposit();
        target.withdraw(x);
    }

    function echidna_value_safe() public view returns (bool) {
        return target.value() <= 100;
    }
}
