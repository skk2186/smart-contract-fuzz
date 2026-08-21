// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../../benchmarks/MultiPropertyExample.sol";

contract MatchedRandomV1MultiPropertyC002Harness {
    MultiPropertyExample public target;

    constructor() {
        target = new MultiPropertyExample();
    }

    /*
     * Frozen matched-random sequence: prepare() -> authorize() -> authorize() -> execute(uint256,uint256)
     */
    function matched_random_sequence_1(uint256 arg_3_0, uint256 arg_3_1) public {
        target.prepare();
        target.authorize();
        target.authorize();
        target.execute(arg_3_0, arg_3_1);
    }

    function echidna_value_a_safe() public returns (bool) {
        return target.echidna_value_a_safe();
    }

    function echidna_value_b_safe() public returns (bool) {
        return target.echidna_value_b_safe();
    }
}
