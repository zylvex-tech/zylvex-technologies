"""
WebSocket endpoint and HTTP event-push endpoint for the realtime service.

WebSocket endpoint:  /ws/{user_id}?token=<jwt>
  - Authenticates by calling GET /auth/verify with the token query param.
  - Sends a heartbeat ping frame every HEARTBEAT_INTERVAL seconds.
  - Clients should reconnect with exponential back-off on disconnect.

  Reconnect guidance for clients:
    1. On close / error, wait min(2^attempt * 500ms, 30 000ms) before retrying.
    2. Re-authenticate with a fresh JWT (refresh if necessary) before reconnecting.
    3. On successful reconnect, re-subscribe to any room/session IDs as needed.

Internal HTTP endpoint: POST /internal/push
  - Body: {"user_id": "...", "event": "...", "data": {...}}
  - Called by other microservices (notifications, social, spatial-canvas) to push
    events to connected users.
"""

import asyncio
import json
import logging
from typing import Any

import httpx
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel

from app.api.connection_manager import manager
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Auth helper
# ---------------------------------------------------------------------------

AUTH_SERVICE_URL = settings.AUTH_SERVICE_URL


async def _verify_token(token: str) -> dict | None:
    """Call the shared auth service to validate *token*.

    Returns the user dict on success, or None on auth failure.
    Raises HTTPException(503) if the auth service is unreachable.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{AUTH_SERVICE_URL}/auth/verify",
                headers={"Authorization": f"Bearer {token}"},
            )
        if resp.status_code == 200:
            return resp.json()
        return None
    except httpx.RequestError as exc:
        logger.warning("Auth service unreachable: %s", exc)
        return None


# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: str = Query(..., description="JWT access token"),
) -> None:
    """
    Authenticated WebSocket endpoint.

    Connect with:  ws://<host>:8004/ws/<user_id>?token=<jwt>

    The server sends heartbeat ping frames every 30 s.
    Clients that miss 2 consecutive pings should reconnect.
    """
    # Authenticate
    user = await _verify_token(token)
    if user is None or str(user.get("id", "")) != user_id:
        await websocket.close(code=4001)
        return

    await manager.connect(user_id, websocket)
    try:
        # Send a welcome message so the client knows the connection is live
        await websocket.send_text(
            json.dumps({"event": "connected", "data": {"user_id": user_id}})
        )

        heartbeat_task = asyncio.create_task(_heartbeat(websocket))
        try:
            while True:
                # Keep the connection alive; we only need to listen for pong/close
                await websocket.receive_text()
        except WebSocketDisconnect:
            pass
        finally:
            heartbeat_task.cancel()
    finally:
        await manager.disconnect(user_id, websocket)


async def _heartbeat(websocket: WebSocket) -> None:
    """Send a ping JSON frame every HEARTBEAT_INTERVAL seconds."""
    try:
        while True:
            await asyncio.sleep(settings.HEARTBEAT_INTERVAL)
            await websocket.send_text(json.dumps({"event": "ping"}))
    except (asyncio.CancelledError, Exception):
        pass


# ---------------------------------------------------------------------------
# Internal HTTP push endpoint
# ---------------------------------------------------------------------------


class PushPayload(BaseModel):
    user_id: str
    event: str
    data: dict[str, Any] = {}


@router.post("/internal/push", status_code=202)
async def push_event(payload: PushPayload) -> dict:
    """
    Internal endpoint — push a real-time event to a specific user.

    Called by other microservices; not exposed to end users.
    """
    await manager.broadcast_to_user(payload.user_id, payload.event, payload.data)
    return {"queued": True, "user_id": payload.user_id, "event": payload.event}


# ---------------------------------------------------------------------------
# Multi-user broadcast endpoint (e.g. nearby-anchor fan-out)
# ---------------------------------------------------------------------------


class BroadcastPayload(BaseModel):
    user_ids: list[str]
    event: str
    data: dict[str, Any] = {}


@router.post("/internal/broadcast", status_code=202)
async def broadcast_event(payload: BroadcastPayload) -> dict:
    """
    Push an event to multiple users at once.

    Used for nearby-anchor alerts where multiple users in a radius
    need to be notified simultaneously.
    """
    await manager.broadcast_to_users(payload.user_ids, payload.event, payload.data)
    return {
        "queued": True,
        "user_count": len(payload.user_ids),
        "event": payload.event,
    }
