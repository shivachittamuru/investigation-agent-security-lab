
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
import pytest
from fastapi.testclient import TestClient

from investigation_agent_security_lab.api import create_app
from investigation_agent_security_lab.identity import (
    LAB_AUDIENCE,
    LAB_ISSUER,
)


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def lab():
    key = secrets.token_bytes(32)
    app = create_app(ROOT, key)
    client = TestClient(app)

    def token(
        subject="E-101",
        signing_key=None,
        audience=LAB_AUDIENCE,
        expires_in=900,
    ):
        now = datetime.now(timezone.utc)
        return jwt.encode(
            {
                "sub": subject,
                "iss": LAB_ISSUER,
                "aud": audience,
                "iat": now,
                "exp": now + timedelta(seconds=expires_in),
            },
            signing_key if signing_key is not None else key,
            algorithm="HS256",
        )

    return client, token, app


def send(client, token, body=None):
    return client.post(
        "/investigate",
        json=body or {"claim_id": "C-1042"},
        headers={"Authorization": f"Bearer {token}"},
    )


def test_authorized_claim(lab):
    client, token, _ = lab
    response = send(client, token("E-101"))

    assert response.status_code == 200
    assert response.json()["claim"]["tenant_id"] == "northstar"


def test_same_tenant_unauthorized_claim(lab):
    client, token, _ = lab
    response = send(client, token("E-102"))

    assert response.status_code == 403
    assert "18500" not in response.text


def test_invalid_signature(lab):
    client, token, _ = lab
    forged = token(
        "E-101",
        signing_key=secrets.token_bytes(32),
    )

    assert send(client, forged).status_code == 401


def test_expired_token(lab):
    client, token, _ = lab
    assert send(client, token(expires_in=-60)).status_code == 401


def test_wrong_audience(lab):
    client, token, _ = lab
    assert send(
        client,
        token(audience="different-api"),
    ).status_code == 401


def test_missing_token(lab):
    client, _, _ = lab
    response = client.post(
        "/investigate",
        json={"claim_id": "C-1042"},
    )

    assert response.status_code == 401


def test_identity_spoofing_in_body(lab):
    client, token, _ = lab
    response = send(
        client,
        token("E-101"),
        {
            "claim_id": "C-1042",
            "employee_id": "E-201",
            "tenant_id": "harbor",
        },
    )

    assert response.status_code == 422


def test_unknown_employee(lab):
    client, token, _ = lab
    assert send(client, token("E-999")).status_code == 403
