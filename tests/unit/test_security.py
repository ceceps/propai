"""Password hashing, tokens, and PII hashing."""

from __future__ import annotations

from datetime import timedelta

import jwt
import pytest

from propai_core.security import (
    create_access_token,
    decode_access_token,
    generate_short_code,
    hash_ip,
    hash_password,
    needs_rehash,
    verify_password,
)


def test_hash_is_salted_and_verifies():
    h1, h2 = hash_password("correct horse"), hash_password("correct horse")
    assert h1 != h2, "identical passwords must not produce identical hashes"
    assert verify_password("correct horse", h1)
    assert verify_password("correct horse", h2)


def test_wrong_password_returns_false_not_raises():
    assert verify_password("nope", hash_password("secret")) is False


def test_garbage_hash_does_not_raise():
    assert verify_password("x", "not-a-hash") is False
    assert needs_rehash("not-a-hash") is True


def test_password_not_recoverable_from_hash():
    assert "hunter2" not in hash_password("hunter2")


def test_token_roundtrip():
    token = create_access_token("user-123", "agent")
    claims = decode_access_token(token)
    assert claims["sub"] == "user-123"
    assert claims["role"] == "agent"


def test_expired_token_rejected():
    token = create_access_token("u", "agent", expires_delta=timedelta(seconds=-1))
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_tampered_token_rejected():
    token = create_access_token("u", "agent")
    head, payload, sig = token.split(".")
    with pytest.raises(jwt.PyJWTError):
        decode_access_token(f"{head}.{payload}.{sig[:-2]}xx")


def test_ip_hash_is_stable_and_not_reversible():
    assert hash_ip("203.0.113.7") == hash_ip("203.0.113.7")
    assert hash_ip("203.0.113.7") != hash_ip("203.0.113.8")
    assert "203.0.113.7" not in hash_ip("203.0.113.7")


def test_short_codes_are_unique_enough():
    codes = {generate_short_code() for _ in range(2000)}
    assert len(codes) == 2000
    assert all(len(c) == 7 and c.isalnum() for c in codes)
