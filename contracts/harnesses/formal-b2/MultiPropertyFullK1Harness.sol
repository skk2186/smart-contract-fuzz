// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../benchmarks/MultiPropertyExample.sol";

contract MultiPropertyFullK1Harness {
    MultiPropertyExample public target;

    constructor() {
        target = new MultiPropertyExample();
    }

    /*
     * Generated sequence:
     * prepare() -> authorize() -> execute(uint256,uint256)
     */
    function full_sequence_1(uint256 arg_1_2_0, uint256 arg_1_2_1) public {
        target.prepare();
        target.authorize();
        target.execute(arg_1_2_0, arg_1_2_1);
    }


    function echidna_value_a_safe()
        public view
        returns (bool)
    {
        return target.echidna_value_a_safe();
    }

    function echidna_value_b_safe()
        public view
        returns (bool)
    {
        return target.echidna_value_b_safe();
    }

}
