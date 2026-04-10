"""Anchor schemas."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, validator


class AnchorBase(BaseModel):
    """Base anchor schema."""
    
    content_type: str = Field(..., description="Type of content: '3d_object', 'text', 'image', 'video'")
    content_data: str = Field(..., description="JSON string or URL to content")
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    altitude: Optional[float] = Field(0.0, description="Altitude in meters")
    
    @validator('content_type')
    def validate_content_type(cls, v):
        valid_types = ['3d_object', 'text', 'image', 'video']
        if v not in valid_types:
            raise ValueError(f'content_type must be one of {valid_types}')
        return v


class AnchorCreate(AnchorBase):
    """Schema for creating an anchor."""
    user_id: str = Field(..., description="User identifier")


class AnchorUpdate(BaseModel):
    """Schema for updating an anchor."""
    
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    is_active: Optional[str] = Field(None, pattern='^[YN]$')


class AnchorResponse(AnchorBase):
    """Schema for anchor response."""
    
    id: UUID
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: str
    
    class Config:
        from_attributes = True


class AnchorListResponse(BaseModel):
    """Schema for list of anchors response."""
    
    anchors: List[AnchorResponse]
    count: int
    radius_km: float
