// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

/*
 * 正确漏洞触发序列：
 *
 * deposit()
 *   ↓
 * deposit()
 *   ↓
 * unlock()
 *   ↓
 * withdraw(x)，其中 x > 100
 *
 * deposit 必须连续执行两次。
 */
contract RepeatedCallExample {
    uint8 public depositCount;
    bool public unlocked;
    uint256 public value;

    uint256 public noiseA;
    uint256 public noiseB;

    function deposit() public {
        require(depositCount < 2, "deposit limit reached");
        depositCount += 1;
    }

    function unlock() public {
        require(depositCount == 2, "two deposits required");
        unlocked = true;
    }

    function withdraw(uint256 x) public {
        require(unlocked, "not unlocked");
        value = x;
    }

    /*
     * 与目标属性无关的噪声函数。
     */

    function noise1(uint256 x) public {
        noiseA = x;
    }

    function noise2() public {
        noiseB = noiseA + 1;
    }

    function noise3() public {
        noiseA = noiseB + 1;
    }

    function echidna_value_safe()
        public
        view
        returns (bool)
    {
        return value <= 100;
    }
}
