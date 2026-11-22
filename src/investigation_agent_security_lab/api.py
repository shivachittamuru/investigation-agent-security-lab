
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from langchain.messages import AIMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, ConfigDict

from .authorization import Principal
from .claims import load_claims
from .authorization import load_grants
from .identity import load_employees, resolve_principal, verify_token
from .tools import InvestigationContext, get_claim


bearer = HTTPBearer(auto_error=False)


class InvestigationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    claim_id: str


def build_graph():
    builder = StateGraph(
        MessagesState,
        context_schema=InvestigationContext,
    )
    builder.add_node(
        "tools",
        ToolNode([get_claim], handle_tool_errors=False),
    )
    builder.add_edge(START, "tools")
    builder.add_edge("tools", END)
    return builder.compile()


def create_app(root: Path, signing_key: bytes) -> FastAPI:
    """Local lab app. Caller must supply server-owned signing key."""
    app = FastAPI(title="Investigation Agent Security Lab")

    claims = load_claims(root / "data/synthetic/claims.csv")
    grants = load_grants(root / "data/synthetic/access_grants.csv")
    # employees = load_employees(
    #     root / "data/synthetic/employees.csv"
    # )
    graph = build_graph()

    def get_current_principal(
        credentials: Annotated[
            HTTPAuthorizationCredentials | None,
            Depends(bearer),
        ],
    ) -> Principal:
        if credentials is None:
            raise HTTPException(401, "Authentication required")

        try:
            verified = verify_token(
                credentials.credentials, signing_key
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                401, "Invalid credentials"
            ) from None

        try:
            employees = load_employees(
                root / "data/synthetic/employees.csv"
            )
            return resolve_principal(verified, employees)
        except PermissionError:
            raise HTTPException(
                403, "Employee access denied"
            ) from None

    @app.post("/investigate")
    def investigate(
        request: InvestigationRequest,
        principal: Annotated[
            Principal, Depends(get_current_principal)
        ],
    ):
        # Simulated model tool call: no LLM is invoked.
        tool_request = AIMessage(
            content="",
            tool_calls=[{
                "name": "get_claim",
                "args": {"claim_id": request.claim_id},
                "id": "lab-call-001",
                "type": "tool_call",
            }],
        )

        context = InvestigationContext(
            principal=principal,
            claims=claims,
            grants=grants,
        )

        try:
            result = graph.invoke(
                {"messages": [tool_request]},
                context=context,
            )
        except PermissionError:
            raise HTTPException(
                403, "Access denied"
            ) from None

        tool_message = result["messages"][-1]

        # The existing tool returns a serialized dictionary.
        evidence = json.loads(tool_message.content)

        if evidence is None:
            raise HTTPException(404, "Claim not found")

        return {"claim": evidence}

    return app
