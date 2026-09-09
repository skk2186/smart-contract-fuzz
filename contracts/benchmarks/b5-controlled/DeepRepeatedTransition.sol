// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

// Controlled B5 C2 scenario. Exactly three calls to advance() are required;
// a shorter prefix cannot unlock the final trigger.
contract DeepRepeatedTransition {
    bool public prepared;
    uint8 public progress;
    bool public unlocked;
    uint256 public exposure;

    function prepare() public { prepared = true; }
    function advance() public {
        require(prepared, "prepare first");
        require(progress < 3, "progress complete");
        progress += 1;
    }
    function unlock() public { require(progress == 3, "three advances required"); unlocked = true; }
    function trigger(uint256 amount) public { require(unlocked, "unlock first"); exposure = amount; }

    function b5_target_state_reached() public view returns (bool) {
        return prepared && progress == 3 && unlocked;
    }

    function echidna_exposure_safe() public view returns (bool) {
        return exposure <= 100;
    }
}
