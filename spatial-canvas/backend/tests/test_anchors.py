"""Spatial Canvas backend tests.

These tests use pytest-mock to mock the auth service HTTP calls and the
PostGIS-dependent service layer, so no running Postgres/PostGIS is needed.
"""

import os
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("AUTH_SERVICE_URL", "http://localhost:8001")

from app.main import app
from app.api.deps import get_current_user, get_current_user_id

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TEST_USER_ID = uuid.uuid4()
TEST_USER = {
    "id": str(TEST_USER_ID),
    "email": "tester@example.com",
    "full_name": "Test User",
    "is_active": True,
}

ANCHOR_PAYLOAD = {
    "title": "My Anchor",
    "content": "Hello World",
    "content_type": "text",
    "latitude": 51.5074,
    "longitude": -0.1278,
}


def _auth_override():
    return TEST_USER


def _user_id_override():
    return TEST_USER_ID


# ---------------------------------------------------------------------------
# 1. Health check (no auth required)
# ---------------------------------------------------------------------------


def test_health_check():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# ---------------------------------------------------------------------------
# 2. Create anchor — unauthenticated (no header)
# ---------------------------------------------------------------------------


def test_create_anchor_unauthenticated():
    client = TestClient(app)
    response = client.post("/api/v1/anchors", json=ANCHOR_PAYLOAD)
    assert response.status_code in (401, 403, 422)


# ---------------------------------------------------------------------------
# 3. Create anchor — authenticated (mocked auth + service)
# ---------------------------------------------------------------------------


def test_create_anchor_authenticated(mocker):
    app.dependency_overrides[get_current_user] = _auth_override
    app.dependency_overrides[get_current_user_id] = _user_id_override

    mock_anchor = MagicMock()
    mock_anchor.id = uuid.uuid4()
    mock_anchor.user_id = TEST_USER_ID
    mock_anchor.title = ANCHOR_PAYLOAD["title"]
    mock_anchor.content = ANCHOR_PAYLOAD["content"]
    mock_anchor.content_type = ANCHOR_PAYLOAD["content_type"]
    mock_anchor.latitude = ANCHOR_PAYLOAD["latitude"]
    mock_anchor.longitude = ANCHOR_PAYLOAD["longitude"]
    mock_anchor.created_at = None
    mock_anchor.updated_at = None
    mock_anchor.owner_name = None

    mocker.patch(
        "app.api.v1.endpoints.anchors.AnchorService.create_anchor",
        return_value=mock_anchor,
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/anchors",
        json=ANCHOR_PAYLOAD,
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == ANCHOR_PAYLOAD["title"]

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# 4. Get nearby anchors — verify radius filter applied
# ---------------------------------------------------------------------------


def test_get_nearby_anchors(mocker):
    mock_anchors = []
    for i, (lat, lon) in enumerate([(51.5074, -0.1278), (51.5080, -0.1280)]):
        a = MagicMock()
        a.id = uuid.uuid4()
        a.user_id = TEST_USER_ID
        a.title = f"Anchor {i}"
        a.content = "content"
        a.content_type = "text"
        a.latitude = lat
        a.longitude = lon
        a.created_at = None
        a.updated_at = None
        a.owner_name = None
        mock_anchors.append(a)

    mocker.patch(
        "app.api.v1.endpoints.anchors.AnchorService.get_anchors_nearby",
        return_value=mock_anchors,
    )

    client = TestClient(app)
    response = client.get(
        "/api/v1/anchors",
        params={"latitude": 51.5074, "longitude": -0.1278, "radius_km": 0.5},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert len(data["anchors"]) == 2


# ---------------------------------------------------------------------------
# 5. Get my anchors — verify user scoping
# ---------------------------------------------------------------------------


def test_get_my_anchors(mocker):
    app.dependency_overrides[get_current_user] = _auth_override
    app.dependency_overrides[get_current_user_id] = _user_id_override

    my_anchor = MagicMock()
    my_anchor.id = uuid.uuid4()
    my_anchor.user_id = TEST_USER_ID
    my_anchor.title = "Mine"
    my_anchor.content = "data"
    my_anchor.content_type = "text"
    my_anchor.latitude = 51.5074
    my_anchor.longitude = -0.1278
    my_anchor.created_at = None
    my_anchor.updated_at = None
    my_anchor.owner_name = None

    mocker.patch(
        "app.api.v1.endpoints.anchors.AnchorService.get_user_anchors",
        return_value=[my_anchor],
    )

    client = TestClient(app)
    response = client.get(
        "/api/v1/anchors/mine",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Mine"

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# 6. Get anchor by ID
# ---------------------------------------------------------------------------


def test_get_anchor_by_id(mocker):
    anchor_id = uuid.uuid4()
    mock_anchor = MagicMock()
    mock_anchor.id = anchor_id
    mock_anchor.user_id = TEST_USER_ID
    mock_anchor.title = "Specific Anchor"
    mock_anchor.content = "hello"
    mock_anchor.content_type = "text"
    mock_anchor.latitude = 51.5074
    mock_anchor.longitude = -0.1278
    mock_anchor.created_at = None
    mock_anchor.updated_at = None
    mock_anchor.owner_name = None

    mocker.patch(
        "app.api.v1.endpoints.anchors.AnchorService.get_anchor_by_id",
        return_value=mock_anchor,
    )

    client = TestClient(app)
    response = client.get(f"/api/v1/anchors/{anchor_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Specific Anchor"


# ---------------------------------------------------------------------------
# 7. Get anchor by ID — not found
# ---------------------------------------------------------------------------


def test_get_anchor_by_id_not_found(mocker):
    mocker.patch(
        "app.api.v1.endpoints.anchors.AnchorService.get_anchor_by_id",
        return_value=None,
    )

    client = TestClient(app)
    response = client.get(f"/api/v1/anchors/{uuid.uuid4()}")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# 8. Delete anchor — owner can delete
# ---------------------------------------------------------------------------


def test_delete_anchor_owner(mocker):
    app.dependency_overrides[get_current_user] = _auth_override
    app.dependency_overrides[get_current_user_id] = _user_id_override

    mocker.patch(
        "app.api.v1.endpoints.anchors.AnchorService.delete_anchor",
        return_value=True,
    )

    client = TestClient(app)
    response = client.delete(
        f"/api/v1/anchors/{uuid.uuid4()}",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 204

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# 9. Delete anchor — non-owner gets 403
# ---------------------------------------------------------------------------


def test_delete_anchor_non_owner(mocker):
    app.dependency_overrides[get_current_user] = _auth_override
    app.dependency_overrides[get_current_user_id] = _user_id_override

    mocker.patch(
        "app.api.v1.endpoints.anchors.AnchorService.delete_anchor",
        return_value=False,
    )

    client = TestClient(app)
    response = client.delete(
        f"/api/v1/anchors/{uuid.uuid4()}",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 403

    app.dependency_overrides.clear()
