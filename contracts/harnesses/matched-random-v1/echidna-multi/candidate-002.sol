// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../../public-benchmarks/raw/echidna/multi.sol";

contract MatchedRandomV1EchidnaMultiC002Harness {
    C public target;

    constructor() {
        target = new C();
    }

    /*
     * Frozen matched-random sequence: g(uint256) -> h(uint256)
     */
    function matched_random_sequence_1(uint256 arg_0_0, uint256 arg_1_0) public {
        target.g(arg_0_0);
        target.h(arg_1_0);
    }

    function echidna_state3() public returns (bool) {
        return target.echidna_state3();
    }
}
