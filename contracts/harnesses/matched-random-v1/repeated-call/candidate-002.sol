// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../../benchmarks/RepeatedCallExample.sol";

contract MatchedRandomV1RepeatedCallC002Harness {
    RepeatedCallExample public target;

    constructor() {
        target = new RepeatedCallExample();
    }

    /*
     * Frozen matched-random sequence: deposit() -> unlock() -> withdraw(uint256)
     */
    function matched_random_sequence_1(uint256 arg_2_0) public {
        target.deposit();
        target.unlock();
        target.withdraw(arg_2_0);
    }

    function echidna_value_safe() public returns (bool) {
        return target.echidna_value_safe();
    }
}
