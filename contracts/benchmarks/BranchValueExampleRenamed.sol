// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

contract BranchValueExampleRenamed {
    uint256 public gate;
    bool public unlocked;
    bool public active;
    uint256 public value;

    function aBadPrepare() public {
        gate = 0;
    }

    function bBadPrepare() public {
        gate = 1;
    }

    function cBadPrepare() public {
        gate = 6;
    }

    function dBadPrepare() public {
        gate = 8;
    }

    // 名称在字典序中排到最后，但语义上是正确函数
    function zCorrectPrepare() public {
        gate = 7;
    }

    function unlock() public {
        require(gate == 7, "incorrect gate");
        unlocked = true;
    }

    function activate() public {
        require(unlocked, "not unlocked");
        active = true;
    }

    function trigger(uint256 x) public {
        require(active, "not active");
        value = x;
    }

    function echidna_value_safe()
        public
        view
        returns (bool)
    {
        return value <= 100;
    }
}
