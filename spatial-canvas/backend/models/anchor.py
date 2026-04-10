"""Anchor model for spatial AR content."""

from sqlalchemy import Column, String, Float, DateTime, UUID, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from geoalchemy2 import Geometry

from app.db.base import Base


class Anchor(Base):
    """Model representing a spatial anchor in AR."""
    
    __tablename__ = "anchors"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(String(255), nullable=False, index=True)
    
    # Content
    content_type = Column(String(50), nullable=False)  # '3d_object', 'text', 'image', 'video'
    content_data = Column(Text, nullable=False)  # JSON string or URL
    title = Column(String(255))
    description = Column(Text)
    
    # Spatial data
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, default=0.0)
    
    # PostGIS geometry for spatial queries
    location = Column(
        Geometry(geometry_type='POINTZ', srid=4326),
        nullable=False
    )
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(String(1), default='Y', nullable=False)
    
    def __repr__(self):
        return f"<Anchor(id={self.id}, title='{self.title}', lat={self.latitude}, lng={self.longitude})>"
