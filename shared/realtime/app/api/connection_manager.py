"""
ConnectionManager — tracks active WebSocket connections by user_id.

Architecture:
  - Each server instance maintains an in-process dict of user_id → [WebSocket].
  - Redis pub/sub is used as a fan-out bus so that multiple server instances
    can push events to users connected to *any* instance.
  - Channel pattern: zylvex:ws:<user_id>
  - The broadcast_to_user helper publishes to Redis; the subscriber loop
    receives the message and delivers it to locally connected sockets.

Event format (JSON string):
  {"event": "<event_type>", "data": {...}}

Supported push events:
  - new_anchor_nearby     — someone placed an anchor within 1 km
  - new_reaction          — someone reacted to your content
  - new_follower          — someone followed you
  - new_mindmap_node      — collaborator added a node to a shared map
"""

import asyncio
import json
import logging
from typing import Any

from fastapi import WebSocket

from app.core.config import settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and Redis pub/sub fan-out."""

    def __init__(self) -> None:
        # user_id (str) → list of active WebSocket connections
        self._connections: dict[str, list[WebSocket]] = {}
        self._redis_client = None
        self._pubsub = None
        self._subscriber_task: asyncio.Task | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def startup(self) -> None:
        """Connect to Redis and start the subscriber background task."""
        try:
            import redis.asyncio as aioredis

            self._redis_client = aioredis.from_url(
                settings.REDIS_URL, decode_responses=True
            )
            await self._redis_client.ping()
            self._pubsub = self._redis_client.pubsub()
            # Subscribe to the wildcard pattern for all user channels
            await self._pubsub.psubscribe(
                f"{settings.REDIS_CHANNEL_PREFIX}*"
            )
            self._subscriber_task = asyncio.create_task(
                self._redis_subscriber_loop()
            )
            logger.info("ConnectionManager: Redis pub/sub started")
        except Exception as exc:  # pragma: no cover
            logger.warning(
                "ConnectionManager: Redis unavailable (%s); "
                "falling back to in-process delivery only.",
                exc,
            )
            self._redis_client = None

    async def shutdown(self) -> None:
        """Cancel the subscriber task and close Redis connection."""
        if self._subscriber_task:
            self._subscriber_task.cancel()
            try:
                await self._subscriber_task
            except asyncio.CancelledError:
                pass
        if self._pubsub:
            await self._pubsub.close()
        if self._redis_client:
            await self._redis_client.aclose()

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        """Accept a WebSocket and register it for the given user."""
        await websocket.accept()
        self._connections.setdefault(user_id, []).append(websocket)
        logger.info("WS connected: user=%s total=%d", user_id, self.connection_count)

    async def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        """Remove a WebSocket from the registry."""
        sockets = self._connections.get(user_id, [])
        if websocket in sockets:
            sockets.remove(websocket)
        if not sockets:
            self._connections.pop(user_id, None)
        logger.info("WS disconnected: user=%s total=%d", user_id, self.connection_count)

    @property
    def connection_count(self) -> int:
        return sum(len(v) for v in self._connections.values())

    # ------------------------------------------------------------------
    # Publishing
    # ------------------------------------------------------------------

    async def broadcast_to_user(self, user_id: str, event: str, data: Any) -> None:
        """
        Publish an event to a specific user.

        1. Publishes to Redis so all server instances receive it.
        2. Also delivers directly to locally connected sockets as a fast-path.
        """
        payload = json.dumps({"event": event, "data": data})

        if self._redis_client:
            try:
                await self._redis_client.publish(
                    f"{settings.REDIS_CHANNEL_PREFIX}{user_id}", payload
                )
                return  # Redis subscriber loop handles local delivery
            except Exception as exc:  # pragma: no cover
                logger.warning("Redis publish failed (%s); delivering locally", exc)

        # Fallback: deliver directly (single-instance mode)
        await self._deliver_locally(user_id, payload)

    async def broadcast_to_users(
        self, user_ids: list[str], event: str, data: Any
    ) -> None:
        """Broadcast an event to multiple users."""
        for uid in user_ids:
            await self.broadcast_to_user(uid, event, data)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _deliver_locally(self, user_id: str, payload: str) -> None:
        """Send *payload* to all WebSocket connections for *user_id*."""
        dead: list[WebSocket] = []
        for ws in list(self._connections.get(user_id, [])):
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(user_id, ws)

    async def _redis_subscriber_loop(self) -> None:
        """Background task: relay Redis messages to local WebSocket connections."""
        prefix_len = len(settings.REDIS_CHANNEL_PREFIX)
        try:
            async for message in self._pubsub.listen():
                if message["type"] != "pmessage":
                    continue
                channel: str = message["channel"]
                user_id = channel[prefix_len:]
                payload: str = message["data"]
                await self._deliver_locally(user_id, payload)
        except asyncio.CancelledError:
            pass
        except Exception as exc:  # pragma: no cover
            logger.error("Redis subscriber loop error: %s", exc)


# Singleton instance shared across the application
manager = ConnectionManager()
