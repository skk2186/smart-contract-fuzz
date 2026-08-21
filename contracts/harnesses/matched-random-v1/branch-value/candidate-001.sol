// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../../benchmarks/BranchValueExample.sol";

contract MatchedRandomV1BranchValueC001Harness {
    BranchValueExample public target;

    constructor() {
        target = new BranchValueExample();
    }

    /*
     * Frozen matched-random sequence: prepareGood() -> unlock() -> activate() -> trigger(uint256)
     */
    function matched_random_sequence_1(uint256 arg_3_0) public {
        target.prepareGood();
        target.unlock();
        target.activate();
        target.trigger(arg_3_0);
    }

    function echidna_value_safe() public returns (bool) {
        return target.echidna_value_safe();
    }
}
