// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

/*
 * 两条有效路径：
 *
 * openRouteA → confirm → execute
 * openRouteB → confirm → execute
 */
contract AlternativePathExample {
    uint8 public stage;
    uint256 public value;

    function openRouteA() public {
        stage = 1;
    }

    function openRouteB() public {
        stage = 1;
    }

    function openWrongRoute() public {
        stage = 9;
    }

    function confirm() public {
        require(stage == 1, "route not open");
        stage = 2;
    }

    function execute(uint256 x) public {
        require(stage == 2, "not confirmed");
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
