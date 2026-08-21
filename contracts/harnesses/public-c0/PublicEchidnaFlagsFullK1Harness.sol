// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../public-benchmarks/raw/echidna/flags.sol";

contract PublicEchidnaFlagsFullK1Harness {
    Test public target;

    constructor() {
        target = new Test();
    }

    /*
     * Generated sequence:
     * set0(int256) -> set1(int256)
     */
    function full_sequence_1(int256 arg_1_0_0, int256 arg_1_1_0) public {
        target.set0(arg_1_0_0);
        target.set1(arg_1_1_0);
    }


    function echidna_alwaystrue()
        public
        returns (bool)
    {
        return target.echidna_alwaystrue();
    }

    function echidna_revert_always()
        public
        returns (bool)
    {
        return target.echidna_revert_always();
    }

    function echidna_sometimesfalse()
        public
        returns (bool)
    {
        return target.echidna_sometimesfalse();
    }

}
