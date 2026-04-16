from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
import uuid


# ---- Follow schemas -------------------------------------------------------

class FollowResponse(BaseModel):
    follower_id: uuid.UUID
    following_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class UserListItem(BaseModel):
    """Minimal user entry returned in follower/following lists."""

    user_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedUserList(BaseModel):
    items: List[UserListItem]
    total: int
    skip: int
    limit: int


# ---- Feed schemas ---------------------------------------------------------

class AnchorFeedItem(BaseModel):
    """Anchor entry in the social feed."""

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    content: str
    content_type: str
    latitude: float
    longitude: float
    created_at: Optional[datetime] = None
    is_followed: bool = False
    reaction_count: int = 0


class TrendingItem(BaseModel):
    """Trending content item (anchor or mindmap)."""

    content_type: Literal["anchor", "mindmap"]
    content_id: uuid.UUID
    reaction_count: int


class TrendingFeedResponse(BaseModel):
    items: List[TrendingItem]
    window_days: int = 7


# ---- Reaction schemas -----------------------------------------------------

class ReactionCreate(BaseModel):
    content_type: Literal["anchor", "mindmap"] = Field(
        ..., description="Type of content being reacted to: 'anchor' or 'mindmap'"
    )
    content_id: uuid.UUID = Field(..., description="UUID of the anchor or mind map")
    emoji: str = Field(
        ...,
        description="Reaction emoji — one of: 👍 ❤️ 🔥 💡",
    )


class ReactionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    content_type: str
    content_id: uuid.UUID
    emoji: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReactionListResponse(BaseModel):
    reactions: List[ReactionResponse]
    total: int
