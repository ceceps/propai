"""Users and the three-role RBAC model from AGENTS.md."""

from __future__ import annotations

import uuid
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from propai_core.models.base import Base, Timestamps, UUIDPrimaryKey

if TYPE_CHECKING:
    from propai_core.models.properties import Property


class UserRole(StrEnum):
    ADMIN = "admin"
    AGENT = "agent"
    FREELANCE = "freelance"


class User(Base, UUIDPrimaryKey, Timestamps):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role", native_enum=False), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # WhatsApp number for the wa.me handoff link. Not a credential.
    whatsapp_number: Mapped[str | None] = mapped_column(String(32))

    properties: Mapped[list[Property]] = relationship(back_populates="owner")

    def __repr__(self) -> str:
        return f"<User {self.email} role={self.role}>"
