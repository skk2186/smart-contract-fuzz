// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../benchmarks/ResetExample.sol";

contract ResetPropertyK10Harness {
    ResetExample public target;

    constructor() {
        target = new ResetExample();
    }

    /*
     * Generated sequence:
     * begin() -> authorize() -> commit() -> execute(uint256)
     */
    function property_sequence_1(uint256 arg_1_3_0) public {
        target.begin();
        target.authorize();
        target.commit();
        target.execute(arg_1_3_0);
    }

    /*
     * Generated sequence:
     * begin() -> commit() -> authorize() -> execute(uint256)
     */
    function property_sequence_2(uint256 arg_2_3_0) public {
        target.begin();
        target.commit();
        target.authorize();
        target.execute(arg_2_3_0);
    }

    /*
     * Generated sequence:
     * poison() -> authorize() -> commit() -> execute(uint256)
     */
    function property_sequence_3(uint256 arg_3_3_0) public {
        target.poison();
        target.authorize();
        target.commit();
        target.execute(arg_3_3_0);
    }

    /*
     * Generated sequence:
     * poison() -> commit() -> authorize() -> execute(uint256)
     */
    function property_sequence_4(uint256 arg_4_3_0) public {
        target.poison();
        target.commit();
        target.authorize();
        target.execute(arg_4_3_0);
    }

    /*
     * Generated sequence:
     * reset() -> authorize() -> commit() -> execute(uint256)
     */
    function property_sequence_5(uint256 arg_5_3_0) public {
        target.reset();
        target.authorize();
        target.commit();
        target.execute(arg_5_3_0);
    }

    /*
     * Generated sequence:
     * reset() -> commit() -> authorize() -> execute(uint256)
     */
    function property_sequence_6(uint256 arg_6_3_0) public {
        target.reset();
        target.commit();
        target.authorize();
        target.execute(arg_6_3_0);
    }

    /*
     * Generated sequence:
     * authorize() -> commit() -> execute(uint256)
     */
    function property_sequence_7(uint256 arg_7_2_0) public {
        target.authorize();
        target.commit();
        target.execute(arg_7_2_0);
    }

    /*
     * Generated sequence:
     * begin() -> authorize() -> execute(uint256)
     */
    function property_sequence_8(uint256 arg_8_2_0) public {
        target.begin();
        target.authorize();
        target.execute(arg_8_2_0);
    }

    /*
     * Generated sequence:
     * begin() -> commit() -> execute(uint256)
     */
    function property_sequence_9(uint256 arg_9_2_0) public {
        target.begin();
        target.commit();
        target.execute(arg_9_2_0);
    }

    /*
     * Generated sequence:
     * commit() -> authorize() -> execute(uint256)
     */
    function property_sequence_10(uint256 arg_10_2_0) public {
        target.commit();
        target.authorize();
        target.execute(arg_10_2_0);
    }


    function echidna_value_safe()
        public
        view
        returns (bool)
    {
        return target.echidna_value_safe();
    }

}
