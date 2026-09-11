/*
 * Adapted from:
 * smartbugs/smartbugs-curated
 * dataset/arithmetic/integer_overflow_multitx_multifunc_feasible.sol
 *
 * Adaptation:
 * Only an Echidna property was added.
 * The vulnerable state transition is preserved.
 */

pragma solidity ^0.4.23;

contract SmartBugsMultiFuncEchidna {
    uint256 private initialized = 0;
    uint256 public count = 1;

    function init() public {
        initialized = 1;
    }

    function run(uint256 input) public {
        if (initialized == 0) {
            return;
        }

        count -= input;
    }

    function echidna_count_does_not_underflow()
        public
        view
        returns (bool)
    {
        return count <= 1;
    }
}
