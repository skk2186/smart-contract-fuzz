// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "../../public-benchmarks/adapted/EchidnaFlagsTarget.sol";

contract PublicEchidnaFlagsFullK5Harness {
    PublicEchidnaFlagsTarget public target;

    constructor() {
        target = new PublicEchidnaFlagsTarget();
    }

    /*
     * Generated sequence:
     * set0(int256) -> set1(int256)
     */
    function full_sequence_1(int256 arg_1_0_0, int256 arg_1_1_0) public {
        target.set0(arg_1_0_0);
        target.set1(arg_1_1_0);
    }


    function echidna_sometimesfalse()
        public
        returns (bool)
    {
        return target.echidna_sometimesfalse();
    }

}
