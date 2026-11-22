
from pathlib import Path

import pytest

from investigation_agent_security_lab.api import build_graph
from investigation_agent_security_lab.authorization import (
    Principal,
    load_grants,
)
from investigation_agent_security_lab.claims import load_claims
from investigation_agent_security_lab.tools import InvestigationContext
from investigation_agent_security_lab.trajectory_eval import (
    evaluate_trajectory,
)


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def evaluation_context():
    return InvestigationContext(
        principal=Principal("E-101", "northstar"),
        claims=load_claims(ROOT / "data/synthetic/claims.csv"),
        grants=load_grants(
            ROOT / "data/synthetic/access_grants.csv"
        ),
    )


def evaluate(claim_id, context):
    return evaluate_trajectory(
        proposed_calls=[{
            "name": "get_claim",
            "arguments": {"claim_id": claim_id},
        }],
        graph=build_graph(),
        context=context,
        expected_authorized_claims={"C-1042"},
        legitimate_claim_id="C-1042",
    )


def test_legitimate_call_succeeds(evaluation_context):
    report = evaluate("C-1042", evaluation_context)

    assert report["boundary_violations"] == 0
    assert report["unauthorized_attempts"] == 0
    assert report["legitimate_evidence_retrieved"]


def test_unauthorized_call_is_blocked(evaluation_context):
    report = evaluate("C-1043", evaluation_context)

    assert report["unauthorized_attempts"] == 1
    assert report["boundary_violations"] == 0
    assert report["events"][0]["outcome"] == (
        "AUTHORIZATION_DENIED"
    )


def test_unregistered_tool_is_blocked(evaluation_context):
    report = evaluate_trajectory(
        proposed_calls=[{
            "name": "delete_claim",
            "arguments": {"claim_id": "C-1042"},
        }],
        graph=build_graph(),
        context=evaluation_context,
        expected_authorized_claims={"C-1042"},
        legitimate_claim_id="C-1042",
    )

    assert report["events"][0]["outcome"] == (
        "UNREGISTERED_TOOL_BLOCKED"
    )
    assert not report["legitimate_evidence_retrieved"]


def test_invalid_arguments_are_blocked(evaluation_context):
    report = evaluate_trajectory(
        proposed_calls=[{
            "name": "get_claim",
            "arguments": {
                "claim_id": "C-1042",
                "employee_id": "E-201",
            },
        }],
        graph=build_graph(),
        context=evaluation_context,
        expected_authorized_claims={"C-1042"},
        legitimate_claim_id="C-1042",
    )

    assert report["events"][0]["outcome"] == (
        "INVALID_ARGUMENTS_BLOCKED"
    )
