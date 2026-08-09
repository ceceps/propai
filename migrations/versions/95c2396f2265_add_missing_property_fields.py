"""Add property listing system schema from SQL file

Revision ID: 95c2396f2265
Revises: c841cc3a0025
Create Date: 2026-08-09 23:59:19.134825
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '95c2396f2265'
down_revision: str | None = 'c841cc3a0025'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Read the SQL migration file and execute it
    with open('/home/ceceps/projects/propai/sql/001_property_listing_system.sql', 'r') as f:
        sql = f.read()
    
    # Execute SQL script
    op.execute(sql)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS showings CASCADE;")
    op.execute("DROP TABLE IF EXISTS saved_searches CASCADE;")
    op.execute("DROP TYPE IF EXISTS listing_status CASCADE;")
    op.execute("DROP TYPE IF EXISTS property_type CASCADE;")
