// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../benchmarks/NoisyFourStepExample.sol";

contract NoisyFourStepRandomHarness {
    NoisyFourStepExample public target;

    constructor() {
        target = new NoisyFourStepExample();
    }

    /*
     * 随机生成的四步函数序列：
     * withdraw -> noise5 -> approve -> noise4
     */
    function random_sequence_1(uint256 x) public {
        target.withdraw(x);
        target.noise5(x);
        target.approve();
        target.noise4();
    }

    function echidna_value_safe() public view returns (bool) {
        return target.value() <= 100;
    }
}
