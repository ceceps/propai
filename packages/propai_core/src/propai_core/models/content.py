"""Generated marketing content, landing pages, short links, click tracking."""

from __future__ import annotations

import uuid
from enum import StrEnum
from typing import Any

from sqlalchemy import Enum as SAEnum
from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from propai_core.models.base import Base, Timestamps, UUIDPrimaryKey


class Demographic(StrEnum):
    MILLENNIAL = "millennial"
    YOUNG_FAMILY = "young_family"
    INVESTOR = "investor"


class ContentAsset(Base, UUIDPrimaryKey, Timestamps):
    """AIDA copy plus SEO metadata, one row per (property, lang, demographic).

    Bilingual output is a row per language rather than parallel columns, so
    adding a third language is data, not a migration.
    """

    __tablename__ = "content_assets"
    __table_args__ = (
        UniqueConstraint(
            "property_id", "lang", "demographic", name="uq_content_property_lang_demo"
        ),
    )

    property_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"), index=True, nullable=False
    )
    lang: Mapped[str] = mapped_column(String(2), nullable=False)
    demographic: Mapped[Demographic] = mapped_column(
        SAEnum(Demographic, name="demographic", native_enum=False), nullable=False
    )

    # AIDA, kept as discrete fields so templates and tests address them directly.
    attention: Mapped[str] = mapped_column(String(255), nullable=False)
    interest: Mapped[str] = mapped_column(Text, nullable=False)
    desire: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)

    seo_keywords: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    seo_meta_description: Mapped[str | None] = mapped_column(String(320))

    model_used: Mapped[str | None] = mapped_column(String(64))
    prompt_version: Mapped[str] = mapped_column(String(32), default="v1", nullable=False)


class LandingPage(Base, UUIDPrimaryKey, Timestamps):
    """Public page for a listing. Draft until a human publishes it."""

    __tablename__ = "landing_pages"
    __table_args__ = (UniqueConstraint("slug", "lang", name="uq_landing_slug_lang"),)

    property_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"), index=True, nullable=False
    )
    content_asset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("content_assets.id", ondelete="SET NULL")
    )
    slug: Mapped[str] = mapped_column(String(160), index=True, nullable=False)
    lang: Mapped[str] = mapped_column(String(2), nullable=False)

    # Null means unpublished. Constraint #1: AI output is a draft until a human
    # approves it, so nothing generated is publicly reachable by default.
    published_at: Mapped[Any | None] = mapped_column(DateTime(timezone=True))
    published_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )

    @property
    def is_published(self) -> bool:
        return self.published_at is not None


class ShortLink(Base, UUIDPrimaryKey, Timestamps):
    """Per-agent unique link. The head of the attribution chain."""

    __tablename__ = "short_links"

    code: Mapped[str] = mapped_column(String(16), unique=True, index=True, nullable=False)
    property_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"), index=True, nullable=False
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    landing_page_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("landing_pages.id", ondelete="SET NULL")
    )
    campaign: Mapped[str | None] = mapped_column(String(64))

    clicks: Mapped[list[LinkClick]] = relationship(
        back_populates="short_link", cascade="all, delete-orphan"
    )


class LinkClick(Base, UUIDPrimaryKey, Timestamps):
    __tablename__ = "link_clicks"

    short_link_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("short_links.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # Hashed with IP_HASH_SALT. Raw IPs are never stored (constraint #3).
    ip_hash: Mapped[str | None] = mapped_column(String(64))
    user_agent: Mapped[str | None] = mapped_column(String(512))
    referrer: Mapped[str | None] = mapped_column(String(512))

    short_link: Mapped[ShortLink] = relationship(back_populates="clicks")
