"""Mind map models."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class MindMap(Base):
    __tablename__ = "mindmaps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    nodes = relationship("Node", back_populates="mindmap", cascade="all, delete-orphan")
    sessions = relationship(
        "Session", back_populates="mindmap", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<MindMap(id={self.id}, title='{self.title}', user_id={self.user_id})>"


class Node(Base):
    __tablename__ = "nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mindmap_id = Column(
        UUID(as_uuid=True),
        ForeignKey("mindmaps.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("nodes.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    text = Column(Text, nullable=False)
    focus_level = Column(Integer, nullable=False)
    color = Column(String(20), nullable=False)
    x = Column(Float, default=0.0)
    y = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    mindmap = relationship("MindMap", back_populates="nodes")
    parent = relationship("Node", remote_side=[id], backref="children")

    def __repr__(self):
        return (
            f"<Node(id={self.id}, text='{self.text[:20]}', focus={self.focus_level})>"
        )


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mindmap_id = Column(
        UUID(as_uuid=True),
        ForeignKey("mindmaps.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    avg_focus = Column(Float, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    node_count = Column(Integer, nullable=False)
    focus_timeline = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    mindmap = relationship("MindMap", back_populates="sessions")

    def __repr__(self):
        return (
            f"<Session(id={self.id}, avg_focus={self.avg_focus},"
            f" duration={self.duration_seconds}s)>"
        )
