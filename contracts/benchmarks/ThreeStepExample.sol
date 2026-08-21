// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

/*
 * 漏洞触发需要三个连续步骤：
 *
 * register()
 *      ↓
 * deposit()
 *      ↓
 * withdraw(x)，其中 x > 100
 */
contract ThreeStepExample {
    uint256 public stage;
    uint256 public value;

    function register() public {
        stage = 1;
    }

    function deposit() public {
        require(stage == 1, "not registered");
        stage = 2;
    }

    function withdraw(uint256 x) public {
        require(stage == 2, "not deposited");
        value = x;
    }

    function echidna_value_safe() public view returns (bool) {
        return value <= 100;
    }
}
