// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../public-benchmarks/raw/echidna/multi.sol";

contract PublicEchidnaMultiFullK5Harness {
    C public target;

    constructor() {
        target = new C();
    }

    /*
     * Generated sequence:
     * f(uint256) -> g(uint256) -> h(uint256)
     */
    function full_sequence_1(uint256 arg_1_0_0, uint256 arg_1_1_0, uint256 arg_1_2_0) public {
        target.f(arg_1_0_0);
        target.g(arg_1_1_0);
        target.h(arg_1_2_0);
    }

    /*
     * Generated sequence:
     * g(uint256) -> h(uint256)
     */
    function full_sequence_2(uint256 arg_2_0_0, uint256 arg_2_1_0) public {
        target.g(arg_2_0_0);
        target.h(arg_2_1_0);
    }


    function echidna_state3()
        public
        returns (bool)
    {
        return target.echidna_state3();
    }

}
