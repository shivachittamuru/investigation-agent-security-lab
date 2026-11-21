from pathlib import Path

import pytest

from investigation_agent_security_lab.authorization import (
    Principal,
    load_grants,
)
from investigation_agent_security_lab.claims import (
    get_claim_authorized,
    load_claims,
)


ROOT = Path(__file__).resolve().parents[2]
claims = load_claims(ROOT / "data/synthetic/claims.csv")
grants = load_grants(ROOT / "data/synthetic/access_grants.csv")


def test_authorized_employee_can_read():
    principal = Principal("E-101", "northstar")

    result = get_claim_authorized(
        claims, grants, principal, "northstar", "C-1042"
    )

    assert result["tenant_id"] == "northstar"


def test_same_tenant_without_grant_is_denied():
    principal = Principal("E-102", "northstar")

    with pytest.raises(PermissionError):
        get_claim_authorized(
            claims, grants, principal, "northstar", "C-1042"
        )


def test_cross_tenant_access_is_denied():
    principal = Principal("E-101", "northstar")

    with pytest.raises(PermissionError):
        get_claim_authorized(
            claims, grants, principal, "harbor", "C-1042"
        )


def test_missing_grant_is_denied():
    principal = Principal("E-999", "northstar")

    with pytest.raises(PermissionError):
        get_claim_authorized(
            claims, grants, principal, "northstar", "C-1042"
        )