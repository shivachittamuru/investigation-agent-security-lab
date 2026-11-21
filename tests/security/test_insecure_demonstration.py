"""Reproduces a known vulnerability; NOT a security-passing test."""
from pathlib import Path
from investigation_agent_security_lab.claims import get_claim_insecure, load_claims

DATA = Path(__file__).resolve().parents[2] / "data" / "synthetic" / "claims.csv"


def test_fixture_has_overlapping_claim_ids():
    claims = load_claims(DATA)
    assert len([r for r in claims if r["claim_id"] == "C-1042"]) == 2


def test_insecure_function_demonstrates_cross_tenant_read():
    claims = load_claims(DATA)
    attacker_tenant = "northstar"  # illustrative, not authenticated
    exposed = get_claim_insecure(claims, tenant_id="harbor", claim_id="C-1042")
    assert attacker_tenant != exposed["tenant_id"]
    assert exposed["amount_usd"] == "18500"
