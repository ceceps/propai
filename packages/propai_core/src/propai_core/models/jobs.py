"""Background job records. The audit trail for anything async."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from sqlalchemy import Enum as SAEnum
from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from propai_core.models.base import Base, Timestamps, UUIDPrimaryKey


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Job(Base, UUIDPrimaryKey, Timestamps):
    __tablename__ = "jobs"

    kind: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    status: Mapped[JobStatus] = mapped_column(
        SAEnum(JobStatus, name="job_status", native_enum=False),
        default=JobStatus.QUEUED,
        nullable=False,
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    error: Mapped[str | None] = mapped_column(Text)
    attempts: Mapped[int] = mapped_column(default=0, nullable=False)
    started_at: Mapped[Any | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[Any | None] = mapped_column(DateTime(timezone=True))
