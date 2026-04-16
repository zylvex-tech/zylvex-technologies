"""Tests for the Redis token verification cache (shared/auth/app/core/token_cache.py).

Covers:
1. Cache hit  — cached data is returned without calling Redis again
2. Cache miss — None is returned when key is absent
3. Cache set  — data is stored with correct TTL and key
4. Redis unreachable / fallback — errors are swallowed, None returned
5. Key derivation — sha256 of token is used as key
6. Invalidation  — delete removes the key
"""

import hashlib
import json
from unittest.mock import MagicMock, patch

import pytest

from app.core.token_cache import (
    TOKEN_CACHE_TTL,
    _KEY_PREFIX,
    _token_key,
    get_cached_user,
    invalidate_cached_token,
    set_cached_user,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"
USER_DATA = {"id": "00000000-0000-0000-0000-000000000001", "email": "a@b.com", "roles": ["user"]}


def _fake_redis(get_return=None, raise_on_get=False, raise_on_set=False):
    """Return a MagicMock that mimics a Redis client."""
    client = MagicMock()
    if raise_on_get:
        client.get.side_effect = ConnectionError("Redis down")
    else:
        client.get.return_value = get_return
    if raise_on_set:
        client.setex.side_effect = ConnectionError("Redis down")
    client.delete.return_value = 1
    return client


# ---------------------------------------------------------------------------
# 1. Key derivation
# ---------------------------------------------------------------------------


def test_token_key_is_sha256_prefixed():
    expected = _KEY_PREFIX + hashlib.sha256(TOKEN.encode()).hexdigest()
    assert _token_key(TOKEN) == expected


# ---------------------------------------------------------------------------
# 2. Cache hit — get_cached_user returns parsed dict
# ---------------------------------------------------------------------------


def test_cache_hit_returns_user_data():
    stored = json.dumps({"user_id": USER_DATA["id"], "roles": ["user"]})
    client = _fake_redis(get_return=stored)

    result = get_cached_user(client, TOKEN)

    client.get.assert_called_once_with(_token_key(TOKEN))
    assert result == {"user_id": USER_DATA["id"], "roles": ["user"]}


# ---------------------------------------------------------------------------
# 3. Cache miss — get_cached_user returns None
# ---------------------------------------------------------------------------


def test_cache_miss_returns_none():
    client = _fake_redis(get_return=None)

    result = get_cached_user(client, TOKEN)

    assert result is None


# ---------------------------------------------------------------------------
# 4. get_cached_user with None client (no Redis configured)
# ---------------------------------------------------------------------------


def test_cache_get_with_no_client_returns_none():
    result = get_cached_user(None, TOKEN)
    assert result is None


# ---------------------------------------------------------------------------
# 5. Redis unreachable on GET — fallback returns None, no exception raised
# ---------------------------------------------------------------------------


def test_cache_get_redis_unreachable_returns_none():
    client = _fake_redis(raise_on_get=True)

    # Must NOT raise
    result = get_cached_user(client, TOKEN)

    assert result is None


# ---------------------------------------------------------------------------
# 6. set_cached_user stores correct payload with TTL
# ---------------------------------------------------------------------------


def test_set_cached_user_stores_with_ttl():
    client = _fake_redis()

    set_cached_user(client, TOKEN, USER_DATA)

    key = _token_key(TOKEN)
    client.setex.assert_called_once()
    call_args = client.setex.call_args
    assert call_args[0][0] == key
    assert call_args[0][1] == TOKEN_CACHE_TTL
    payload = json.loads(call_args[0][2])
    assert payload["user_id"] == USER_DATA["id"]
    assert payload["roles"] == USER_DATA["roles"]


# ---------------------------------------------------------------------------
# 7. set_cached_user with None client — no-op, no exception
# ---------------------------------------------------------------------------


def test_set_cached_user_with_no_client_is_noop():
    # Should not raise
    set_cached_user(None, TOKEN, USER_DATA)


# ---------------------------------------------------------------------------
# 8. Redis unreachable on SET — non-fatal, no exception raised
# ---------------------------------------------------------------------------


def test_set_cached_user_redis_unreachable_is_nonfatal():
    client = _fake_redis(raise_on_set=True)

    # Must NOT raise
    set_cached_user(client, TOKEN, USER_DATA)


# ---------------------------------------------------------------------------
# 9. invalidate_cached_token deletes the key
# ---------------------------------------------------------------------------


def test_invalidate_cached_token_deletes_key():
    client = _fake_redis()

    invalidate_cached_token(client, TOKEN)

    client.delete.assert_called_once_with(_token_key(TOKEN))


# ---------------------------------------------------------------------------
# 10. invalidate_cached_token with None client — no-op
# ---------------------------------------------------------------------------


def test_invalidate_with_no_client_is_noop():
    # Should not raise
    invalidate_cached_token(None, TOKEN)
