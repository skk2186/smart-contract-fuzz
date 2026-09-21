// SPDX-License-Identifier: MIT
pragma solidity 0.4.25;

// Controlled mechanism benchmark: independent target and distractor properties.
contract MultiPropertyInterference {
    uint256 private targetReady;
    uint256 private targetValue;

    uint256 private distractorAReady;
    uint256 private distractorAStage1;
    uint256 private distractorAStage2;
    uint256 private distractorAValue;

    uint256 private distractorBReady;
    uint256 private distractorBStage1;
    uint256 private distractorBStage2;
    uint256 private distractorBStage3;
    uint256 private distractorBValue;

    function prepareTarget() public {
        targetReady = 1;
    }

    function triggerTarget() public {
        require(targetReady == 1);
        targetValue = 1;
    }

    function prepareDistractorA() public {
        distractorAReady = 1;
    }

    function stepDistractorA1() public {
        require(distractorAReady == 1);
        distractorAStage1 = 1;
    }

    function stepDistractorA2() public {
        require(distractorAStage1 == 1);
        distractorAStage2 = 1;
    }

    function triggerDistractorA() public {
        require(distractorAStage2 == 1);
        distractorAValue = 1;
    }

    function prepareDistractorB() public {
        distractorBReady = 1;
    }

    function stepDistractorB1() public {
        require(distractorBReady == 1);
        distractorBStage1 = 1;
    }

    function stepDistractorB2() public {
        require(distractorBStage1 == 1);
        distractorBStage2 = 1;
    }

    function stepDistractorB3() public {
        require(distractorBStage2 == 1);
        distractorBStage3 = 1;
    }

    function triggerDistractorB() public {
        require(distractorBStage3 == 1);
        distractorBValue = 1;
    }

    function echidna_target_safe() public view returns (bool) {
        return targetValue <= 1;
    }

    function echidna_distractor_a_safe() public view returns (bool) {
        return distractorAValue <= 1;
    }

    function echidna_distractor_b_safe() public view returns (bool) {
        return distractorBValue <= 1;
    }
}
