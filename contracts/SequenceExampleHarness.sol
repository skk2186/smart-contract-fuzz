// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "./SequenceExample.sol";

contract SequenceExampleHarness {
    SequenceExample target;

    constructor() {
        target = new SequenceExample();
    }

    function guided_sequence_1(uint256 x) public {
        target.initialize();
        target.update(x);
    }

    function echidna_value_safe() public view returns (bool) {
        return target.value() <= 100;
    }
}
