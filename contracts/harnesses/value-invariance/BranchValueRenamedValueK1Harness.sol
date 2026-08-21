// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../benchmarks/BranchValueExampleRenamed.sol";

contract BranchValueRenamedValueK1Harness {
    BranchValueExampleRenamed public target;

    constructor() {
        target = new BranchValueExampleRenamed();
    }

    /*
     * Generated sequence:
     * zCorrectPrepare() -> unlock() -> activate() -> trigger(uint256)
     */
    function value_sequence_1(uint256 arg_1_3_0) public {
        target.zCorrectPrepare();
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
