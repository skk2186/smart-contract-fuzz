// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

/*
 * Local regression fixture for the V1 Harness execution model.
 *
 * This is not a vulnerability benchmark.  It makes three semantic
 * expectations executable:
 *   1. a same-caller two-step trace agrees with a wrapper trace;
 *   2. alternating callers can disagree with the wrapper trace;
 *   3. a later revert preserves a completed independent call, while
 *      it rolls back an earlier call inside the same wrapper frame.
 */

contract CallerSensitiveTarget {
    address public owner;
    bool public resumed;

    function claimOwner() external {
        owner = msg.sender;
    }

    function resume() external {
        require(msg.sender == owner, "not owner");
        resumed = true;
    }
}

contract CallerActor {
    function claimOwner(CallerSensitiveTarget target) external {
        target.claimOwner();
    }

    function tryResume(
        CallerSensitiveTarget target
    ) external returns (bool) {
        (bool ok, ) = address(target).call(
            abi.encodeWithSelector(target.resume.selector)
        );
        return ok;
    }
}

contract SameCallerWrapper {
    CallerSensitiveTarget public target;

    constructor() {
        target = new CallerSensitiveTarget();
    }

    function claimAndResume() external {
        target.claimOwner();
        target.resume();
    }
}

contract RollbackTarget {
    uint256 public stage;

    function prepare() external {
        stage = 1;
    }

    function failAfterPrepare() external pure {
        revert("expected failure");
    }
}

contract AtomicFailureWrapper {
    RollbackTarget public target;

    constructor() {
        target = new RollbackTarget();
    }

    function prepareAndFail() external {
        target.prepare();
        target.failAfterPrepare();
    }
}

contract HarnessSemanticDifferential {
    bool private sameCallerEquivalent;
    bool private callerAlternationDifference;
    bool private rollbackBoundaryDifference;

    constructor() {
        sameCallerEquivalent = evaluateSameCaller();
        callerAlternationDifference = evaluateCallerAlternation();
        rollbackBoundaryDifference = evaluateRollbackBoundary();
    }

    function evaluateSameCaller() private returns (bool) {
        CallerSensitiveTarget original = new CallerSensitiveTarget();
        CallerActor actor = new CallerActor();

        actor.claimOwner(original);
        bool originalOk = actor.tryResume(original);

        SameCallerWrapper wrapper = new SameCallerWrapper();
        wrapper.claimAndResume();

        return
            originalOk &&
            original.resumed() &&
            wrapper.target().resumed();
    }

    function evaluateCallerAlternation() private returns (bool) {
        CallerSensitiveTarget original = new CallerSensitiveTarget();
        CallerActor firstActor = new CallerActor();
        CallerActor secondActor = new CallerActor();

        firstActor.claimOwner(original);
        bool alternatingOk = secondActor.tryResume(original);

        SameCallerWrapper wrapper = new SameCallerWrapper();
        wrapper.claimAndResume();

        return
            !alternatingOk &&
            !original.resumed() &&
            wrapper.target().resumed();
    }

    function evaluateRollbackBoundary() private returns (bool) {
        RollbackTarget independentCalls = new RollbackTarget();
        independentCalls.prepare();

        (bool independentSecondCallOk, ) = address(independentCalls).call(
            abi.encodeWithSelector(
                independentCalls.failAfterPrepare.selector
            )
        );

        AtomicFailureWrapper wrapper = new AtomicFailureWrapper();
        (bool wrapperOk, ) = address(wrapper).call(
            abi.encodeWithSelector(wrapper.prepareAndFail.selector)
        );

        return
            !independentSecondCallOk &&
            independentCalls.stage() == 1 &&
            !wrapperOk &&
            wrapper.target().stage() == 0;
    }

    function echidna_same_caller_trace_is_equivalent()
        public
        view
        returns (bool)
    {
        return sameCallerEquivalent;
    }

    function echidna_caller_alternation_changes_behavior()
        public
        view
        returns (bool)
    {
        return callerAlternationDifference;
    }

    function echidna_rollback_boundary_changes_behavior()
        public
        view
        returns (bool)
    {
        return rollbackBoundaryDifference;
    }
}
