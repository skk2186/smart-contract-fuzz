// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../benchmarks/NoisyFourStepExample.sol";

contract PropertyHarnessK10 {
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

    /*
     * Generated sequence:
     * deposit() -> approve() -> withdraw(uint256)
     */
    function property_sequence_2(uint256 arg_2_2_0) public {
        target.deposit();
        target.approve();
        target.withdraw(arg_2_2_0);
    }

    /*
     * Generated sequence:
     * approve() -> withdraw(uint256)
     */
    function property_sequence_3(uint256 arg_3_1_0) public {
        target.approve();
        target.withdraw(arg_3_1_0);
    }


    function echidna_value_safe()
        public
        view
        returns (bool)
    {
        return target.echidna_value_safe();
    }

}
