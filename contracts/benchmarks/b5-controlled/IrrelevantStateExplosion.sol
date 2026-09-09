// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

// Controlled B5 C1 scenario. The safety property depends on one five-step
// state transition, while the other public functions form legal stateful
// maintenance paths that are not property writers.
contract IrrelevantStateExplosion {
    bool public initialized;
    bool public configured;
    bool public authorized;
    bool public active;
    uint256 public exposure;
    uint256 public metadata;
    uint256 public cache;
    uint256 public snapshot;
    uint256 public counter;
    uint256 public auxiliary;
    bool public maintenanceOpen;

    function initialize() public { initialized = true; }
    function configure() public { require(initialized, "initialize first"); configured = true; }
    function authorize() public { require(configured, "configure first"); authorized = true; }
    function activate() public { require(authorized, "authorize first"); active = true; }
    function expose(uint256 amount) public { require(active, "activate first"); exposure = amount; }

    function recordMetadata(uint256 value) public { metadata = value; }
    function refreshCache() public { cache = metadata + 1; }
    function publishSnapshot() public { snapshot = cache + 1; }
    function rotateMetadata() public { metadata = snapshot; }
    function setMaintenance(bool enabled) public { maintenanceOpen = enabled; }
    function updateCounter() public { require(maintenanceOpen, "maintenance closed"); counter += 1; }
    function tuneAuxiliary(uint256 value) public { auxiliary = value; }
    function combineAuxiliary() public { auxiliary = auxiliary + counter; }
    function clearCache() public { cache = 0; }

    // Passive post-run observer input; it is not an Echidna property and is
    // not part of PHS candidate generation.
    function b5_target_state_reached() public view returns (bool) {
        return initialized && configured && authorized && active;
    }

    function echidna_exposure_safe() public view returns (bool) {
        return exposure <= 100;
    }
}
