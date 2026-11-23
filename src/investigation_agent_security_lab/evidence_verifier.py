
import csv
from pathlib import Path

from .decision_policy import Coverage, VerifiedEvidence


def load_coverage_registry(path: Path) -> list[dict[str, str]]:
    """Load a trusted synthetic registry.

    The file is assumed to be controlled by the application,
    not by customers or the model.
    """
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def verify_evidence(
    *,
    candidate: dict,
    tenant_id: str,
    claim_id: str,
    registry: list[dict[str, str]],
) -> VerifiedEvidence:
    """Resolve untrusted evidence to an authoritative record.

    tenant_id and claim_id must come from trusted execution
    context, not from the model-generated candidate.
    """
    unverified = VerifiedEvidence(
        coverage=Coverage.UNKNOWN,
        evidence_complete=False,
        source_id=None,
    )

    if not isinstance(candidate, dict):
        return unverified

    reference = candidate.get("source_id")

    if not isinstance(reference, str) or not reference:
        return unverified

    matches = [
        row for row in registry
        if row["source_id"] == reference
        and row["tenant_id"] == tenant_id
        and row["claim_id"] == claim_id
    ]

    # Reject missing or ambiguous authoritative records.
    if len(matches) != 1:
        return unverified

    record = matches[0]

    if record["active"] != "true":
        return unverified

    if record["evidence_complete"] != "true":
        return unverified

    try:
        coverage = Coverage(record["coverage"])
    except ValueError:
        return unverified

    if coverage == Coverage.UNKNOWN:
        return unverified

    # Crucially: use authoritative record values,
    # NOT model-provided coverage/evidence_complete.
    return VerifiedEvidence(
        coverage=coverage,
        evidence_complete=True,
        source_id=record["source_id"],
    )
