// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../benchmarks/ResetExample.sol";

contract ResetPropertyK1Harness {
    ResetExample public target;

    constructor() {
        target = new ResetExample();
    }

    /*
     * Generated sequence:
     * begin() -> authorize() -> commit() -> execute(uint256)
     */
    function property_sequence_1(uint256 arg_1_3_0) public {
        target.begin();
        target.authorize();
        target.commit();
        target.execute(arg_1_3_0);
    }


    function echidna_value_safe()
        public
        view
        returns (bool)
    {
        return target.echidna_value_safe();
    }

}
