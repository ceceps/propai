"""Leads, conversations, messages. The chat side of the funnel."""

from __future__ import annotations

import uuid
from enum import StrEnum
from typing import Any

from sqlalchemy import CheckConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from propai_core.models.base import Base, Timestamps, UUIDPrimaryKey


class LeadStatus(StrEnum):
    NEW = "new"
    QUALIFYING = "qualifying"
    QUALIFIED = "qualified"
    HANDED_OFF = "handed_off"
    LOST = "lost"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Lead(Base, UUIDPrimaryKey, Timestamps):
    __tablename__ = "leads"
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="ck_lead_score_range"),
    )

    name: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(32), index=True)
    email: Mapped[str | None] = mapped_column(String(255))

    status: Mapped[LeadStatus] = mapped_column(
        SAEnum(LeadStatus, name="lead_status", native_enum=False),
        default=LeadStatus.NEW,
        nullable=False,
    )
    score: Mapped[int] = mapped_column(default=0, nullable=False)
    # Rubric breakdown behind the score, so a number is never unexplained.
    score_breakdown: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    # Attribution: which agent's short link produced this lead.
    short_link_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("short_links.id", ondelete="SET NULL"), index=True
    )
    property_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("properties.id", ondelete="SET NULL"), index=True
    )
    assigned_agent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )

    handed_off_at: Mapped[Any | None] = mapped_column(DateTime(timezone=True))

    conversations: Mapped[list[Conversation]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )


class Conversation(Base, UUIDPrimaryKey, Timestamps):
    __tablename__ = "conversations"

    lead_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"), index=True, nullable=False
    )
    channel: Mapped[str] = mapped_column(String(32), default="web", nullable=False)
    lang: Mapped[str] = mapped_column(String(2), default="id", nullable=False)
    # LangGraph checkpoint thread id, so a conversation resumes where it stopped.
    thread_id: Mapped[str | None] = mapped_column(String(64), index=True)

    lead: Mapped[Lead] = relationship(back_populates="conversations")
    messages: Mapped[list[Message]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )


class Message(Base, UUIDPrimaryKey, Timestamps):
    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role: Mapped[MessageRole] = mapped_column(
        SAEnum(MessageRole, name="message_role", native_enum=False), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # Chunk ids the answer was grounded in. Empty list means ungrounded.
    citations: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    model_used: Mapped[str | None] = mapped_column(String(64))
    token_cost: Mapped[int | None] = mapped_column()

    conversation: Mapped[Conversation] = relationship(back_populates="messages")
