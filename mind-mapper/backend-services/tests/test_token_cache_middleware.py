"""Tests for the Redis token cache integration in mind-mapper auth middleware.

Covers:
1. Cache hit  — auth service is NOT called when a valid cache entry exists
2. Cache miss — auth service IS called, result is stored in cache
3. Redis fallback — Redis unreachable, falls through to auth service
4. Expired/evicted entry — treated as cache miss, re-verified
"""

import json
import os
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("AUTH_SERVICE_URL", "http://localhost:8001")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")

from app.core.token_cache import _token_key

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TOKEN = "test-bearer-token-mindmapper"
USER_SUB = str(uuid.uuid4())
AUTH_VERIFY_RESPONSE = {"sub": USER_SUB, "email": "mm@test.com"}
CACHED_PAYLOAD = json.dumps({"user_id": USER_SUB, "roles": []})


# ---------------------------------------------------------------------------
# 1. Cache HIT — auth service must not be called
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_current_user_id_cache_hit():
    """When Redis returns a cached entry the auth service must not be called."""
    mock_redis = MagicMock()
    mock_redis.get.return_value = CACHED_PAYLOAD

    with patch("app.middleware.auth._redis_client", mock_redis):
        from app.middleware.auth import get_current_user_id

        with patch("app.middleware.auth.httpx.AsyncClient") as mock_httpx:
            result = await get_current_user_id(f"Bearer {TOKEN}")

    mock_httpx.assert_not_called()
    assert result == uuid.UUID(USER_SUB)


# ---------------------------------------------------------------------------
# 2. Cache MISS — auth service called, result stored in cache
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_current_user_id_cache_miss_calls_auth_service():
    """On cache miss the auth service is called and the result is cached."""
    mock_redis = MagicMock()
    mock_redis.get.return_value = None  # cache miss

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = AUTH_VERIFY_RESPONSE

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch("app.middleware.auth._redis_client", mock_redis):
        with patch("app.middleware.auth.httpx.AsyncClient", return_value=mock_client):
            from app.middleware.auth import get_current_user_id

            result = await get_current_user_id(f"Bearer {TOKEN}")

    mock_client.get.assert_called_once()
    mock_redis.setex.assert_called_once()
    assert result == uuid.UUID(USER_SUB)


# ---------------------------------------------------------------------------
# 3. Redis FALLBACK — Redis unreachable, falls through to auth service
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_current_user_id_redis_fallback():
    """When Redis raises an error the request falls through to the auth service."""
    mock_redis = MagicMock()
    mock_redis.get.side_effect = ConnectionError("Redis is down")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = AUTH_VERIFY_RESPONSE

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch("app.middleware.auth._redis_client", mock_redis):
        with patch("app.middleware.auth.httpx.AsyncClient", return_value=mock_client):
            from app.middleware.auth import get_current_user_id

            # Must not raise even though Redis is down
            result = await get_current_user_id(f"Bearer {TOKEN}")

    assert result == uuid.UUID(USER_SUB)
    mock_client.get.assert_called_once()


# ---------------------------------------------------------------------------
# 4. Expired / evicted entry — treated as cache miss, re-verified
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_current_user_id_expired_entry_revalidates():
    """An expired cache entry (None after TTL) is treated as a cache miss."""
    mock_redis = MagicMock()
    mock_redis.get.return_value = None  # expired key returns None

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = AUTH_VERIFY_RESPONSE

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch("app.middleware.auth._redis_client", mock_redis):
        with patch("app.middleware.auth.httpx.AsyncClient", return_value=mock_client):
            from app.middleware.auth import get_current_user_id

            result = await get_current_user_id(f"Bearer {TOKEN}")

    mock_client.get.assert_called_once()
    mock_redis.setex.assert_called_once()
    assert result == uuid.UUID(USER_SUB)
