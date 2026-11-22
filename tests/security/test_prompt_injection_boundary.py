from pathlib import Path

import pytest
from langchain.messages import AIMessage

from investigation_agent_security_lab.api import build_graph
from investigation_agent_security_lab.authorization import (
    Principal,
    load_grants,
)
from investigation_agent_security_lab.claims import load_claims
from investigation_agent_security_lab.tools import InvestigationContext


ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "claim_id,allowed",
    [
        ("C-1042", True),
        ("C-1043", False),
    ],
)
def test_claim_tool_enforces_authorization(claim_id, allowed):
    context = InvestigationContext(
        principal=Principal("E-101", "northstar"),
        claims=load_claims(ROOT / "data/synthetic/claims.csv"),
        grants=load_grants(
            ROOT / "data/synthetic/access_grants.csv"
        ),
    )

    request = AIMessage(
        content="",
        tool_calls=[{
            "name": "get_claim",
            "args": {"claim_id": claim_id},
            "id": "security-test",
            "type": "tool_call",
        }],
    )

    def invoke():
        return build_graph().invoke(
            {"messages": [request]},
            context=context,
        )

    if allowed:
        result = invoke()
        assert "C-1042" in result["messages"][-1].content
    else:
        with pytest.raises(PermissionError):
            invoke()