// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../benchmarks/NoisyFourStepExample.sol";

contract NoisyFourStepPermutationHarness {
    NoisyFourStepExample public target;

    constructor() {
        target = new NoisyFourStepExample();
    }

    /*
     * 固定关键函数集合，仅改变调用顺序：
     * register -> approve -> withdraw -> deposit
     */
    function permuted_sequence_1(uint256 x) public {
        target.register();
        target.approve();
        target.withdraw(x);
        target.deposit();
    }

    function echidna_value_safe() public view returns (bool) {
        return target.value() <= 100;
    }
}
