// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

// Controlled B5 C3 scenario. The three route setters have the same structural
// role. Only the verified constant satisfies the following state-value gate.
contract ValueGatedCompetingPaths {
    uint8 public route;
    bool public unlocked;
    bool public active;
    uint256 public exposure;

    function selectArchiveRoute() public { route = 1; }
    function selectReviewRoute() public { route = 2; }
    function selectVerifiedRoute() public { route = 3; }
    function unlock() public { require(route == 3, "verified route required"); unlocked = true; }
    function activate() public { require(unlocked, "unlock first"); active = true; }
    function trigger(uint256 amount) public { require(active, "activate first"); exposure = amount; }

    function b5_target_state_reached() public view returns (bool) {
        return unlocked && active;
    }

    function echidna_exposure_safe() public view returns (bool) {
        return exposure <= 100;
    }
}
