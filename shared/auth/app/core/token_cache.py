"""Redis-backed token verification cache.

Caches the result of /auth/verify calls so downstream services avoid
hitting the auth service (and its database) on every request.

Key   : ``auth:token:{sha256(raw_token)}``
Value : JSON-encoded dict ``{"user_id": str, "roles": list}``
TTL   : TOKEN_CACHE_TTL seconds (default 300 s / 5 min)
"""

import hashlib
import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

TOKEN_CACHE_TTL = 300  # seconds
_KEY_PREFIX = "auth:token:"


def _token_key(token: str) -> str:
    """Return the Redis key for a given raw bearer token."""
    digest = hashlib.sha256(token.encode()).hexdigest()
    return f"{_KEY_PREFIX}{digest}"


def _make_redis_client(redis_url: str):
    """Create a synchronous Redis client.  Returns ``None`` on import error."""
    try:
        import redis as redis_lib  # type: ignore

        return redis_lib.from_url(redis_url, decode_responses=True, socket_connect_timeout=2)
    except ImportError:
        logger.warning("redis package is not installed; token caching disabled.")
        return None


def get_cached_user(redis_client: Any, token: str) -> Optional[Dict]:
    """Return cached user dict for *token*, or ``None`` on cache miss / error."""
    if redis_client is None:
        return None
    try:
        raw = redis_client.get(_token_key(token))
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as exc:
        logger.warning("Redis cache get failed (falling through to auth service): %s", exc)
        return None


def set_cached_user(redis_client: Any, token: str, user_data: Dict, ttl: int = TOKEN_CACHE_TTL) -> None:
    """Store *user_data* in Redis under the sha256 of *token* with the given TTL."""
    if redis_client is None:
        return
    try:
        payload = json.dumps({"user_id": user_data.get("id") or user_data.get("user_id"), "roles": user_data.get("roles", [])})
        redis_client.setex(_token_key(token), ttl, payload)
    except Exception as exc:
        logger.warning("Redis cache set failed (non-fatal): %s", exc)


def invalidate_cached_token(redis_client: Any, token: str) -> None:
    """Remove a token from the cache (e.g. on logout)."""
    if redis_client is None:
        return
    try:
        redis_client.delete(_token_key(token))
    except Exception as exc:
        logger.warning("Redis cache delete failed (non-fatal): %s", exc)
