// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../benchmarks/BranchValueExample.sol";

contract BranchValuePropertyK3Harness {
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

    /*
     * Generated sequence:
     * prepareBadB() -> unlock() -> activate() -> trigger(uint256)
     */
    function property_sequence_2(uint256 arg_2_3_0) public {
        target.prepareBadB();
        target.unlock();
        target.activate();
        target.trigger(arg_2_3_0);
    }

    /*
     * Generated sequence:
     * prepareBadC() -> unlock() -> activate() -> trigger(uint256)
     */
    function property_sequence_3(uint256 arg_3_3_0) public {
        target.prepareBadC();
        target.unlock();
        target.activate();
        target.trigger(arg_3_3_0);
    }


    function echidna_value_safe()
        public
        view
        returns (bool)
    {
        return target.echidna_value_safe();
    }

}
