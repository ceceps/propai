"""Test config. Forces fake providers so no test can spend money or need a token."""

from __future__ import annotations

import os
import uuid

os.environ.setdefault("PROPAI_PROVIDER_MODE", "fake")
os.environ.setdefault("SECRET_KEY", "test-secret-not-used-in-production")
os.environ.setdefault("IP_HASH_SALT", "test-salt")
os.environ.setdefault(
    "DATABASE_URL", "postgresql+psycopg://postgres:bismillah123@localhost:5432/propai"
)

import pytest  # noqa: E402

from propai_core.models.users import User, UserRole  # noqa: E402


def _user(role: UserRole) -> User:
    """A User instance not attached to a session. Enough for pure RBAC logic."""
    u = User(
        email=f"{role.value}@prolov-test.example.com",
        password_hash="x",
        full_name=role.value.title(),
        role=role,
    )
    u.id = uuid.uuid4()
    return u


@pytest.fixture
def admin() -> User:
    return _user(UserRole.ADMIN)


@pytest.fixture
def agent() -> User:
    return _user(UserRole.AGENT)


@pytest.fixture
def freelance() -> User:
    return _user(UserRole.FREELANCE)
