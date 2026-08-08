"""RAG corpus: source documents and their embedded chunks."""

from __future__ import annotations

import uuid
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from propai_core.config import get_settings
from propai_core.models.base import Base, Timestamps, UUIDPrimaryKey

# Fixed at table-definition time: pgvector columns are fixed-width.
EMBEDDING_DIM = get_settings().embedding_dim


class Document(Base, UUIDPrimaryKey, Timestamps):
    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    lang: Mapped[str] = mapped_column(String(2), default="id", nullable=False)
    source_path: Mapped[str | None] = mapped_column(String(512))
    # Detects re-ingest of unchanged files.
    content_sha256: Mapped[str | None] = mapped_column(String(64), index=True)
    property_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"), index=True
    )

    chunks: Mapped[list[DocumentChunk]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class DocumentChunk(Base, UUIDPrimaryKey, Timestamps):
    """One retrievable passage. Carries both vector and lexical search surfaces."""

    __tablename__ = "document_chunks"
    __table_args__ = (
        Index(
            "ix_chunk_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Any | None] = mapped_column(Vector(EMBEDDING_DIM))
    # page number, section heading, etc.
    meta: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    document: Mapped[Document] = relationship(back_populates="chunks")
