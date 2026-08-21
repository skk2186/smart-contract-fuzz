// SPDX-License-Identifier: MIT
pragma solidity ^0.4.23;

import "../../public-benchmarks/adapted/SmartBugsOneFuncEchidna.sol";

contract PublicSmartBugsOneFuncFullK5Harness {
    SmartBugsOneFuncEchidna public target;

    constructor() {
        target = new SmartBugsOneFuncEchidna();
    }

    /*
     * Generated sequence:
     * run(uint256) -> run(uint256)
     */
    function full_sequence_1(uint256 arg_1_0_0, uint256 arg_1_1_0) public {
        target.run(arg_1_0_0);
        target.run(arg_1_1_0);
    }


    function echidna_count_does_not_underflow()
        public view
        returns (bool)
    {
        return target.echidna_count_does_not_underflow();
    }

}
