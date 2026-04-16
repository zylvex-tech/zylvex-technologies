"""Tests for the Redis token cache integration in spatial-canvas deps.py.

Covers:
1. Cache hit  — auth service is NOT called when a valid cache entry exists
2. Cache miss — auth service IS called, result is stored in cache
3. Redis fallback — Redis unreachable, falls through to auth service without error
4. Expired/evicted entry — treated as cache miss, auth service re-verified
"""

import json
import os
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("AUTH_SERVICE_URL", "http://localhost:8001")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")

from app.core.token_cache import _token_key, set_cached_user

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TOKEN = "test-bearer-token-spatial"
USER_ID = str(uuid.uuid4())
USER_DATA = {"id": USER_ID, "email": "spatial@test.com", "roles": ["user"]}
CACHED_PAYLOAD = json.dumps({"user_id": USER_ID, "roles": ["user"]})


# ---------------------------------------------------------------------------
# 1. Cache HIT — auth service must not be called
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_current_user_cache_hit():
    """When Redis returns a cached entry the auth service must not be called."""
    mock_redis = MagicMock()
    mock_redis.get.return_value = CACHED_PAYLOAD

    with patch("app.api.deps._redis_client", mock_redis):
        from app.api.deps import get_current_user
        from fastapi.security import HTTPAuthorizationCredentials

        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=TOKEN)

        with patch("app.api.deps.httpx.AsyncClient") as mock_httpx:
            result = await get_current_user(creds)

        # Cache was hit so httpx must never have been invoked
        mock_httpx.assert_not_called()
        assert result["id"] == USER_ID


# ---------------------------------------------------------------------------
# 2. Cache MISS — auth service called, result stored in cache
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_current_user_cache_miss_calls_auth_service():
    """On cache miss the auth service is called and the result is cached."""
    mock_redis = MagicMock()
    mock_redis.get.return_value = None  # cache miss

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = USER_DATA

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch("app.api.deps._redis_client", mock_redis):
        with patch("app.api.deps.httpx.AsyncClient", return_value=mock_client):
            from app.api.deps import get_current_user
            from fastapi.security import HTTPAuthorizationCredentials

            creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=TOKEN)
            result = await get_current_user(creds)

    # Auth service must have been called
    mock_client.get.assert_called_once()
    # Cache must have been populated
    mock_redis.setex.assert_called_once()
    assert result == USER_DATA


# ---------------------------------------------------------------------------
# 3. Redis FALLBACK — Redis unreachable, falls through to auth service
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_current_user_redis_fallback():
    """When Redis raises an error the request falls through to the auth service."""
    mock_redis = MagicMock()
    mock_redis.get.side_effect = ConnectionError("Redis is down")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = USER_DATA

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch("app.api.deps._redis_client", mock_redis):
        with patch("app.api.deps.httpx.AsyncClient", return_value=mock_client):
            from app.api.deps import get_current_user
            from fastapi.security import HTTPAuthorizationCredentials

            creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=TOKEN)
            # Must not raise even though Redis is down
            result = await get_current_user(creds)

    assert result == USER_DATA
    # Auth service must have been called despite Redis error
    mock_client.get.assert_called_once()


# ---------------------------------------------------------------------------
# 4. Expired / evicted entry — treated as cache miss, re-verified
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_current_user_expired_entry_revalidates():
    """An expired cache entry (key gone after TTL) is treated as a cache miss."""
    mock_redis = MagicMock()
    # Simulate key expiry — Redis returns None for an expired key
    mock_redis.get.return_value = None

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = USER_DATA

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch("app.api.deps._redis_client", mock_redis):
        with patch("app.api.deps.httpx.AsyncClient", return_value=mock_client):
            from app.api.deps import get_current_user
            from fastapi.security import HTTPAuthorizationCredentials

            creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=TOKEN)
            result = await get_current_user(creds)

    # Should have gone to auth service and re-populated the cache
    mock_client.get.assert_called_once()
    mock_redis.setex.assert_called_once()
    assert result == USER_DATA
