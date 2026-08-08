"""Enable required Postgres extensions.

Split from the table migration because the ``vector`` type must exist before any
column can declare it, and ``pg_trgm`` before the fuzzy indexes.

Revision ID: 0001_extensions
Revises:
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0001_extensions"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")


def downgrade() -> None:
    # Left in place deliberately: dropping an extension cascades to every column
    # using its types, which would silently destroy embedding data.
    pass
