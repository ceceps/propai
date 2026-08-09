"""Enable required Postgres extensions.

Split from the table migration because the ``vector`` type must exist before any
column can declare it, and ``pg_trgm`` before the fuzzy indexes.

Revision ID: 0001_extensions
Revises:
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_extensions"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _extension_available(conn, extension_name: str) -> bool:
    result = conn.execute(
        sa.text("SELECT 1 FROM pg_available_extensions WHERE name = :name"),
        {"name": extension_name},
    )
    return result.scalar() == 1


def _extension_exists(conn, extension_name: str) -> bool:
    result = conn.execute(
        sa.text("SELECT 1 FROM pg_extension WHERE extname = :name"),
        {"name": extension_name},
    )
    return result.scalar() == 1


def upgrade() -> None:
    conn = op.get_bind()

    if _extension_available(conn, "vector") and not _extension_exists(conn, "vector"):
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    if _extension_available(conn, "pg_trgm") and not _extension_exists(conn, "pg_trgm"):
        op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")


def downgrade() -> None:
    # Left in place deliberately: dropping an extension cascades to every column
    # using its types, which would silently destroy embedding data.
    pass
