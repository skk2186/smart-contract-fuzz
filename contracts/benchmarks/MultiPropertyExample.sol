// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

/*
 * 同一条状态序列可以影响两个不同安全属性。
 */
contract MultiPropertyExample {
    uint8 public stage;

    uint256 public valueA;
    uint256 public valueB;

    function prepare() public {
        stage = 1;
    }

    function authorize() public {
        require(stage == 1, "not prepared");
        stage = 2;
    }

    function execute(
        uint256 x,
        uint256 y
    ) public {
        require(stage == 2, "not authorized");

        valueA = x;
        valueB = y;
    }

    function echidna_value_a_safe()
        public
        view
        returns (bool)
    {
        return valueA <= 100;
    }

    function echidna_value_b_safe()
        public
        view
        returns (bool)
    {
        return valueB <= 200;
    }
}
