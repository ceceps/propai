"""add_rls_policies

Revision ID: 042e304ad2b7
Revises: 95c2396f2265
Create Date: 2026-08-10 01:59:18.276677
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '042e304ad2b7'
down_revision: str | None = '95c2396f2265'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Enable RLS
    op.execute("ALTER TABLE properties ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE property_photos ENABLE ROW LEVEL SECURITY;")

    # Drop existing policies if they exist (for idempotency)
    op.execute("DROP POLICY IF EXISTS properties_access_policy ON properties;")
    op.execute("DROP POLICY IF EXISTS property_photos_access_policy ON property_photos;")
    op.execute("DROP POLICY IF EXISTS properties_modify_policy ON properties;")

    # Create Policies
    op.execute("""
        CREATE POLICY properties_access_policy ON properties
            FOR SELECT
            USING (owner_id = current_setting('app.current_user_id', true)::uuid);
    """)
    op.execute("""
        CREATE POLICY property_photos_access_policy ON property_photos
            FOR SELECT
            USING (EXISTS (
                SELECT 1 FROM properties 
                WHERE properties.id = property_photos.property_id 
                AND properties.owner_id = current_setting('app.current_user_id', true)::uuid
            ));
    """)
    op.execute("""
        CREATE POLICY properties_modify_policy ON properties
            FOR ALL
            USING (owner_id = current_setting('app.current_user_id', true)::uuid);
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS properties_modify_policy ON properties;")
    op.execute("DROP POLICY IF EXISTS property_photos_access_policy ON property_photos;")
    op.execute("DROP POLICY IF EXISTS properties_access_policy ON properties;")
    op.execute("ALTER TABLE property_photos DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE properties DISABLE ROW LEVEL SECURITY;")
