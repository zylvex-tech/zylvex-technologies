from datetime import datetime
from typing import Any
import uuid

from pydantic import BaseModel, Field


class NotificationSendRequest(BaseModel):
    """Internal request body for POST /notifications/send."""

    user_id: str
    type: str
    title: str
    body: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    body: str
    metadata: dict[str, Any]
    read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedNotifications(BaseModel):
    items: list[NotificationResponse]
    total: int
    page: int
    page_size: int
