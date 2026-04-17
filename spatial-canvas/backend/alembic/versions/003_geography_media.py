"""migrate location Geometry to Geography and add media_url

Revision ID: 003_geography_media
Revises: update_anchor_user_id
Create Date: 2026-04-17 00:00:00.000000

Resolves ADR-002: PostGIS Geometry not Geography.
Geography type uses meters for ST_DWithin, providing accurate distance
calculations at all latitudes (Geometry was ~50% wrong at 60°N).
"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geography

# revision identifiers, used by Alembic.
revision = "003_geography_media"
down_revision = "update_anchor_user_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Part A: Migrate Geometry → Geography (ADR-002) ---

    # 1. Add new Geography column
    op.add_column(
        "anchors",
        sa.Column(
            "location_geo",
            Geography(geometry_type="POINT", srid=4326),
            nullable=True,
        ),
    )

    # 2. Copy existing Geometry data to Geography
    op.execute("UPDATE anchors SET location_geo = location::geography")

    # 3. Drop the old Geometry column
    op.drop_column("anchors", "location")

    # 4. Rename location_geo → location
    op.alter_column("anchors", "location_geo", new_column_name="location")

    # 5. Set NOT NULL after data migration
    op.alter_column("anchors", "location", nullable=False)

    # 6. Recreate spatial index (GIST on Geography)
    op.execute(
        "CREATE INDEX idx_anchors_location ON anchors USING GIST(location)"
    )

    # --- Part B: Add media_url column ---
    op.add_column(
        "anchors",
        sa.Column("media_url", sa.String(512), nullable=True),
    )


def downgrade() -> None:
    # Remove media_url
    op.drop_column("anchors", "media_url")

    # Revert Geography → Geometry
    op.execute("DROP INDEX IF EXISTS idx_anchors_location")

    op.add_column(
        "anchors",
        sa.Column(
            "location_geo",
            sa.Column("location_geo", sa.Text),  # placeholder for Geometry
            nullable=True,
        ),
    )
    op.execute("UPDATE anchors SET location_geo = location::geometry")
    op.drop_column("anchors", "location")
    op.alter_column("anchors", "location_geo", new_column_name="location")
    op.alter_column("anchors", "location", nullable=False)
    op.execute(
        "CREATE INDEX idx_anchors_location ON anchors USING GIST(location)"
    )
