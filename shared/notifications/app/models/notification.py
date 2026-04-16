import uuid
import sqlalchemy as sa
from sqlalchemy import Uuid
from sqlalchemy.sql import func

from app.db.base import Base

# Notification types
NOTIFICATION_TYPES = frozenset(
    {"follow", "reaction", "nearby_anchor", "collaboration_invite"}
)


class Notification(Base):
    __tablename__ = "notifications"

    id = sa.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(Uuid(as_uuid=True), nullable=False, index=True)
    type = sa.Column(sa.String(50), nullable=False)
    title = sa.Column(sa.String(255), nullable=False)
    body = sa.Column(sa.Text, nullable=False)
    # JSONB on PostgreSQL; TEXT/JSON on SQLite (for tests)
    metadata_ = sa.Column("metadata", sa.JSON, nullable=True, default=dict)
    read = sa.Column(sa.Boolean, nullable=False, default=False, server_default="false")
    created_at = sa.Column(
        sa.DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        sa.Index("ix_notifications_user_created", "user_id", "created_at"),
    )

    def __repr__(self):
        return (
            f"<Notification(id={self.id}, user={self.user_id},"
            f" type={self.type}, read={self.read})>"
        )
