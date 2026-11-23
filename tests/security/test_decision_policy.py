
from decimal import Decimal

import pytest

from investigation_agent_security_lab.decision_policy import (
    Coverage,
    Decision,
    VerifiedEvidence,
    authorize_agent_action,
    evaluate_payout_policy,
)


@pytest.mark.parametrize(
    "coverage,complete,source,amount,expected",
    [
        (Coverage.UNKNOWN, False, None, "4200",
         Decision.NEEDS_MORE_EVIDENCE),

        (Coverage.COVERED, True, "verified-001", "4200",
         Decision.ELIGIBLE_FOR_ADJUSTER_REVIEW),

        (Coverage.COVERED, True, "verified-002", "8000",
         Decision.REQUIRES_SUPERVISOR_APPROVAL),

        (Coverage.NOT_COVERED, True, "verified-003", "4200",
         Decision.NOT_COVERED),

        (Coverage.COVERED, False, "verified-004", "4200",
         Decision.NEEDS_MORE_EVIDENCE),

        (Coverage.COVERED, True, None, "4200",
         Decision.NEEDS_MORE_EVIDENCE),
    ],
)
def test_payout_policy(
    coverage, complete, source, amount, expected
):
    evidence = VerifiedEvidence(coverage, complete, source)

    assert evaluate_payout_policy(
        amount=Decimal(amount),
        evidence=evidence,
    ) == expected


@pytest.mark.parametrize("action", ["approve", "execute_payment"])
def test_agent_cannot_approve_or_pay(action):
    assert authorize_agent_action(action) == Decision.ACTION_DENIED


def test_agent_can_recommend():
    assert authorize_agent_action("recommend") is None


def test_invalid_amount_is_rejected():
    with pytest.raises(ValueError):
        evaluate_payout_policy(
            amount=Decimal("-100"),
            evidence=VerifiedEvidence(
                Coverage.COVERED, True, "verified-001"
            ),
        )
