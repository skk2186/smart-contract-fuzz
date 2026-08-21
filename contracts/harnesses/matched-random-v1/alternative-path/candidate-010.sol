// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../../benchmarks/AlternativePathExample.sol";

contract MatchedRandomV1AlternativePathC010Harness {
    AlternativePathExample public target;

    constructor() {
        target = new AlternativePathExample();
    }

    /*
     * Frozen matched-random sequence: openRouteB() -> execute(uint256)
     */
    function matched_random_sequence_1(uint256 arg_1_0) public {
        target.openRouteB();
        target.execute(arg_1_0);
    }

    function echidna_value_safe() public returns (bool) {
        return target.echidna_value_safe();
    }
}
