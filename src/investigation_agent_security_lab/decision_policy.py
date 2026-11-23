
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class Coverage(str, Enum):
    UNKNOWN = "UNKNOWN"
    COVERED = "COVERED"
    NOT_COVERED = "NOT_COVERED"


class Decision(str, Enum):
    NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
    NOT_COVERED = "NOT_COVERED"
    ELIGIBLE_FOR_ADJUSTER_REVIEW = "ELIGIBLE_FOR_ADJUSTER_REVIEW"
    REQUIRES_SUPERVISOR_APPROVAL = "REQUIRES_SUPERVISOR_APPROVAL"
    ACTION_DENIED = "ACTION_DENIED"


@dataclass(frozen=True)
class VerifiedEvidence:
    """Facts supplied by a trusted evidence-validation process.

    Never populate this directly from unverified model output.
    """
    coverage: Coverage
    evidence_complete: bool
    source_id: str | None


MAX_ADJUSTER_REVIEW = Decimal("5000.00")


def evaluate_payout_policy(
    *,
    amount: Decimal,
    evidence: VerifiedEvidence,
) -> Decision:
    if not amount.is_finite() or amount < 0:
        raise ValueError("Invalid amount")

    # An evidence source must be independently verified.
    if (
        not evidence.source_id
        or not evidence.evidence_complete
        or evidence.coverage == Coverage.UNKNOWN
    ):
        return Decision.NEEDS_MORE_EVIDENCE

    if evidence.coverage == Coverage.NOT_COVERED:
        return Decision.NOT_COVERED

    if amount > MAX_ADJUSTER_REVIEW:
        return Decision.REQUIRES_SUPERVISOR_APPROVAL

    return Decision.ELIGIBLE_FOR_ADJUSTER_REVIEW


def authorize_agent_action(action: str) -> Decision | None:
    """Lab policy: an AI agent may recommend, never approve/pay."""
    if action == "recommend":
        return None

    return Decision.ACTION_DENIED
