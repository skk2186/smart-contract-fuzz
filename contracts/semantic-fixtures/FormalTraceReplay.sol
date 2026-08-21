// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../benchmarks/BranchValueExample.sol";
import "../benchmarks/NoisyFourStepExample.sol";
import "../benchmarks/RepeatedCallExample.sol";
import "../benchmarks/ResetExample.sol";
import "../benchmarks/AlternativePathExample.sol";
import "../benchmarks/MultiPropertyExample.sol";
import "../harnesses/formal/BranchValueFullK1Harness.sol";
import "../harnesses/formal/NoisyFourStepFullK1Harness.sol";
import "../harnesses/formal/RepeatedCallFullK1Harness.sol";
import "../harnesses/formal/ResetFullK1Harness.sol";
import "../harnesses/formal-b2/AlternativePathFullK1Harness.sol";
import "../harnesses/formal-b2/MultiPropertyFullK1Harness.sol";

/*
 * Successful-trace replay for the six synthetic formal benchmarks.
 * Each property executes a fixed known trigger directly on an original
 * target and through the actual generated Harness, then compares the
 * property-relevant final state.
 */
contract FormalTraceReplay {
    function echidna_branch_value_trace_agrees()
        public
        returns (bool)
    {
        BranchValueExample original = new BranchValueExample();
        original.prepareGood();
        original.unlock();
        original.activate();
        original.trigger(101);

        BranchValueFullK1Harness harness =
            new BranchValueFullK1Harness();
        harness.full_sequence_1(101);

        return
            original.value() == harness.target().value() &&
            !original.echidna_value_safe() &&
            !harness.echidna_value_safe();
    }

    function echidna_noisy_trace_agrees()
        public
        returns (bool)
    {
        NoisyFourStepExample original = new NoisyFourStepExample();
        original.register();
        original.deposit();
        original.approve();
        original.withdraw(101);

        NoisyFourStepFullK1Harness harness =
            new NoisyFourStepFullK1Harness();
        harness.full_sequence_1(101);

        return
            original.value() == harness.target().value() &&
            !original.echidna_value_safe() &&
            !harness.echidna_value_safe();
    }

    function echidna_repeated_call_trace_agrees()
        public
        returns (bool)
    {
        RepeatedCallExample original = new RepeatedCallExample();
        original.deposit();
        original.deposit();
        original.unlock();
        original.withdraw(101);

        RepeatedCallFullK1Harness harness =
            new RepeatedCallFullK1Harness();
        harness.full_sequence_1(101);

        return
            original.value() == harness.target().value() &&
            !original.echidna_value_safe() &&
            !harness.echidna_value_safe();
    }

    function echidna_reset_trace_agrees()
        public
        returns (bool)
    {
        ResetExample original = new ResetExample();
        original.begin();
        original.authorize();
        original.commit();
        original.execute(101);

        ResetFullK1Harness harness = new ResetFullK1Harness();
        harness.full_sequence_1(101);

        return
            original.value() == harness.target().value() &&
            !original.echidna_value_safe() &&
            !harness.echidna_value_safe();
    }

    function echidna_alternative_path_trace_agrees()
        public
        returns (bool)
    {
        AlternativePathExample original = new AlternativePathExample();
        original.openRouteA();
        original.confirm();
        original.execute(101);

        AlternativePathFullK1Harness harness =
            new AlternativePathFullK1Harness();
        harness.full_sequence_1(101);

        return
            original.value() == harness.target().value() &&
            !original.echidna_value_safe() &&
            !harness.echidna_value_safe();
    }

    function echidna_multi_property_trace_agrees()
        public
        returns (bool)
    {
        MultiPropertyExample original = new MultiPropertyExample();
        original.prepare();
        original.authorize();
        original.execute(101, 201);

        MultiPropertyFullK1Harness harness =
            new MultiPropertyFullK1Harness();
        harness.full_sequence_1(101, 201);

        return
            original.valueA() == harness.target().valueA() &&
            original.valueB() == harness.target().valueB() &&
            !original.echidna_value_a_safe() &&
            !original.echidna_value_b_safe() &&
            !harness.echidna_value_a_safe() &&
            !harness.echidna_value_b_safe();
    }
}
