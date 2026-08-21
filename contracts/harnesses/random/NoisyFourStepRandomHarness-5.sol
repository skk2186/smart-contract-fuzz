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
     * noise6 -> noise1 -> noise2 -> noise3
     */
    function random_sequence_1(uint256 x) public {
        target.noise6();
        target.noise1(x);
        target.noise2();
        target.noise3();
    }

    function echidna_value_safe() public view returns (bool) {
        return target.value() <= 100;
    }
}
