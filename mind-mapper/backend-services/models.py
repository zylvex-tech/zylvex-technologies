import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class MindMap(Base):
    __tablename__ = "mindmaps"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # From auth service
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    nodes = relationship("Node", back_populates="mindmap", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="mindmap", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MindMap(id={self.id}, title='{self.title}', user_id={self.user_id})>"


class Node(Base):
    __tablename__ = "nodes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mindmap_id = Column(UUID(as_uuid=True), ForeignKey("mindmaps.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=True, index=True)
    text = Column(Text, nullable=False)
    focus_level = Column(Integer, nullable=False)  # 0-100
    color = Column(String(20), nullable=False)  # 'green', 'yellow', 'red' based on focus
    x = Column(Float, default=0.0)  # X position in canvas
    y = Column(Float, default=0.0)  # Y position in canvas
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    mindmap = relationship("MindMap", back_populates="nodes")
    parent = relationship("Node", remote_side=[id], backref="children")
    
    def __repr__(self):
        return f"<Node(id={self.id}, text='{self.text[:20]}...', focus={self.focus_level})>"


class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mindmap_id = Column(UUID(as_uuid=True), ForeignKey("mindmaps.id", ondelete="CASCADE"), nullable=False, index=True)
    avg_focus = Column(Float, nullable=False)  # Average focus level 0-100
    duration_seconds = Column(Integer, nullable=False)  # Session duration in seconds
    node_count = Column(Integer, nullable=False)  # Total nodes created
    focus_timeline = Column(JSON, nullable=False)  # List of focus levels over time
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    mindmap = relationship("MindMap", back_populates="sessions")
    
    def __repr__(self):
        return f"<Session(id={self.id}, avg_focus={self.avg_focus}, duration={self.duration_seconds}s)>"
