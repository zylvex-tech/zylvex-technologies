"""Anchor endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import logging

from app.db.session import get_db
from schemas.anchor import AnchorCreate, AnchorResponse, AnchorListResponse
from services.anchor import AnchorService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=AnchorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new anchor",
    description="Create a new spatial anchor with content and location data."
)
def create_anchor(
    anchor_data: AnchorCreate,
    db: Session = Depends(get_db)
):
    """Create a new anchor."""
    try:
        logger.info(f"Creating anchor for user: {anchor_data.user_id}")
        anchor = AnchorService.create_anchor(db, anchor_data)
        return anchor
    except Exception as e:
        logger.error(f"Error creating anchor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create anchor: {str(e)}"
        )


@router.get(
    "",
    response_model=AnchorListResponse,
    summary="Get anchors nearby",
    description="Get anchors within specified radius of a location."
)
def get_anchors_nearby(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees"),
    radius_km: float = Query(1.0, ge=0.1, le=100, description="Search radius in kilometers"),
    db: Session = Depends(get_db)
):
    """Get anchors within radius of a location."""
    try:
        logger.info(f"Searching anchors near ({latitude}, {longitude}) within {radius_km}km")
        
        anchors = AnchorService.get_anchors_nearby(
            db=db,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km
        )
        
        return AnchorListResponse(
            anchors=anchors,
            count=len(anchors),
            radius_km=radius_km
        )
    except Exception as e:
        logger.error(f"Error fetching anchors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch anchors: {str(e)}"
        )


@router.get(
    "/{anchor_id}",
    response_model=AnchorResponse,
    summary="Get anchor by ID",
    description="Get a specific anchor by its ID."
)
def get_anchor(
    anchor_id: str,
    db: Session = Depends(get_db)
):
    """Get anchor by ID."""
    try:
        from uuid import UUID
        anchor_uuid = UUID(anchor_id)
        anchor = AnchorService.get_anchor_by_id(db, anchor_uuid)
        
        if not anchor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Anchor with ID {anchor_id} not found"
            )
        
        return anchor
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid anchor ID format"
        )
    except Exception as e:
        logger.error(f"Error fetching anchor {anchor_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch anchor: {str(e)}"
        )
