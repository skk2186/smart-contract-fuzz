// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

/*
 * 正确漏洞触发路径：
 *
 * register()
 *    ↓
 * deposit()
 *    ↓
 * approve()
 *    ↓
 * withdraw(x)，其中 x > 100
 *
 * 合约同时包含多个与安全属性无关的干扰函数。
 */
contract NoisyFourStepExample {
    bool public registered;
    bool public funded;
    bool public approved;

    uint256 public value;

    uint256 public noiseA;
    uint256 public noiseB;
    uint256 public noiseC;

    function register() public {
        registered = true;
    }

    function deposit() public {
        require(registered, "not registered");
        funded = true;
    }

    function approve() public {
        require(funded, "not funded");
        approved = true;
    }

    function withdraw(uint256 x) public {
        require(approved, "not approved");
        value = x;
    }

    /*
     * 以下函数会扩大可调用函数集合，
     * 但不会直接影响安全属性 value <= 100。
     */

    function noise1(uint256 x) public {
        noiseA = x;
    }

    function noise2() public {
        noiseB = noiseA + 1;
    }

    function noise3() public {
        noiseC = noiseB + 1;
    }

    function noise4() public {
        noiseA = noiseC;
    }

    function noise5(uint256 x) public {
        noiseB = x;
    }

    function noise6() public {
        noiseC = noiseC + 1;
    }

    function echidna_value_safe() public view returns (bool) {
        return value <= 100;
    }
}
