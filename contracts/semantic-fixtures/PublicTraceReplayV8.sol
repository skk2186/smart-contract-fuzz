// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../public-benchmarks/raw/echidna/multi.sol";
import "../public-benchmarks/adapted/EchidnaFlagsTarget.sol";
import "../public-benchmarks/raw/exercise2/solution.sol";
import "../harnesses/public-c1/PublicEchidnaMultiFullK5Harness.sol";
import "../harnesses/public-c1/PublicEchidnaFlagsFullK5Harness.sol";
import "../harnesses/public-c1/PublicExercise2FullK5Harness.sol";

/* Successful-trace replay for the Solidity 0.8 public C-1 targets. */
contract PublicTraceReplayV8 {
    function echidna_public_multi_trace_agrees()
        public
        returns (bool)
    {
        C original = new C();
        original.f(12);
        original.g(8);
        original.h(0);

        PublicEchidnaMultiFullK5Harness harness =
            new PublicEchidnaMultiFullK5Harness();
        harness.full_sequence_1(12, 8, 0);

        return
            !original.echidna_state3() &&
            !harness.echidna_state3();
    }

    function echidna_public_flags_trace_agrees()
        public
        returns (bool)
    {
        PublicEchidnaFlagsTarget original =
            new PublicEchidnaFlagsTarget();
        original.set0(100);
        original.set1(10);

        PublicEchidnaFlagsFullK5Harness harness =
            new PublicEchidnaFlagsFullK5Harness();
        harness.full_sequence_1(100, 10);

        return
            !original.echidna_sometimesfalse() &&
            !harness.echidna_sometimesfalse();
    }

    function echidna_exercise2_same_caller_trace_agrees()
        public
        returns (bool)
    {
        TestToken original = new TestToken();
        original.Owner();
        original.resume();

        PublicExercise2FullK5Harness harness =
            new PublicExercise2FullK5Harness();
        harness.full_sequence_2();

        return
            !original.echidna_no_transfer() &&
            !harness.echidna_no_transfer();
    }
}
