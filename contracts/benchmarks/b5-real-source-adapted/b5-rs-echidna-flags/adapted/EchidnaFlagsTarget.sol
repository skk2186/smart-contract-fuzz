// SPDX-License-Identifier: AGPL-3.0
pragma solidity ^0.8.0;

/*
 * Adapted from:
 * crytic/echidna/tests/solidity/basic/flags.sol
 *
 * Adaptation:
 * The target state transition and echidna_sometimesfalse property
 * are preserved. Two unrelated Echidna framework-test properties
 * are omitted to prevent result contamination.
 */
contract PublicEchidnaFlagsTarget {
    event Flag(bool);

    bool private flag0 = true;
    bool private flag1 = true;

    function set0(int256 val) public returns (bool) {
        if (val % 100 == 0) {
            flag0 = false;
        }
    }

    function set1(int256 val) public returns (bool) {
        if (val % 10 == 0 && !flag0) {
            flag1 = false;
        }
    }

    /*
     * Deliberately non-view because the original property emits events.
     */
    function echidna_sometimesfalse()
        public
        returns (bool)
    {
        emit Flag(flag0);
        emit Flag(flag1);
        return flag1;
    }
}
