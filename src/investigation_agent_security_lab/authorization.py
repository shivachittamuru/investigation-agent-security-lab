import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Principal:
    employee_id: str
    tenant_id: str


def load_grants(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def can_read_claim(
    principal: Principal,
    tenant_id: str,
    claim_id: str,
    grants: list[dict[str, str]],
) -> bool:
    # Tenant isolation
    if principal.tenant_id != tenant_id:
        return False

    # Explicit resource-level permission
    return any(
        grant["employee_id"] == principal.employee_id
        and grant["tenant_id"] == tenant_id
        and grant["claim_id"] == claim_id
        and grant["permission"] == "read"
        for grant in grants
    )