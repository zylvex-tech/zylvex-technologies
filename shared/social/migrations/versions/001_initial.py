"""initial social graph schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create content_type enum
    content_type_enum = postgresql.ENUM(
        "anchor", "mindmap", name="content_type_enum", create_type=True
    )
    content_type_enum.create(op.get_bind(), checkfirst=True)

    # Create follows table
    op.create_table(
        "follows",
        sa.Column("follower_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("following_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("follower_id", "following_id"),
    )
    op.create_index("ix_follows_follower_id", "follows", ["follower_id"])
    op.create_index("ix_follows_following_id", "follows", ["following_id"])

    # Create reactions table
    op.create_table(
        "reactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "content_type",
            sa.Enum("anchor", "mindmap", name="content_type_enum", create_type=False),
            nullable=False,
        ),
        sa.Column("content_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("emoji", sa.String(length=10), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "content_type",
            "content_id",
            name="uq_reaction_per_user_content",
        ),
    )
    op.create_index("ix_reactions_user_id", "reactions", ["user_id"])
    op.create_index(
        "ix_reactions_content", "reactions", ["content_type", "content_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_reactions_content", table_name="reactions")
    op.drop_index("ix_reactions_user_id", table_name="reactions")
    op.drop_table("reactions")
    op.drop_index("ix_follows_following_id", table_name="follows")
    op.drop_index("ix_follows_follower_id", table_name="follows")
    op.drop_table("follows")
    sa.Enum(name="content_type_enum").drop(op.get_bind(), checkfirst=True)
