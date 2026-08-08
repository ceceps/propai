"""All ORM models. Importing this module registers every table on Base.metadata,
which is what Alembic autogenerate walks.
"""

from propai_core.models.base import Base, Language, Timestamps, UUIDPrimaryKey
from propai_core.models.content import (
    ContentAsset,
    Demographic,
    LandingPage,
    LinkClick,
    ShortLink,
)
from propai_core.models.jobs import Job, JobStatus
from propai_core.models.leads import (
    Conversation,
    Lead,
    LeadStatus,
    Message,
    MessageRole,
)
from propai_core.models.properties import Property, PropertyPhoto, PropertyStatus
from propai_core.models.rag import EMBEDDING_DIM, Document, DocumentChunk
from propai_core.models.users import User, UserRole

__all__ = [
    "EMBEDDING_DIM",
    "Base",
    "ContentAsset",
    "Conversation",
    "Demographic",
    "Document",
    "DocumentChunk",
    "Job",
    "JobStatus",
    "LandingPage",
    "Language",
    "Lead",
    "LeadStatus",
    "LinkClick",
    "Message",
    "MessageRole",
    "Property",
    "PropertyPhoto",
    "PropertyStatus",
    "ShortLink",
    "Timestamps",
    "UUIDPrimaryKey",
    "User",
    "UserRole",
]
