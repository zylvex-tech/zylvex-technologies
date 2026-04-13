"""Anchor service."""

import logging
from uuid import UUID
from sqlalchemy.orm import Session
from geoalchemy2 import WKTElement
from sqlalchemy import func

from models.anchor import Anchor
from schemas.anchor import AnchorCreate

logger = logging.getLogger(__name__)


class AnchorService:
    """Service for anchor operations."""
    
    @staticmethod
    def create_anchor(db: Session, anchor_data: AnchorCreate, user_id: UUID) -> Anchor:
        """Create a new anchor for authenticated user."""
        try:
            # Create WKT point for PostGIS
            point = WKTElement(f'POINT({anchor_data.longitude} {anchor_data.latitude})', srid=4326)
            
            anchor = Anchor(
                title=anchor_data.title,
                content=anchor_data.content,
                content_type=anchor_data.content_type,
                latitude=anchor_data.latitude,
                longitude=anchor_data.longitude,
                location=point,
                user_id=user_id
            )
            
            db.add(anchor)
            db.commit()
            db.refresh(anchor)
            
            logger.info(f"Created anchor {anchor.id} for user {user_id}")
            return anchor
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating anchor: {str(e)}")
            raise
    
    @staticmethod
    def get_anchors_nearby(db: Session, latitude: float, longitude: float, radius_km: float = 1.0,
                           skip: int = 0, limit: int = 100) -> list:
        """Get anchors within radius of a location."""
        try:
            # Convert km to degrees (equatorial approximation; 1° ≈ 111 km).
            # Note: Accuracy degrades at higher latitudes (~50% error at 60°N).
            # For production use, migrate to Geography('POINT', srid=4326) and
            # call ST_DWithin with radius in meters for meter-accurate results.
            radius_deg = radius_km / 111.0

            # Create point for distance calculation
            point = WKTElement(f'POINT({longitude} {latitude})', srid=4326)

            # Query anchors within radius using PostGIS ST_DWithin
            anchors = db.query(Anchor).filter(
                func.ST_DWithin(Anchor.location, point, radius_deg)
            ).order_by(Anchor.created_at.desc()).offset(skip).limit(limit).all()

            return anchors

        except Exception as e:
            logger.error(f"Error fetching nearby anchors: {str(e)}")
            raise
    
    @staticmethod
    def get_anchor_by_id(db: Session, anchor_id: UUID) -> Anchor:
        """Get anchor by ID."""
        return db.query(Anchor).filter(Anchor.id == anchor_id).first()
    
    @staticmethod
    def get_user_anchors(db: Session, user_id: UUID) -> list:
        """Get all anchors belonging to a user."""
        return db.query(Anchor).filter(Anchor.user_id == user_id).order_by(Anchor.created_at.desc()).all()
    
    @staticmethod
    def delete_anchor(db: Session, anchor_id: UUID, user_id: UUID) -> bool:
        """Delete anchor if it belongs to the user."""
        anchor = db.query(Anchor).filter(Anchor.id == anchor_id).first()
        
        if not anchor:
            return False
        
        if anchor.user_id != user_id:
            return False
        
        db.delete(anchor)
        db.commit()
        return True
