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
     * noise4 -> noise2 -> noise1 -> deposit
     */
    function random_sequence_1(uint256 x) public {
        target.noise4();
        target.noise2();
        target.noise1(x);
        target.deposit();
    }

    function echidna_value_safe() public view returns (bool) {
        return target.value() <= 100;
    }
}
