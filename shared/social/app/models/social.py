import uuid
import sqlalchemy as sa
from sqlalchemy import Uuid
from sqlalchemy.sql import func

from app.db.base import Base

VALID_EMOJIS = frozenset({"👍", "❤️", "🔥", "💡"})

# content_type_enum: create_type=False lets the migration control type creation
# while SQLite tests use it as a plain VARCHAR check constraint
_content_type_enum = sa.Enum(
    "anchor", "mindmap", name="content_type_enum", create_type=False
)


class Follow(Base):
    __tablename__ = "follows"

    follower_id = sa.Column(
        Uuid(as_uuid=True), nullable=False, primary_key=True
    )
    following_id = sa.Column(
        Uuid(as_uuid=True), nullable=False, primary_key=True
    )
    created_at = sa.Column(
        sa.DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        sa.Index("ix_follows_follower_id", "follower_id"),
        sa.Index("ix_follows_following_id", "following_id"),
    )

    def __repr__(self):
        return f"<Follow({self.follower_id} -> {self.following_id})>"


class Reaction(Base):
    __tablename__ = "reactions"

    id = sa.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(Uuid(as_uuid=True), nullable=False, index=True)
    content_type = sa.Column(
        sa.Enum("anchor", "mindmap", name="content_type_enum", create_type=False),
        nullable=False,
    )
    content_id = sa.Column(Uuid(as_uuid=True), nullable=False)
    emoji = sa.Column(sa.String(10), nullable=False)
    created_at = sa.Column(
        sa.DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "user_id", "content_type", "content_id", name="uq_reaction_per_user_content"
        ),
        sa.Index("ix_reactions_content", "content_type", "content_id"),
    )

    def __repr__(self):
        return (
            f"<Reaction(id={self.id}, user={self.user_id},"
            f" {self.content_type}/{self.content_id}, {self.emoji})>"
        )
