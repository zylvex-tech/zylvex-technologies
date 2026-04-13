"""Anchor schemas."""

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class AnchorBase(BaseModel):
    """Base anchor schema."""

    title: str = Field(..., min_length=1, max_length=255, description="Anchor title")
    content: Optional[str] = Field(None, description="Anchor content (text, URL, etc.)")
    content_type: str = Field(
        "text", description="Content type: text, image, video, audio"
    )
    latitude: float = Field(
        ..., ge=-90, le=90, description="Latitude in decimal degrees"
    )
    longitude: float = Field(
        ..., ge=-180, le=180, description="Longitude in decimal degrees"
    )

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v):
        allowed_types = ["text", "image", "video", "audio"]
        if v not in allowed_types:
            raise ValueError(f"content_type must be one of {allowed_types}")
        return v


class AnchorCreate(AnchorBase):
    """Schema for creating an anchor."""

    # Note: user_id is no longer accepted from request body
    # It will be extracted from JWT token
    pass


class AnchorResponse(AnchorBase):
    """Schema for anchor response."""

    id: UUID
    user_id: UUID
    owner_name: Optional[str] = Field(None, description="Full name of anchor owner")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnchorListResponse(BaseModel):
    """Schema for list of anchors response."""

    anchors: list[AnchorResponse]
    count: int
    radius_km: float
