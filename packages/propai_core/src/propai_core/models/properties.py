"""Property listings and their photos."""

from __future__ import annotations

import uuid
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from propai_core.models.base import Base, Timestamps, UUIDPrimaryKey

if TYPE_CHECKING:
    from propai_core.models.users import User


class PropertyStatus(StrEnum):
    DRAFT = "draft"
    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"


class Property(Base, UUIDPrimaryKey, Timestamps):
    __tablename__ = "properties"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    # IDR values exceed float precision at scale; Numeric keeps them exact.
    price: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[PropertyStatus] = mapped_column(
        SAEnum(PropertyStatus, name="property_status", native_enum=False),
        default=PropertyStatus.DRAFT,
        nullable=False,
    )
    # Origin URL when the listing came from an external source (deferred scraper).
    source_url: Mapped[str | None] = mapped_column(String(512))

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    # bedrooms, bathrooms, land_area_m2, building_area_m2, certificate_type
    specs: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    owner: Mapped[User] = relationship(back_populates="properties")
    photos: Mapped[list[PropertyPhoto]] = relationship(
        back_populates="property", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Property {self.title!r} {self.status}>"


class PropertyPhoto(Base, UUIDPrimaryKey, Timestamps):
    __tablename__ = "property_photos"

    property_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"), index=True, nullable=False
    )
    path: Mapped[str] = mapped_column(String(512), nullable=False)
    # Vision-extracted feature labels.
    labels: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    # True for gpt-image-2 virtual staging output; originals stay untouched.
    is_staged: Mapped[bool] = mapped_column(default=False, nullable=False)
    source_photo_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("property_photos.id", ondelete="SET NULL")
    )
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)

    property: Mapped[Property] = relationship(back_populates="photos")
