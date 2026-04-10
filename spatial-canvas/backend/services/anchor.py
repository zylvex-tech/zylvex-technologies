"""Anchor service for business logic."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2.functions import ST_MakePoint, ST_DistanceSphere

from app.db.base import Base
from models.anchor import Anchor
from schemas.anchor import AnchorCreate, AnchorUpdate


class AnchorService:
    """Service for anchor operations."""
    
    @staticmethod
    def create_anchor(db: Session, anchor_data: AnchorCreate) -> Anchor:
        """Create a new anchor."""
        
        # Create geometry point from lat/lng/alt
        location = func.ST_SetSRID(
            ST_MakePoint(
                anchor_data.longitude,
                anchor_data.latitude,
                anchor_data.altitude or 0.0
            ),
            4326
        )
        
        db_anchor = Anchor(
            user_id=anchor_data.user_id,
            content_type=anchor_data.content_type,
            content_data=anchor_data.content_data,
            title=anchor_data.title,
            description=anchor_data.description,
            latitude=anchor_data.latitude,
            longitude=anchor_data.longitude,
            altitude=anchor_data.altitude or 0.0,
            location=location,
            is_active='Y'
        )
        
        db.add(db_anchor)
        db.commit()
        db.refresh(db_anchor)
        
        return db_anchor
    
    @staticmethod
    def get_anchors_nearby(
        db: Session,
        latitude: float,
        longitude: float,
        radius_km: float = 1.0,
        limit: int = 100
    ) -> List[Anchor]:
        """Get anchors within radius of a point."""
        
        # Convert km to meters (ST_DistanceSphere returns meters)
        radius_meters = radius_km * 1000
        
        # Create reference point
        reference_point = func.ST_SetSRID(
            ST_MakePoint(longitude, latitude, 0),
            4326
        )
        
        # Query anchors within radius
        query = db.query(Anchor).filter(
            Anchor.is_active == 'Y',
            func.ST_DistanceSphere(Anchor.location, reference_point) <= radius_meters
        ).order_by(
            func.ST_DistanceSphere(Anchor.location, reference_point)
        ).limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_anchor_by_id(db: Session, anchor_id: UUID) -> Optional[Anchor]:
        """Get anchor by ID."""
        return db.query(Anchor).filter(
            Anchor.id == anchor_id,
            Anchor.is_active == 'Y'
        ).first()
    
    @staticmethod
    def update_anchor(
        db: Session,
        anchor_id: UUID,
        update_data: AnchorUpdate
    ) -> Optional[Anchor]:
        """Update an anchor."""
        db_anchor = AnchorService.get_anchor_by_id(db, anchor_id)
        if not db_anchor:
            return None
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(db_anchor, field, value)
        
        db.commit()
        db.refresh(db_anchor)
        
        return db_anchor
    
    @staticmethod
    def delete_anchor(db: Session, anchor_id: UUID) -> bool:
        """Soft delete an anchor."""
        db_anchor = AnchorService.get_anchor_by_id(db, anchor_id)
        if not db_anchor:
            return False
        
        db_anchor.is_active = 'N'
        db.commit()
        
        return True
