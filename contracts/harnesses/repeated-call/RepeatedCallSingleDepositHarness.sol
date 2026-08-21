// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../benchmarks/RepeatedCallExample.sol";

contract RepeatedCallSingleDepositHarness {
    RepeatedCallExample public target;

    constructor() {
        target = new RepeatedCallExample();
    }

    /*
     * 错误序列：
     * 只调用一次 deposit，unlock 必然回滚。
     */
    function single_deposit_sequence(uint256 x) public {
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
