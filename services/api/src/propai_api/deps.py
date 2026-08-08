"""Shared FastAPI dependencies: DB session and the authenticated user."""

from __future__ import annotations

import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from propai_core.db import get_session
from propai_core.models.users import User
from propai_core.rbac import Action, Module, can
from propai_core.security import decode_access_token

bearer = HTTPBearer(auto_error=False)

SessionDep = Annotated[Session, Depends(get_session)]

_UNAUTHENTICATED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)


def current_user(
    session: SessionDep,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)] = None,
) -> User:
    if creds is None:
        raise _UNAUTHENTICATED
    try:
        claims = decode_access_token(creds.credentials)
        user_id = uuid.UUID(claims["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        # Deliberately identical response for expired, malformed, and forged
        # tokens: distinguishing them tells an attacker which part to fix.
        raise _UNAUTHENTICATED from None

    user = session.scalar(select(User).where(User.id == user_id))
    if user is None or not user.is_active:
        raise _UNAUTHENTICATED
    return user


CurrentUser = Annotated[User, Depends(current_user)]


def require(module: Module, action: Action):
    """Route guard for the coarse role check. Row ownership is enforced
    separately by the scope_* helpers, since a role may act on some rows only.
    """

    def _guard(user: CurrentUser) -> User:
        if not can(user, module, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {user.role} cannot {action} {module}",
            )
        return user

    return _guard
