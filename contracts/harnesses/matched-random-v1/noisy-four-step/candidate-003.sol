// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../../benchmarks/NoisyFourStepExample.sol";

contract MatchedRandomV1NoisyFourStepC003Harness {
    NoisyFourStepExample public target;

    constructor() {
        target = new NoisyFourStepExample();
    }

    /*
     * Frozen matched-random sequence: approve() -> withdraw(uint256)
     */
    function matched_random_sequence_1(uint256 arg_1_0) public {
        target.approve();
        target.withdraw(arg_1_0);
    }

    function echidna_value_safe() public returns (bool) {
        return target.echidna_value_safe();
    }
}
