// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../benchmarks/NoisyFourStepExample.sol";

contract DependencyHarnessK10 {
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

    /*
     * Generated sequence:
     * noise2() -> noise3() -> noise6() -> noise4()
     */
    function dependency_sequence_4() public {
        target.noise2();
        target.noise3();
        target.noise6();
        target.noise4();
    }

    /*
     * Generated sequence:
     * noise1(uint256) -> noise2() -> noise3() -> noise6()
     */
    function dependency_sequence_5(uint256 arg_5_0_0) public {
        target.noise1(arg_5_0_0);
        target.noise2();
        target.noise3();
        target.noise6();
    }

    /*
     * Generated sequence:
     * register() -> deposit() -> approve() -> withdraw(uint256)
     */
    function dependency_sequence_6(uint256 arg_6_3_0) public {
        target.register();
        target.deposit();
        target.approve();
        target.withdraw(arg_6_3_0);
    }

    /*
     * Generated sequence:
     * noise6() -> noise4() -> noise2() -> noise3()
     */
    function dependency_sequence_7() public {
        target.noise6();
        target.noise4();
        target.noise2();
        target.noise3();
    }

    /*
     * Generated sequence:
     * noise5(uint256) -> noise3() -> noise4() -> noise2()
     */
    function dependency_sequence_8(uint256 arg_8_0_0) public {
        target.noise5(arg_8_0_0);
        target.noise3();
        target.noise4();
        target.noise2();
    }

    /*
     * Generated sequence:
     * noise1(uint256) -> noise2() -> noise3() -> noise4()
     */
    function dependency_sequence_9(uint256 arg_9_0_0) public {
        target.noise1(arg_9_0_0);
        target.noise2();
        target.noise3();
        target.noise4();
    }

    /*
     * Generated sequence:
     * noise5(uint256) -> noise3() -> noise6()
     */
    function dependency_sequence_10(uint256 arg_10_0_0) public {
        target.noise5(arg_10_0_0);
        target.noise3();
        target.noise6();
    }


    function echidna_value_safe()
        public
        view
        returns (bool)
    {
        return target.echidna_value_safe();
    }

}
