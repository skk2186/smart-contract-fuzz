// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../../benchmarks/ResetExample.sol";

contract MatchedRandomV1ResetExampleC023Harness {
    ResetExample public target;

    constructor() {
        target = new ResetExample();
    }

    /*
     * Frozen matched-random sequence: authorize() -> authorize() -> execute(uint256)
     */
    function matched_random_sequence_1(uint256 arg_2_0) public {
        target.authorize();
        target.authorize();
        target.execute(arg_2_0);
    }

    function echidna_value_safe() public returns (bool) {
        return target.echidna_value_safe();
    }
}
