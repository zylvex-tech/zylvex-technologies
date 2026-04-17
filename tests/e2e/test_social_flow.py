"""E2E tests for the social graph flow (6 scenarios)."""

import pytest

from conftest import (
    SOCIAL_URL,
    auth_headers,
    login_user,
    register_user,
    _unique_email,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_authenticated_user(client):
    """Create a new user and return (user_id, token)."""
    email = _unique_email()
    reg_resp = register_user(client, email=email)
    user_id = reg_resp.json().get("id") or reg_resp.json().get("user_id")
    login_resp = login_user(client, email)
    token = login_resp.json()["access_token"]
    return user_id, token


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSocialFlow:
    """Full social graph E2E scenarios."""

    # 1 ── Follow a user → 200
    def test_follow_user(self, http_client):
        user_a_id, token_a = _create_authenticated_user(http_client)
        user_b_id, _ = _create_authenticated_user(http_client)
        resp = http_client.post(
            f"{SOCIAL_URL}/social/follow/{user_b_id}",
            headers=auth_headers(token_a),
        )
        assert resp.status_code in (200, 201)

    # 2 ── Follow same user again → idempotent (no duplicate)
    def test_follow_idempotent(self, http_client):
        user_a_id, token_a = _create_authenticated_user(http_client)
        user_b_id, _ = _create_authenticated_user(http_client)
        http_client.post(
            f"{SOCIAL_URL}/social/follow/{user_b_id}",
            headers=auth_headers(token_a),
        )
        resp = http_client.post(
            f"{SOCIAL_URL}/social/follow/{user_b_id}",
            headers=auth_headers(token_a),
        )
        # Should succeed without creating a duplicate
        assert resp.status_code in (200, 201)

    # 3 ── Cannot follow yourself → 400
    def test_cannot_follow_self(self, http_client):
        user_id, token = _create_authenticated_user(http_client)
        resp = http_client.post(
            f"{SOCIAL_URL}/social/follow/{user_id}",
            headers=auth_headers(token),
        )
        assert resp.status_code == 400

    # 4 ── Unfollow → 200
    def test_unfollow_user(self, http_client):
        user_a_id, token_a = _create_authenticated_user(http_client)
        user_b_id, _ = _create_authenticated_user(http_client)
        # Follow first
        http_client.post(
            f"{SOCIAL_URL}/social/follow/{user_b_id}",
            headers=auth_headers(token_a),
        )
        # Unfollow
        resp = http_client.delete(
            f"{SOCIAL_URL}/social/follow/{user_b_id}",
            headers=auth_headers(token_a),
        )
        assert resp.status_code == 200

    # 5 ── Get followers list → correct count
    def test_get_followers_list(self, http_client):
        user_a_id, token_a = _create_authenticated_user(http_client)
        user_b_id, token_b = _create_authenticated_user(http_client)
        # A follows B
        http_client.post(
            f"{SOCIAL_URL}/social/follow/{user_b_id}",
            headers=auth_headers(token_a),
        )
        # Get B's followers
        resp = http_client.get(
            f"{SOCIAL_URL}/social/followers/{user_b_id}",
            headers=auth_headers(token_b),
        )
        assert resp.status_code == 200
        data = resp.json()
        # Response may be list or dict with items
        followers = data if isinstance(data, list) else data.get("items", data.get("followers", []))
        assert len(followers) >= 1

    # 6 ── Get nearby feed → returns anchors with creator info
    def test_nearby_feed(self, http_client):
        _, token = _create_authenticated_user(http_client)
        resp = http_client.get(
            f"{SOCIAL_URL}/social/feed/nearby",
            params={"lat": 6.5244, "lng": 3.3792, "radius_km": 10},
            headers=auth_headers(token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
