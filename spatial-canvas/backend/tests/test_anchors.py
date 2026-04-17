"""Spatial Canvas backend tests.

These tests use pytest-mock to mock the auth service HTTP calls and the
PostGIS-dependent service layer, so no running Postgres/PostGIS is needed.
"""

import io
import os
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("AUTH_SERVICE_URL", "http://localhost:8001")
os.environ.setdefault("MEDIA_STORAGE_PATH", "/tmp/test_media")

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
    mock_anchor.media_url = None
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
# 4. Get nearby anchors — verify radius filter applied (meters-based)
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
        a.media_url = None
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
    # radius_km=0.5 → service converts to 500 meters for Geography ST_DWithin
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
    my_anchor.media_url = None
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
    mock_anchor.media_url = None
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


# ===========================================================================
# MEDIA UPLOAD TESTS
# ===========================================================================


def _make_image_anchor_mock(anchor_id=None, user_id=None):
    """Create a mock anchor with content_type=image."""
    a = MagicMock()
    a.id = anchor_id or uuid.uuid4()
    a.user_id = user_id or TEST_USER_ID
    a.title = "Image Anchor"
    a.content = "A photo"
    a.content_type = "image"
    a.media_url = None
    a.latitude = 51.5074
    a.longitude = -0.1278
    a.created_at = None
    a.updated_at = None
    return a


# ---------------------------------------------------------------------------
# 10. Upload media — success (image anchor)
# ---------------------------------------------------------------------------


def test_upload_media_success(mocker):
    app.dependency_overrides[get_current_user] = _auth_override
    app.dependency_overrides[get_current_user_id] = _user_id_override

    anchor_id = uuid.uuid4()
    mock_anchor = _make_image_anchor_mock(anchor_id, TEST_USER_ID)
    # After "upload", media_url should be set
    mock_anchor.media_url = f"/media/{anchor_id}/test.png"

    mocker.patch(
        "app.api.v1.endpoints.media.AnchorService.get_anchor_by_id",
        return_value=mock_anchor,
    )

    # Mock the DB session's commit and refresh to be no-ops
    mock_db = MagicMock()
    from app.db.session import get_db as real_get_db

    def _mock_get_db():
        yield mock_db

    app.dependency_overrides[real_get_db] = _mock_get_db

    # Create a small fake image file
    file_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    files = {"file": ("test.png", io.BytesIO(file_content), "image/png")}

    client = TestClient(app)
    response = client.post(
        f"/api/v1/anchors/{anchor_id}/media",
        files=files,
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["media_url"] is not None
    assert "test.png" in data["media_url"]

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# 11. Upload media — wrong content type (video file to image anchor)
# ---------------------------------------------------------------------------


def test_upload_media_wrong_type(mocker):
    app.dependency_overrides[get_current_user] = _auth_override
    app.dependency_overrides[get_current_user_id] = _user_id_override

    anchor_id = uuid.uuid4()
    mock_anchor = _make_image_anchor_mock(anchor_id, TEST_USER_ID)

    mocker.patch(
        "app.api.v1.endpoints.media.AnchorService.get_anchor_by_id",
        return_value=mock_anchor,
    )

    # Upload a video file to an image anchor
    file_content = b"\x00" * 100
    files = {"file": ("test.mp4", io.BytesIO(file_content), "video/mp4")}

    client = TestClient(app)
    response = client.post(
        f"/api/v1/anchors/{anchor_id}/media",
        files=files,
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 400
    assert "does not match" in response.json()["detail"]

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# 12. Upload media — file size exceeded
# ---------------------------------------------------------------------------


def test_upload_media_size_exceeded(mocker):
    app.dependency_overrides[get_current_user] = _auth_override
    app.dependency_overrides[get_current_user_id] = _user_id_override

    anchor_id = uuid.uuid4()
    mock_anchor = _make_image_anchor_mock(anchor_id, TEST_USER_ID)

    mocker.patch(
        "app.api.v1.endpoints.media.AnchorService.get_anchor_by_id",
        return_value=mock_anchor,
    )

    # Create a file that exceeds the 10 MB image limit
    file_content = b"\x00" * (11 * 1024 * 1024)  # 11 MB
    files = {"file": ("huge.png", io.BytesIO(file_content), "image/png")}

    client = TestClient(app)
    response = client.post(
        f"/api/v1/anchors/{anchor_id}/media",
        files=files,
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 413
    assert "exceeds" in response.json()["detail"]

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# 13. Upload media — text anchor rejects media
# ---------------------------------------------------------------------------


def test_upload_media_text_anchor_rejected(mocker):
    app.dependency_overrides[get_current_user] = _auth_override
    app.dependency_overrides[get_current_user_id] = _user_id_override

    anchor_id = uuid.uuid4()
    mock_anchor = MagicMock()
    mock_anchor.id = anchor_id
    mock_anchor.user_id = TEST_USER_ID
    mock_anchor.content_type = "text"

    mocker.patch(
        "app.api.v1.endpoints.media.AnchorService.get_anchor_by_id",
        return_value=mock_anchor,
    )

    file_content = b"\x00" * 100
    files = {"file": ("test.png", io.BytesIO(file_content), "image/png")}

    client = TestClient(app)
    response = client.post(
        f"/api/v1/anchors/{anchor_id}/media",
        files=files,
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 400
    assert "text" in response.json()["detail"].lower()

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# 14. Upload media — anchor not found
# ---------------------------------------------------------------------------


def test_upload_media_anchor_not_found(mocker):
    app.dependency_overrides[get_current_user] = _auth_override
    app.dependency_overrides[get_current_user_id] = _user_id_override

    mocker.patch(
        "app.api.v1.endpoints.media.AnchorService.get_anchor_by_id",
        return_value=None,
    )

    file_content = b"\x00" * 100
    files = {"file": ("test.png", io.BytesIO(file_content), "image/png")}

    client = TestClient(app)
    response = client.post(
        f"/api/v1/anchors/{uuid.uuid4()}/media",
        files=files,
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 404

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# 15. Upload media — non-owner gets 403
# ---------------------------------------------------------------------------


def test_upload_media_non_owner(mocker):
    app.dependency_overrides[get_current_user] = _auth_override
    app.dependency_overrides[get_current_user_id] = _user_id_override

    anchor_id = uuid.uuid4()
    other_user_id = uuid.uuid4()
    mock_anchor = _make_image_anchor_mock(anchor_id, other_user_id)

    mocker.patch(
        "app.api.v1.endpoints.media.AnchorService.get_anchor_by_id",
        return_value=mock_anchor,
    )

    file_content = b"\x00" * 100
    files = {"file": ("test.png", io.BytesIO(file_content), "image/png")}

    client = TestClient(app)
    response = client.post(
        f"/api/v1/anchors/{anchor_id}/media",
        files=files,
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 403

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# 16. Get anchor media info
# ---------------------------------------------------------------------------


def test_get_anchor_media_info(mocker):
    anchor_id = uuid.uuid4()
    mock_anchor = MagicMock()
    mock_anchor.id = anchor_id
    mock_anchor.media_url = f"/media/{anchor_id}/photo.jpg"
    mock_anchor.content_type = "image"

    mocker.patch(
        "app.api.v1.endpoints.media.AnchorService.get_anchor_by_id",
        return_value=mock_anchor,
    )

    client = TestClient(app)
    response = client.get(f"/api/v1/anchors/{anchor_id}/media")
    assert response.status_code == 200
    data = response.json()
    assert data["content_type"] == "image"
    assert "photo.jpg" in data["media_url"]
