// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

contract BranchValueExampleReordered {
    uint256 public gate;
    bool public unlocked;
    bool public active;
    uint256 public value;

    // 正确函数被放在源码最前面
    function prepareGood() public {
        gate = 7;
    }

    function prepareBadA() public {
        gate = 0;
    }

    function prepareBadB() public {
        gate = 1;
    }

    function prepareBadC() public {
        gate = 6;
    }

    function prepareBadD() public {
        gate = 8;
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
