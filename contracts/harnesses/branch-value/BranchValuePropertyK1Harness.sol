// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../benchmarks/BranchValueExample.sol";

contract BranchValuePropertyK1Harness {
    BranchValueExample public target;

    constructor() {
        target = new BranchValueExample();
    }

    /*
     * Generated sequence:
     * prepareBadA() -> unlock() -> activate() -> trigger(uint256)
     */
    function property_sequence_1(uint256 arg_1_3_0) public {
        target.prepareBadA();
        target.unlock();
        target.activate();
        target.trigger(arg_1_3_0);
    }


    function echidna_value_safe()
        public
        view
        returns (bool)
    {
        return target.echidna_value_safe();
    }

}
