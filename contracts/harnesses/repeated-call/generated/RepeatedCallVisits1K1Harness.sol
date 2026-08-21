// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../../benchmarks/RepeatedCallExample.sol";

contract RepeatedCallVisits1K1Harness {
    RepeatedCallExample public target;

    constructor() {
        target = new RepeatedCallExample();
    }

    /*
     * Generated sequence:
     * deposit() -> unlock() -> withdraw(uint256)
     */
    function repeat_v1_sequence_1(uint256 arg_1_2_0) public {
        target.deposit();
        target.unlock();
        target.withdraw(arg_1_2_0);
    }


    function echidna_value_safe()
        public
        view
        returns (bool)
    {
        return target.echidna_value_safe();
    }

}
