"""Synthetic claim reads. INSECURE EXAMPLE: not for use with real data."""

import csv
from pathlib import Path

from .authorization import Principal, can_read_claim


def load_claims(path: Path) -> list[dict[str, str]]:
    """Read local, synthetic CSV fixture."""
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def get_claim_insecure(claims: list[dict[str, str]], tenant_id: str, claim_id: str) -> dict[str, str] | None:
    """INSECURE: trusts a caller-supplied tenant ID without authorization."""
    return next((claim for claim in claims if claim["tenant_id"] == tenant_id and claim["claim_id"] == claim_id), None)



def get_claim_authorized(
    claims: list[dict[str, str]],
    grants: list[dict[str, str]],
    principal: Principal,
    tenant_id: str,
    claim_id: str,
) -> dict[str, str] | None:

    if not can_read_claim(
        principal, tenant_id, claim_id, grants
    ):
        raise PermissionError("Access denied")

    return next(
        (
            claim for claim in claims
            if claim["tenant_id"] == tenant_id
            and claim["claim_id"] == claim_id
        ),
        None,
    )