// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../benchmarks/NoisyFourStepExample.sol";

contract PropertyHarnessK1 {
    NoisyFourStepExample public target;

    constructor() {
        target = new NoisyFourStepExample();
    }

    /*
     * Generated sequence:
     * register() -> deposit() -> approve() -> withdraw(uint256)
     */
    function property_sequence_1(uint256 arg_1_3_0) public {
        target.register();
        target.deposit();
        target.approve();
        target.withdraw(arg_1_3_0);
    }


    function echidna_value_safe()
        public
        view
        returns (bool)
    {
        return target.echidna_value_safe();
    }

}
