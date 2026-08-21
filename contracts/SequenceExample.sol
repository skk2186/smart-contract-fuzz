// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

contract SequenceExample {
    bool public initialized;
    uint256 public value;

    function initialize() public {
        initialized = true;
    }

    function update(uint256 x) public {
        require(initialized, "not initialized");
        value = x;
    }

    function echidna_value_safe() public view returns (bool) {
        return value <= 100;
    }
}
