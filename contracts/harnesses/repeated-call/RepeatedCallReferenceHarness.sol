// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../benchmarks/RepeatedCallExample.sol";

contract RepeatedCallReferenceHarness {
    RepeatedCallExample public target;

    constructor() {
        target = new RepeatedCallExample();
    }

    /*
     * 正确序列：
     * deposit → deposit → unlock → withdraw
     */
    function repeated_sequence_1(uint256 x) public {
        target.deposit();
        target.deposit();
        target.unlock();
        target.withdraw(x);
    }

    function echidna_value_safe()
        public
        view
        returns (bool)
    {
        return target.echidna_value_safe();
    }
}
