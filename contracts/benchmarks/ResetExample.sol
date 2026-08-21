// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

/*
 * 正确漏洞触发路径：
 *
 * begin()
 *   ↓
 * authorize()
 *   ↓
 * commit()
 *   ↓
 * execute(x)，其中 x > 100
 *
 * reset 和 poison 同样会写 stage，
 * 但它们写入的值无法满足后续 require 条件。
 */
contract ResetExample {
    uint8 public stage;
    uint256 public value;

    uint256 public noiseA;
    uint256 public noiseB;

    function begin() public {
        stage = 1;
    }

    function authorize() public {
        require(stage == 1, "invalid begin stage");
        stage = 2;
    }

    function commit() public {
        require(stage == 2, "invalid authorize stage");
        stage = 3;
    }

    function execute(uint256 x) public {
        require(stage == 3, "invalid commit stage");
        value = x;
    }

    /*
     * 状态干扰函数。
     */

    function reset() public {
        stage = 0;
    }

    function poison() public {
        stage = 255;
    }

    /*
     * 与目标属性无关的噪声状态链。
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
