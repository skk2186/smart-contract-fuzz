// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../benchmarks/AlternativePathExample.sol";

contract AlternativePathFullK2Harness {
    AlternativePathExample public target;

    constructor() {
        target = new AlternativePathExample();
    }

    /*
     * Generated sequence:
     * openRouteA() -> confirm() -> execute(uint256)
     */
    function full_sequence_1(uint256 arg_1_2_0) public {
        target.openRouteA();
        target.confirm();
        target.execute(arg_1_2_0);
    }

    /*
     * Generated sequence:
     * openRouteB() -> confirm() -> execute(uint256)
     */
    function full_sequence_2(uint256 arg_2_2_0) public {
        target.openRouteB();
        target.confirm();
        target.execute(arg_2_2_0);
    }


    function echidna_value_safe()
        public view
        returns (bool)
    {
        return target.echidna_value_safe();
    }

}
