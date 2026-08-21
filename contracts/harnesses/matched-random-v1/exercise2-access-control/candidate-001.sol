// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "../../../public-benchmarks/raw/exercise2/solution.sol";

contract MatchedRandomV1Exercise2AccessControlC001Harness {
    TestToken public target;

    constructor() {
        target = new TestToken();
    }

    /*
     * Frozen matched-random sequence: Owner() -> pause()
     */
    function matched_random_sequence_1() public {
        target.Owner();
        target.pause();
    }

    function echidna_no_transfer() public returns (bool) {
        return target.echidna_no_transfer();
    }
}
