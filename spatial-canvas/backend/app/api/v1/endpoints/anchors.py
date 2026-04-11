"""Anchor endpoints."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import logging

from app.db.session import get_db
from app.api.deps import get_current_user_id, get_current_user_name
from schemas.anchor import AnchorCreate, AnchorResponse, AnchorListResponse
from services.anchor import AnchorService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=AnchorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new anchor",
    description="Create a new spatial anchor with content and location data. Requires authentication."
)
async def create_anchor(
    anchor_data: AnchorCreate,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new anchor for authenticated user."""
    try:
        logger.info(f"Creating anchor for user: {user_id}")
        anchor = AnchorService.create_anchor(db, anchor_data, user_id)
        
        # Convert to response model
        return AnchorResponse(
            id=anchor.id,
            user_id=anchor.user_id,
            title=anchor.title,
            content=anchor.content,
            content_type=anchor.content_type,
            latitude=anchor.latitude,
            longitude=anchor.longitude,
            created_at=anchor.created_at,
            updated_at=anchor.updated_at
        )
        
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
    description="Get anchors within specified radius of a location. Public endpoint."
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
        
        # Convert to response models with owner names
        # Note: In production, we would fetch owner names from auth service
        # For now, we'll return without owner names
        anchor_responses = []
        for anchor in anchors:
            anchor_responses.append(
                AnchorResponse(
                    id=anchor.id,
                    user_id=anchor.user_id,
                    title=anchor.title,
                    content=anchor.content,
                    content_type=anchor.content_type,
                    latitude=anchor.latitude,
                    longitude=anchor.longitude,
                    created_at=anchor.created_at,
                    updated_at=anchor.updated_at
                )
            )
        
        return AnchorListResponse(
            anchors=anchor_responses,
            count=len(anchor_responses),
            radius_km=radius_km
        )
    except Exception as e:
        logger.error(f"Error fetching anchors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch anchors: {str(e)}"
        )


@router.get(
    "/mine",
    response_model=List[AnchorResponse],
    summary="Get my anchors",
    description="Get all anchors belonging to the currently authenticated user."
)
async def get_my_anchors(
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get anchors belonging to the current user."""
    try:
        logger.info(f"Getting anchors for user: {user_id}")
        anchors = AnchorService.get_user_anchors(db, user_id)
        
        anchor_responses = []
        for anchor in anchors:
            anchor_responses.append(
                AnchorResponse(
                    id=anchor.id,
                    user_id=anchor.user_id,
                    title=anchor.title,
                    content=anchor.content,
                    content_type=anchor.content_type,
                    latitude=anchor.latitude,
                    longitude=anchor.longitude,
                    created_at=anchor.created_at,
                    updated_at=anchor.updated_at
                )
            )
        
        return anchor_responses
        
    except Exception as e:
        logger.error(f"Error fetching user anchors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user anchors: {str(e)}"
        )


@router.delete(
    "/{anchor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an anchor",
    description="Delete an anchor if it belongs to the current user."
)
async def delete_anchor(
    anchor_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete anchor if it belongs to the current user."""
    try:
        logger.info(f"Attempting to delete anchor {anchor_id} for user {user_id}")
        
        success = AnchorService.delete_anchor(db, anchor_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Anchor not found or you don't have permission to delete it"
            )
        
        # Return 204 No Content on success
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting anchor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete anchor: {str(e)}"
        )


@router.get(
    "/{anchor_id}",
    response_model=AnchorResponse,
    summary="Get anchor by ID",
    description="Get a specific anchor by its ID. Public endpoint."
)
def get_anchor(
    anchor_id: UUID,
    db: Session = Depends(get_db)
):
    """Get anchor by ID."""
    try:
        anchor = AnchorService.get_anchor_by_id(db, anchor_id)
        
        if not anchor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Anchor with ID {anchor_id} not found"
            )
        
        return AnchorResponse(
            id=anchor.id,
            user_id=anchor.user_id,
            title=anchor.title,
            content=anchor.content,
            content_type=anchor.content_type,
            latitude=anchor.latitude,
            longitude=anchor.longitude,
            created_at=anchor.created_at,
            updated_at=anchor.updated_at
        )
    except Exception as e:
        logger.error(f"Error fetching anchor {anchor_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch anchor: {str(e)}"
        )
