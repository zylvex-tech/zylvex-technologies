"""Initial migration for mindmapper tables

Revision ID: 001_initial_migration
Revises: 
Create Date: 2024-04-11 08:14:24.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001_initial_migration"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create mindmaps table
    op.create_table(
        "mindmaps",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_mindmaps_user_id"), "mindmaps", ["user_id"], unique=False)

    # Create nodes table
    op.create_table(
        "nodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mindmap_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("focus_level", sa.Integer(), nullable=False),
        sa.Column("color", sa.String(length=20), nullable=False),
        sa.Column("x", sa.Float(), nullable=True),
        sa.Column("y", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["mindmap_id"], ["mindmaps.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["nodes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_nodes_mindmap_id"), "nodes", ["mindmap_id"], unique=False)
    op.create_index(op.f("ix_nodes_parent_id"), "nodes", ["parent_id"], unique=False)

    # Create sessions table
    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mindmap_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("avg_focus", sa.Float(), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column("node_count", sa.Integer(), nullable=False),
        sa.Column("focus_timeline", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["mindmap_id"], ["mindmaps.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_sessions_mindmap_id"), "sessions", ["mindmap_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_sessions_mindmap_id"), table_name="sessions")
    op.drop_table("sessions")
    op.drop_index(op.f("ix_nodes_parent_id"), table_name="nodes")
    op.drop_index(op.f("ix_nodes_mindmap_id"), table_name="nodes")
    op.drop_table("nodes")
    op.drop_index(op.f("ix_mindmaps_user_id"), table_name="mindmaps")
    op.drop_table("mindmaps")
