"""End-to-end RBAC against a live database.

Marked integration: requires the compose Postgres on 5433.
Skip with: pytest -m "not integration"
"""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from propai_api.main import app
from propai_core.db import session_scope
from propai_core.models.properties import Property
from propai_core.models.users import User, UserRole
from propai_core.security import hash_password

pytestmark = pytest.mark.integration


def _mk_user(session, role: UserRole, tag: str) -> User:
    u = User(
        email=f"{tag}-{uuid.uuid4().hex[:8]}@prolov-test.example.com",
        password_hash=hash_password("pw-" + tag),
        full_name=tag,
        role=role,
    )
    session.add(u)
    session.flush()
    return u


@pytest.fixture
def world():
    """Two agents, an admin, a freelancer, one listing each for the agents.

    Only the rows created here are removed afterwards, matched by captured id.
    """
    with session_scope() as s:
        a1 = _mk_user(s, UserRole.AGENT, "agent-one")
        a2 = _mk_user(s, UserRole.AGENT, "agent-two")
        adm = _mk_user(s, UserRole.ADMIN, "admin")
        fr = _mk_user(s, UserRole.FREELANCE, "freelance")
        p1 = Property(
            title="Rumah Lamprit",
            price=Decimal("850000000"),
            location="Banda Aceh",
            owner_id=a1.id,
        )
        p2 = Property(
            title="Ruko Peunayong",
            price=Decimal("1200000000"),
            location="Banda Aceh",
            owner_id=a2.id,
        )
        s.add_all([p1, p2])
        s.flush()
        created = {
            "a1": a1.id,
            "a2": a2.id,
            "adm": adm.id,
            "fr": fr.id,
            "p1": p1.id,
            "p2": p2.id,
            "a1_email": a1.email,
            "adm_email": adm.email,
            "fr_email": fr.email,
        }
    yield created
    with session_scope() as s:
        s.execute(delete(Property).where(Property.id.in_([created["p1"], created["p2"]])))
        s.execute(
            delete(User).where(
                User.id.in_([created["a1"], created["a2"], created["adm"], created["fr"]])
            )
        )


@pytest.fixture
def client():
    return TestClient(app)


def _token(client, email: str, password: str) -> str:
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_health_reports_fake_mode(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["provider_mode"] == "fake"


def test_login_rejects_wrong_password(client, world):
    r = client.post("/auth/login", json={"email": world["a1_email"], "password": "wrong"})
    assert r.status_code == 401


def test_unauthenticated_request_is_401(client):
    assert client.get("/properties").status_code == 401


def test_agent_sees_only_own_listing(client, world):
    t = _token(client, world["a1_email"], "pw-agent-one")
    ids = {p["id"] for p in client.get("/properties", headers=_auth(t)).json()}
    assert str(world["p1"]) in ids
    assert str(world["p2"]) not in ids, "agent must not see another agent's listing"


def test_admin_sees_all_listings(client, world):
    t = _token(client, world["adm_email"], "pw-admin")
    ids = {p["id"] for p in client.get("/properties", headers=_auth(t)).json()}
    assert {str(world["p1"]), str(world["p2"])} <= ids


def test_cross_agent_fetch_returns_404_not_403(client, world):
    """403 would confirm the id exists, enabling portfolio enumeration."""
    t = _token(client, world["a1_email"], "pw-agent-one")
    assert client.get(f"/properties/{world['p2']}", headers=_auth(t)).status_code == 404


def test_cross_agent_update_is_blocked(client, world):
    t = _token(client, world["a1_email"], "pw-agent-one")
    r = client.patch(f"/properties/{world['p2']}", json={"price": 1}, headers=_auth(t))
    assert r.status_code == 404
    with session_scope() as s:
        assert s.get(Property, world["p2"]).price == Decimal("1200000000")


def test_freelance_cannot_create(client, world):
    t = _token(client, world["fr_email"], "pw-freelance")
    r = client.post(
        "/properties",
        json={"title": "Nope", "price": 1000, "location": "Banda Aceh"},
        headers=_auth(t),
    )
    assert r.status_code == 403


def test_freelance_cannot_delete(client, world):
    t = _token(client, world["fr_email"], "pw-freelance")
    assert client.delete(f"/properties/{world['p1']}", headers=_auth(t)).status_code == 403
