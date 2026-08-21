// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

/*
 * 正确路径：
 *
 * prepareGood()
 *   ↓
 * unlock()
 *   ↓
 * activate()
 *   ↓
 * trigger(x)，其中 x > 100
 *
 * 多个 prepare 函数都写 gate，但只有 prepareGood
 * 写入的值能够满足 unlock 的 require 条件。
 */
contract BranchValueExample {
    uint256 public gate;
    bool public unlocked;
    bool public active;
    uint256 public value;

    /*
     * 按名称和声明顺序将错误写入函数放在前面，
     * 便于观察变量级依赖排序的不足。
     */

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

    function AprepareGood() public {
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
