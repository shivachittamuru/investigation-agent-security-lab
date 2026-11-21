from dataclasses import dataclass

from langchain.tools import ToolRuntime, tool

from .authorization import Principal
from .claims import get_claim_authorized


@dataclass(frozen=True)
class InvestigationContext:
    principal: Principal
    claims: list[dict[str, str]]
    grants: list[dict[str, str]]


@tool
def get_claim(
    claim_id: str,
    runtime: ToolRuntime[InvestigationContext],
) -> dict:
    """Retrieve an authorized insurance claim by its claim ID."""

    ctx = runtime.context

    if ctx is None:
        raise PermissionError("Missing trusted context")

    return get_claim_authorized(
        claims=ctx.claims,
        grants=ctx.grants,
        principal=ctx.principal,
        tenant_id=ctx.principal.tenant_id,
        claim_id=claim_id,
    )