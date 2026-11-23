
from pathlib import Path

import pytest

from investigation_agent_security_lab.decision_policy import Coverage
from investigation_agent_security_lab.evidence_verifier import (
    load_coverage_registry,
    verify_evidence,
)


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def registry():
    return load_coverage_registry(
        ROOT / "data/synthetic/coverage_registry.csv"
    )


@pytest.mark.parametrize(
    "reference,tenant,claim,expected",
    [
        ("SUP-8821", "northstar", "C-1042", Coverage.UNKNOWN),
        ("POL-NS-1042", "northstar", "C-1042", Coverage.COVERED),
        ("POL-HB-1042", "northstar", "C-1042", Coverage.UNKNOWN),
        ("POL-NS-1043", "northstar", "C-1043", Coverage.NOT_COVERED),
        ("POL-NS-1044", "northstar", "C-1044", Coverage.UNKNOWN),
    ],
)
def test_evidence_provenance(
    reference, tenant, claim, expected, registry
):
    result = verify_evidence(
        candidate={
            "source_id": reference,
            "coverage": "COVERED",
            "evidence_complete": True,
        },
        tenant_id=tenant,
        claim_id=claim,
        registry=registry,
    )

    assert result.coverage == expected


def test_model_cannot_override_authoritative_coverage(registry):
    result = verify_evidence(
        candidate={
            "source_id": "POL-NS-1043",
            "coverage": "COVERED",
            "evidence_complete": True,
        },
        tenant_id="northstar",
        claim_id="C-1043",
        registry=registry,
    )

    assert result.coverage == Coverage.NOT_COVERED


def test_ambiguous_registry_reference_is_rejected(registry):
    duplicate = next(
        row for row in registry
        if row["source_id"] == "POL-NS-1042"
    )

    result = verify_evidence(
        candidate={"source_id": "POL-NS-1042"},
        tenant_id="northstar",
        claim_id="C-1042",
        registry=[*registry, duplicate],
    )

    assert result.coverage == Coverage.UNKNOWN
