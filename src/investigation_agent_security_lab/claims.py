"""Synthetic claim reads. INSECURE EXAMPLE: not for use with real data."""

import csv
from pathlib import Path


def load_claims(path: Path) -> list[dict[str, str]]:
    """Read local, synthetic CSV fixture."""
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def get_claim_insecure(claims: list[dict[str, str]], tenant_id: str, claim_id: str) -> dict[str, str] | None:
    """INSECURE: trusts a caller-supplied tenant ID without authorization."""
    return next((claim for claim in claims if claim["tenant_id"] == tenant_id and claim["claim_id"] == claim_id), None)
