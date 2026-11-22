
import csv
from pathlib import Path

import jwt

from .authorization import Principal


LAB_ISSUER = "investigation-lab"
LAB_AUDIENCE = "investigation-api"


def load_employees(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        return {
            row["employee_id"]: row
            for row in csv.DictReader(file)
        }


def verify_token(token: str, signing_key: bytes) -> dict:
    """Validate a synthetic lab token. Not a production verifier."""
    return jwt.decode(
        token,
        signing_key,
        algorithms=["HS256"],
        issuer=LAB_ISSUER,
        audience=LAB_AUDIENCE,
        options={
            "require": ["sub", "iss", "aud", "iat", "exp"]
        },
    )


def resolve_principal(
    verified_claims: dict,
    employees: dict[str, dict[str, str]],
) -> Principal:
    """Resolve employee eligibility from the trusted directory."""
    employee_id = verified_claims["sub"]
    employee = employees.get(employee_id)

    if employee is None or employee["active"] != "true":
        raise PermissionError("Employee access denied")

    if not employee.get("tenant_id"):
        raise PermissionError("Missing tenant assignment")

    return Principal(
        employee_id=employee_id,
        tenant_id=employee["tenant_id"],
    )
