"""Password hashing and access tokens.

Argon2id is used directly rather than through passlib: passlib is unmaintained
and its bcrypt backend breaks against bcrypt>=4. Argon2 is also the current
OWASP first choice for new applications.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import string
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from propai_core.config import get_settings

_hasher = PasswordHasher()

ALGORITHM = "HS256"
_BASE62 = string.digits + string.ascii_letters


def hash_password(plain: str) -> str:
    return _hasher.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Constant-time-ish verify. Never raises on a bad password."""
    try:
        return _hasher.verify(hashed, plain)
    except (VerifyMismatchError, InvalidHashError, ValueError):
        return False


def needs_rehash(hashed: str) -> bool:
    """True when argon2 parameters have moved on since this hash was made."""
    try:
        return _hasher.check_needs_rehash(hashed)
    except (InvalidHashError, ValueError):
        return True


def create_access_token(subject: str, role: str, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    if not settings.secret_key:
        raise RuntimeError("SECRET_KEY is required to issue tokens")
    ttl = expires_delta or timedelta(minutes=settings.access_token_ttl_minutes)
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": now + ttl,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Raises jwt.PyJWTError on anything invalid, including expiry."""
    settings = get_settings()
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])


def hash_ip(ip: str) -> str:
    """Salted hash for click tracking.

    Raw IPs are PII under constraint #3 and are never stored. HMAC rather than
    a bare digest, because the IPv4 space is small enough to brute force a
    plain SHA-256 of every address in seconds.
    """
    salt = get_settings().ip_hash_salt or "propai-dev-salt"
    return hmac.new(salt.encode(), ip.encode(), hashlib.sha256).hexdigest()


def generate_short_code(length: int = 7) -> str:
    """Base62 code for short links. 62^7 is ~3.5e12, so collisions are rare,
    but the caller still retries on unique-violation rather than assuming.
    """
    return "".join(secrets.choice(_BASE62) for _ in range(length))
