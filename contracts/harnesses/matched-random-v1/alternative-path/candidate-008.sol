// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../../benchmarks/AlternativePathExample.sol";

contract MatchedRandomV1AlternativePathC008Harness {
    AlternativePathExample public target;

    constructor() {
        target = new AlternativePathExample();
    }

    /*
     * Frozen matched-random sequence: openWrongRoute() -> confirm() -> confirm() -> execute(uint256)
     */
    function matched_random_sequence_1(uint256 arg_3_0) public {
        target.openWrongRoute();
        target.confirm();
        target.confirm();
        target.execute(arg_3_0);
    }

    function echidna_value_safe() public returns (bool) {
        return target.echidna_value_safe();
    }
}
