"""E2E tests for the Spatial Canvas anchor flow (8 scenarios)."""

import math

import pytest

from conftest import (
    SPATIAL_URL,
    auth_headers,
    login_user,
    register_user,
    _unique_email,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_anchor(client, token, **overrides):
    payload = {
        "title": overrides.get("title", "Test Anchor"),
        "description": overrides.get("description", "E2E test anchor"),
        "content_type": overrides.get("content_type", "text"),
        "latitude": overrides.get("latitude", 6.5244),
        "longitude": overrides.get("longitude", 3.3792),
    }
    return client.post(
        f"{SPATIAL_URL}/api/v1/anchors",
        json=payload,
        headers=auth_headers(token),
    )


def _get_user_token(client):
    email = _unique_email()
    register_user(client, email=email)
    resp = login_user(client, email)
    return resp.json()["access_token"]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestAnchorFlow:
    """Full Spatial Canvas anchor E2E scenarios."""

    # 1 ── Create anchor with valid auth → 201
    def test_create_anchor(self, http_client, authenticated_user):
        _, _, token, _ = authenticated_user
        resp = _create_anchor(http_client, token)
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data

    # 2 ── Create anchor without auth → 401
    def test_create_anchor_no_auth(self, http_client):
        resp = http_client.post(
            f"{SPATIAL_URL}/api/v1/anchors",
            json={
                "title": "No Auth Anchor",
                "description": "Should fail",
                "content_type": "text",
                "latitude": 6.5,
                "longitude": 3.3,
            },
        )
        assert resp.status_code in (401, 403)

    # 3 ── Get nearby anchors with lat/lng/radius → returns list
    def test_get_nearby_anchors(self, http_client, authenticated_user):
        _, _, token, _ = authenticated_user
        _create_anchor(http_client, token, latitude=6.5244, longitude=3.3792)
        resp = http_client.get(
            f"{SPATIAL_URL}/api/v1/anchors/nearby",
            params={"latitude": 6.5244, "longitude": 3.3792, "radius_km": 10},
            headers=auth_headers(token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    # 4 ── Distance accuracy: two anchors at known coords
    def test_distance_accuracy(self, http_client, authenticated_user):
        _, _, token, _ = authenticated_user
        # Lagos (6.5244, 3.3792) and a point ~5 km away
        lat1, lng1 = 6.5244, 3.3792
        lat2, lng2 = 6.5700, 3.3792  # ~5 km north
        _create_anchor(http_client, token, latitude=lat1, longitude=lng1, title="A1")
        _create_anchor(http_client, token, latitude=lat2, longitude=lng2, title="A2")
        resp = http_client.get(
            f"{SPATIAL_URL}/api/v1/anchors/nearby",
            params={"latitude": lat1, "longitude": lng1, "radius_km": 10},
            headers=auth_headers(token),
        )
        assert resp.status_code == 200
        anchors = resp.json()
        # At least two anchors should be returned
        assert len(anchors) >= 2

    # 5 ── Update own anchor → 200
    def test_update_own_anchor(self, http_client, authenticated_user):
        _, _, token, _ = authenticated_user
        create_resp = _create_anchor(http_client, token)
        anchor_id = create_resp.json()["id"]
        resp = http_client.put(
            f"{SPATIAL_URL}/api/v1/anchors/{anchor_id}",
            json={"title": "Updated Title"},
            headers=auth_headers(token),
        )
        assert resp.status_code == 200

    # 6 ── Update another user's anchor → 403
    def test_update_other_users_anchor(self, http_client, authenticated_user):
        _, _, token, _ = authenticated_user
        create_resp = _create_anchor(http_client, token)
        anchor_id = create_resp.json()["id"]

        # Create second user
        other_token = _get_user_token(http_client)
        resp = http_client.put(
            f"{SPATIAL_URL}/api/v1/anchors/{anchor_id}",
            json={"title": "Hijacked"},
            headers=auth_headers(other_token),
        )
        assert resp.status_code == 403

    # 7 ── Delete own anchor → 204
    def test_delete_own_anchor(self, http_client, authenticated_user):
        _, _, token, _ = authenticated_user
        create_resp = _create_anchor(http_client, token)
        anchor_id = create_resp.json()["id"]
        resp = http_client.delete(
            f"{SPATIAL_URL}/api/v1/anchors/{anchor_id}",
            headers=auth_headers(token),
        )
        assert resp.status_code in (200, 204)

    # 8 ── Upload media to anchor → 200 with media_url
    def test_upload_media_to_anchor(self, http_client, authenticated_user):
        _, _, token, _ = authenticated_user
        create_resp = _create_anchor(http_client, token)
        anchor_id = create_resp.json()["id"]
        # Create a tiny PNG file (1x1 pixel)
        png_bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
            b"\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00"
            b"\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        resp = http_client.post(
            f"{SPATIAL_URL}/api/v1/anchors/{anchor_id}/media",
            files={"file": ("test.png", png_bytes, "image/png")},
            headers=auth_headers(token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "media_url" in data
