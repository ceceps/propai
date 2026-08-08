"""Request and response models. Separate from ORM models on purpose: the wire
format should not change just because a column did.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from propai_core.models.properties import PropertyStatus
from propai_core.models.users import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    full_name: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: UserRole


class PropertyCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str | None = None
    price: Decimal = Field(gt=0, description="IDR, exact. Never a float.")
    location: str = Field(min_length=2, max_length=255)
    status: PropertyStatus = PropertyStatus.DRAFT
    specs: dict[str, Any] = Field(default_factory=dict)


class PropertyUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    location: str | None = Field(default=None, min_length=2, max_length=255)
    status: PropertyStatus | None = None
    specs: dict[str, Any] | None = None


class PropertyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    price: Decimal
    location: str
    status: PropertyStatus
    specs: dict[str, Any]
    owner_id: uuid.UUID
    created_at: datetime
