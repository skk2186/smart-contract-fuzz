// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../benchmarks/NoisyFourStepExample.sol";

contract DependencyHarnessK3 {
    NoisyFourStepExample public target;

    constructor() {
        target = new NoisyFourStepExample();
    }

    /*
     * Generated sequence:
     * noise5(uint256) -> noise3() -> noise6() -> noise4()
     */
    function dependency_sequence_1(uint256 arg_1_0_0) public {
        target.noise5(arg_1_0_0);
        target.noise3();
        target.noise6();
        target.noise4();
    }

    /*
     * Generated sequence:
     * noise4() -> noise2() -> noise3() -> noise6()
     */
    function dependency_sequence_2() public {
        target.noise4();
        target.noise2();
        target.noise3();
        target.noise6();
    }

    /*
     * Generated sequence:
     * noise3() -> noise6() -> noise4() -> noise2()
     */
    function dependency_sequence_3() public {
        target.noise3();
        target.noise6();
        target.noise4();
        target.noise2();
    }


    function echidna_value_safe()
        public
        view
        returns (bool)
    {
        return target.echidna_value_safe();
    }

}
