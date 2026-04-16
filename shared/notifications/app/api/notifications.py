"""
Notifications REST API endpoints.

POST  /notifications/send              Internal — queue a notification
GET   /notifications/me                Paginated list for authenticated user
POST  /notifications/mark-read/{id}    Mark one notification as read
POST  /notifications/mark-all-read     Mark all of the user's notifications as read
"""

import asyncio
import uuid
import logging
from typing import Any

import httpx
import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.email_templates.sender import maybe_send_notification_email
from app.models.notification import Notification, NOTIFICATION_TYPES
from app.push import send_push_notification
from app.schemas.notification import (
    NotificationResponse,
    NotificationSendRequest,
    PaginatedNotifications,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _to_response(n: Notification) -> NotificationResponse:
    return NotificationResponse(
        id=str(n.id),
        user_id=str(n.user_id),
        type=n.type,
        title=n.title,
        body=n.body,
        metadata=n.metadata_ or {},
        read=n.read,
        created_at=n.created_at,
    )


async def _push_realtime(user_id: str, notification: NotificationResponse) -> None:
    """Fire-and-forget: push event to realtime gateway (best-effort)."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            await client.post(
                f"{settings.REALTIME_SERVICE_URL}/internal/push",
                json={
                    "user_id": user_id,
                    "event": f"new_{notification.type}",
                    "data": {
                        "id": notification.id,
                        "type": notification.type,
                        "title": notification.title,
                        "body": notification.body,
                        "metadata": notification.metadata,
                    },
                },
            )
    except Exception as exc:
        logger.debug("Realtime push skipped: %s", exc)


# ---------------------------------------------------------------------------
# POST /notifications/send  (internal)
# ---------------------------------------------------------------------------


@router.post("/send", status_code=201, response_model=NotificationResponse)
async def send_notification(
    payload: NotificationSendRequest,
    db: Session = Depends(get_db),
) -> NotificationResponse:
    """
    Internal endpoint — called by other microservices to create a notification.

    Not authenticated with a user JWT; relies on network-level trust
    (internal Docker network).
    """
    if payload.type not in NOTIFICATION_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid notification type. Must be one of: {sorted(NOTIFICATION_TYPES)}",
        )

    notif = Notification(
        user_id=uuid.UUID(payload.user_id),
        type=payload.type,
        title=payload.title,
        body=payload.body,
        metadata_=payload.metadata,
        read=False,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    resp = _to_response(notif)

    # Fire side-effects asynchronously (best-effort; never block the response)
    user_email = payload.metadata.get("user_email", "")
    user_name = payload.metadata.get("user_name", "User")

    asyncio.create_task(
        maybe_send_notification_email(
            notification_type=payload.type,
            user_email=user_email,
            user_name=user_name,
            title=payload.title,
            body=payload.body,
            metadata=payload.metadata,
        )
    )
    asyncio.create_task(
        send_push_notification(
            user_id=payload.user_id,
            notification_type=payload.type,
            title=payload.title,
            body=payload.body,
            metadata=payload.metadata,
        )
    )
    asyncio.create_task(_push_realtime(payload.user_id, resp))

    return resp


# ---------------------------------------------------------------------------
# GET /notifications/me  (authenticated)
# ---------------------------------------------------------------------------


@router.get("/me", response_model=PaginatedNotifications)
def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> PaginatedNotifications:
    """Return a paginated list of notifications for the authenticated user."""
    user_id = uuid.UUID(current_user["id"])

    query = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        query = query.filter(Notification.read == False)  # noqa: E712

    total = query.count()
    items = (
        query.order_by(Notification.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedNotifications(
        items=[_to_response(n) for n in items],
        total=total,
        page=page,
        page_size=page_size,
    )


# ---------------------------------------------------------------------------
# POST /notifications/mark-read/{id}  (authenticated)
# ---------------------------------------------------------------------------


@router.post("/mark-read/{notification_id}", response_model=NotificationResponse)
def mark_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> NotificationResponse:
    """Mark a single notification as read. Returns 404 if not found or not owned."""
    try:
        nid = uuid.UUID(notification_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    user_id = uuid.UUID(current_user["id"])
    notif = (
        db.query(Notification)
        .filter(Notification.id == nid, Notification.user_id == user_id)
        .first()
    )
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    notif.read = True
    db.commit()
    db.refresh(notif)
    return _to_response(notif)


# ---------------------------------------------------------------------------
# POST /notifications/mark-all-read  (authenticated)
# ---------------------------------------------------------------------------


@router.post("/mark-all-read", status_code=200)
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Mark all unread notifications as read for the authenticated user."""
    user_id = uuid.UUID(current_user["id"])
    updated = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.read == False)  # noqa: E712
        .update({"read": True})
    )
    db.commit()
    return {"marked_read": updated}
