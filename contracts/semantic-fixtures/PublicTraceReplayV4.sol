// SPDX-License-Identifier: MIT
pragma solidity 0.4.25;

/*
 * Project-root-relative imports avoid the parent-import restriction in
 * Solidity 0.4.x while keeping the fixture in its dedicated directory.
 */
import "contracts/public-benchmarks/adapted/SmartBugsMultiFuncEchidna.sol";
import "contracts/public-benchmarks/adapted/SmartBugsOneFuncEchidna.sol";
import "contracts/harnesses/public-c1/PublicSmartBugsMultiFuncFullK5Harness.sol";
import "contracts/harnesses/public-c1/PublicSmartBugsOneFuncFullK5Harness.sol";

/* Successful-trace replay for the Solidity 0.4 public C-1 targets. */
contract PublicTraceReplayV4 {
    function echidna_smartbugs_multifunc_trace_agrees()
        public
        returns (bool)
    {
        SmartBugsMultiFuncEchidna original =
            new SmartBugsMultiFuncEchidna();
        original.init();
        original.run(2);

        PublicSmartBugsMultiFuncFullK5Harness harness =
            new PublicSmartBugsMultiFuncFullK5Harness();
        harness.full_sequence_3(2);

        return
            original.count() == harness.target().count() &&
            !original.echidna_count_does_not_underflow() &&
            !harness.echidna_count_does_not_underflow();
    }

    function echidna_smartbugs_onefunc_trace_agrees()
        public
        returns (bool)
    {
        SmartBugsOneFuncEchidna original =
            new SmartBugsOneFuncEchidna();
        original.run(0);
        original.run(2);

        PublicSmartBugsOneFuncFullK5Harness harness =
            new PublicSmartBugsOneFuncFullK5Harness();
        harness.full_sequence_1(0, 2);

        return
            original.count() == harness.target().count() &&
            !original.echidna_count_does_not_underflow() &&
            !harness.echidna_count_does_not_underflow();
    }
}
