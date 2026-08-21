// SPDX-License-Identifier: MIT
pragma solidity ^0.4.23;

import "../../../public-benchmarks/adapted/SmartBugsMultiFuncEchidna.sol";

contract MatchedRandomV1SmartbugsMultifuncC003Harness {
    SmartBugsMultiFuncEchidna public target;

    constructor() {
        target = new SmartBugsMultiFuncEchidna();
    }

    /*
     * Frozen matched-random sequence: init() -> run(uint256)
     */
    function matched_random_sequence_1(uint256 arg_1_0) public {
        target.init();
        target.run(arg_1_0);
    }

    function echidna_count_does_not_underflow() public returns (bool) {
        return target.echidna_count_does_not_underflow();
    }
}
