"""Anchor model."""

import uuid
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from sqlalchemy.sql import func

from app.db.base import Base


class Anchor(Base):
    """Spatial anchor model."""
    __tablename__ = "anchors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    content_type = Column(String(50), nullable=False, default="text")  # text, image, video, audio
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    
    # Foreign key to auth service users
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Anchor(id={self.id}, title='{self.title}', user_id={self.user_id})>"
