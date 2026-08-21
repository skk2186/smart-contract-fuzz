// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../benchmarks/ResetExample.sol";

contract ResetDependencyK10Harness {
    ResetExample public target;

    constructor() {
        target = new ResetExample();
    }

    /*
     * Generated sequence:
     * reset() -> commit() -> authorize() -> execute(uint256)
     */
    function dependency_sequence_1(uint256 arg_1_3_0) public {
        target.reset();
        target.commit();
        target.authorize();
        target.execute(arg_1_3_0);
    }

    /*
     * Generated sequence:
     * reset() -> authorize() -> commit() -> execute(uint256)
     */
    function dependency_sequence_2(uint256 arg_2_3_0) public {
        target.reset();
        target.authorize();
        target.commit();
        target.execute(arg_2_3_0);
    }

    /*
     * Generated sequence:
     * poison() -> commit() -> authorize() -> execute(uint256)
     */
    function dependency_sequence_3(uint256 arg_3_3_0) public {
        target.poison();
        target.commit();
        target.authorize();
        target.execute(arg_3_3_0);
    }

    /*
     * Generated sequence:
     * poison() -> authorize() -> commit() -> execute(uint256)
     */
    function dependency_sequence_4(uint256 arg_4_3_0) public {
        target.poison();
        target.authorize();
        target.commit();
        target.execute(arg_4_3_0);
    }

    /*
     * Generated sequence:
     * begin() -> commit() -> authorize() -> execute(uint256)
     */
    function dependency_sequence_5(uint256 arg_5_3_0) public {
        target.begin();
        target.commit();
        target.authorize();
        target.execute(arg_5_3_0);
    }

    /*
     * Generated sequence:
     * begin() -> authorize() -> commit() -> execute(uint256)
     */
    function dependency_sequence_6(uint256 arg_6_3_0) public {
        target.begin();
        target.authorize();
        target.commit();
        target.execute(arg_6_3_0);
    }

    /*
     * Generated sequence:
     * reset() -> commit() -> authorize()
     */
    function dependency_sequence_7() public {
        target.reset();
        target.commit();
        target.authorize();
    }

    /*
     * Generated sequence:
     * reset() -> authorize() -> commit()
     */
    function dependency_sequence_8() public {
        target.reset();
        target.authorize();
        target.commit();
    }

    /*
     * Generated sequence:
     * poison() -> commit() -> authorize()
     */
    function dependency_sequence_9() public {
        target.poison();
        target.commit();
        target.authorize();
    }

    /*
     * Generated sequence:
     * poison() -> authorize() -> commit()
     */
    function dependency_sequence_10() public {
        target.poison();
        target.authorize();
        target.commit();
    }


    function echidna_value_safe()
        public
        view
        returns (bool)
    {
        return target.echidna_value_safe();
    }

}
