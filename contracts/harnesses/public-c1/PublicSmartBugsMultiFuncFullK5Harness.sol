// SPDX-License-Identifier: MIT
pragma solidity ^0.4.23;

import "../../public-benchmarks/adapted/SmartBugsMultiFuncEchidna.sol";

contract PublicSmartBugsMultiFuncFullK5Harness {
    SmartBugsMultiFuncEchidna public target;

    constructor() {
        target = new SmartBugsMultiFuncEchidna();
    }

    /*
     * Generated sequence:
     * init() -> run(uint256) -> run(uint256)
     */
    function full_sequence_1(uint256 arg_1_1_0, uint256 arg_1_2_0) public {
        target.init();
        target.run(arg_1_1_0);
        target.run(arg_1_2_0);
    }

    /*
     * Generated sequence:
     * run(uint256) -> run(uint256)
     */
    function full_sequence_2(uint256 arg_2_0_0, uint256 arg_2_1_0) public {
        target.run(arg_2_0_0);
        target.run(arg_2_1_0);
    }

    /*
     * Generated sequence:
     * init() -> run(uint256)
     */
    function full_sequence_3(uint256 arg_3_1_0) public {
        target.init();
        target.run(arg_3_1_0);
    }


    function echidna_count_does_not_underflow()
        public view
        returns (bool)
    {
        return target.echidna_count_does_not_underflow();
    }

}
