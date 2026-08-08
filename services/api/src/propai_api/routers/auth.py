"""Login. No registration endpoint: agency staff are provisioned by an admin."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from propai_api.deps import CurrentUser, SessionDep
from propai_api.schemas import LoginRequest, TokenResponse, UserOut
from propai_core.models.users import User
from propai_core.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, session: SessionDep) -> TokenResponse:
    user = session.scalar(select(User).where(User.email == payload.email))

    # Verify even when the user is missing, against a dummy hash, so response
    # time does not reveal whether an email is registered.
    stored = user.password_hash if user else "$argon2id$v=19$m=65536,t=3,p=4$invalid"
    ok = verify_password(payload.password, stored)

    if not user or not ok or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    return TokenResponse(
        access_token=create_access_token(str(user.id), user.role.value),
        role=user.role,
        full_name=user.full_name,
    )


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser) -> User:
    return user
