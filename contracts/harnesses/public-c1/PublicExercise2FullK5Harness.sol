// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "../../public-benchmarks/raw/exercise2/solution.sol";

contract PublicExercise2FullK5Harness {
    TestToken public target;

    constructor() {
        target = new TestToken();
    }

    /*
     * Generated sequence:
     * Owner() -> pause()
     */
    function full_sequence_1() public {
        target.Owner();
        target.pause();
    }

    /*
     * Generated sequence:
     * Owner() -> resume()
     */
    function full_sequence_2() public {
        target.Owner();
        target.resume();
    }


    function echidna_no_transfer()
        public view
        returns (bool)
    {
        return target.echidna_no_transfer();
    }

}
