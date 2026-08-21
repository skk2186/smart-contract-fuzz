// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../benchmarks/ThreeStepExample.sol";

contract ThreeStepWrongOrderHarness {
    ThreeStepExample public target;

    constructor() {
        target = new ThreeStepExample();
    }

    /*
     * 错误顺序：
     * register 后直接 withdraw。
     *
     * withdraw 要求 stage == 2，
     * 但 register 只会把 stage 设置为 1。
     */
    function wrong_sequence_1(uint256 x) public {
        target.register();
        target.withdraw(x);
        target.deposit();
    }

    function echidna_value_safe() public view returns (bool) {
        return target.value() <= 100;
    }
}
