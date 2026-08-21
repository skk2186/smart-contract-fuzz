// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../../benchmarks/AlternativePathExample.sol";

contract MatchedRandomV1AlternativePathC006Harness {
    AlternativePathExample public target;

    constructor() {
        target = new AlternativePathExample();
    }

    /*
     * Frozen matched-random sequence: confirm() -> confirm() -> execute(uint256)
     */
    function matched_random_sequence_1(uint256 arg_2_0) public {
        target.confirm();
        target.confirm();
        target.execute(arg_2_0);
    }

    function echidna_value_safe() public returns (bool) {
        return target.echidna_value_safe();
    }
}
