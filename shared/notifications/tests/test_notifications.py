"""Notifications service test suite — 10 test cases.

Uses SQLite in-memory (same pattern as shared/auth and shared/social tests).
Auth dependency is overridden to skip HTTP calls to the auth service.
SendGrid and push notification side-effects are mocked.
"""

import asyncio
import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set required env vars before importing the app
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("AUTH_SERVICE_URL", "http://localhost:8001")
os.environ.setdefault("REALTIME_SERVICE_URL", "http://localhost:8004")
os.environ.setdefault("SENDGRID_API_KEY", "")

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.api.deps import get_current_user

# ---------------------------------------------------------------------------
# Test database setup (SQLite in-memory)
# ---------------------------------------------------------------------------

SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

USER_A_ID = uuid.uuid4()
USER_B_ID = uuid.uuid4()

USER_A = {
    "id": str(USER_A_ID),
    "sub": str(USER_A_ID),
    "email": "alice@example.com",
    "full_name": "Alice",
    "is_active": True,
}
USER_B = {
    "id": str(USER_B_ID),
    "sub": str(USER_B_ID),
    "email": "bob@example.com",
    "full_name": "Bob",
    "is_active": True,
}


def auth_as(user: dict):
    async def _override():
        return user

    return _override


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _client_as(user: dict) -> TestClient:
    app.dependency_overrides[get_current_user] = auth_as(user)
    return TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# 1. Health check
# ---------------------------------------------------------------------------


def test_health_check():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# ---------------------------------------------------------------------------
# 2. Send a notification (internal endpoint)
# ---------------------------------------------------------------------------


def test_send_notification(mocker):
    mocker.patch("app.api.notifications.asyncio.create_task")
    client = TestClient(app, raise_server_exceptions=False)
    response = client.post(
        "/notifications/send",
        json={
            "user_id": str(USER_A_ID),
            "type": "follow",
            "title": "Alice followed you",
            "body": "Alice started following you.",
            "metadata": {"user_email": "alice@example.com", "user_name": "Alice"},
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "follow"
    assert data["title"] == "Alice followed you"
    assert data["read"] is False
    assert data["user_id"] == str(USER_A_ID)


# ---------------------------------------------------------------------------
# 3. Send notification with invalid type returns 400
# ---------------------------------------------------------------------------


def test_send_notification_invalid_type():
    client = TestClient(app, raise_server_exceptions=False)
    response = client.post(
        "/notifications/send",
        json={
            "user_id": str(USER_A_ID),
            "type": "invalid_type",
            "title": "Test",
            "body": "Test body",
        },
    )
    assert response.status_code == 400
    assert "Invalid notification type" in response.json()["detail"]


# ---------------------------------------------------------------------------
# 4. GET /notifications/me — empty list for new user
# ---------------------------------------------------------------------------


def test_list_notifications_empty():
    client = _client_as(USER_A)
    response = client.get(
        "/notifications/me",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []
    assert data["page"] == 1


# ---------------------------------------------------------------------------
# 5. GET /notifications/me — returns created notifications
# ---------------------------------------------------------------------------


def test_list_notifications_with_data(mocker):
    mocker.patch("app.api.notifications.asyncio.create_task")
    client_send = TestClient(app, raise_server_exceptions=False)

    # Create 2 notifications for USER_A
    for i in range(2):
        client_send.post(
            "/notifications/send",
            json={
                "user_id": str(USER_A_ID),
                "type": "reaction",
                "title": f"Reaction {i}",
                "body": f"Someone reacted {i}",
            },
        )

    client = _client_as(USER_A)
    response = client.get(
        "/notifications/me",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


# ---------------------------------------------------------------------------
# 6. GET /notifications/me — pagination works
# ---------------------------------------------------------------------------


def test_list_notifications_pagination(mocker):
    mocker.patch("app.api.notifications.asyncio.create_task")
    client_send = TestClient(app, raise_server_exceptions=False)

    # Create 5 notifications
    for i in range(5):
        client_send.post(
            "/notifications/send",
            json={
                "user_id": str(USER_A_ID),
                "type": "nearby_anchor",
                "title": f"Anchor {i}",
                "body": f"New anchor nearby {i}",
            },
        )

    client = _client_as(USER_A)
    response = client.get(
        "/notifications/me",
        params={"page": 1, "page_size": 3},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 3
    assert data["page"] == 1

    response2 = client.get(
        "/notifications/me",
        params={"page": 2, "page_size": 3},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2["items"]) == 2


# ---------------------------------------------------------------------------
# 7. Mark a single notification as read
# ---------------------------------------------------------------------------


def test_mark_notification_read(mocker):
    mocker.patch("app.api.notifications.asyncio.create_task")
    client_send = TestClient(app, raise_server_exceptions=False)

    r = client_send.post(
        "/notifications/send",
        json={
            "user_id": str(USER_A_ID),
            "type": "follow",
            "title": "New follower",
            "body": "Bob followed you.",
        },
    )
    notif_id = r.json()["id"]

    client = _client_as(USER_A)
    mark_r = client.post(
        f"/notifications/mark-read/{notif_id}",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert mark_r.status_code == 200
    assert mark_r.json()["read"] is True


# ---------------------------------------------------------------------------
# 8. Mark-read returns 404 for another user's notification
# ---------------------------------------------------------------------------


def test_mark_read_wrong_user(mocker):
    mocker.patch("app.api.notifications.asyncio.create_task")
    client_send = TestClient(app, raise_server_exceptions=False)

    # Create notification for USER_A
    r = client_send.post(
        "/notifications/send",
        json={
            "user_id": str(USER_A_ID),
            "type": "reaction",
            "title": "Test",
            "body": "Test body",
        },
    )
    notif_id = r.json()["id"]

    # USER_B tries to mark it read → should get 404
    client_b = _client_as(USER_B)
    mark_r = client_b.post(
        f"/notifications/mark-read/{notif_id}",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert mark_r.status_code == 404


# ---------------------------------------------------------------------------
# 9. Mark-all-read
# ---------------------------------------------------------------------------


def test_mark_all_read(mocker):
    mocker.patch("app.api.notifications.asyncio.create_task")
    client_send = TestClient(app, raise_server_exceptions=False)

    # Create 3 unread notifications for USER_A
    for i in range(3):
        client_send.post(
            "/notifications/send",
            json={
                "user_id": str(USER_A_ID),
                "type": "collaboration_invite",
                "title": f"Invite {i}",
                "body": f"Collaboration invite {i}",
            },
        )

    client = _client_as(USER_A)
    r = client.post(
        "/notifications/mark-all-read",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert r.status_code == 200
    assert r.json()["marked_read"] == 3

    # Verify all are read
    list_r = client.get(
        "/notifications/me",
        params={"unread_only": True},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert list_r.json()["total"] == 0


# ---------------------------------------------------------------------------
# 10. Notifications for USER_B are not visible to USER_A
# ---------------------------------------------------------------------------


def test_user_isolation(mocker):
    mocker.patch("app.api.notifications.asyncio.create_task")
    client_send = TestClient(app, raise_server_exceptions=False)

    # Create 1 notification for USER_B
    client_send.post(
        "/notifications/send",
        json={
            "user_id": str(USER_B_ID),
            "type": "follow",
            "title": "For Bob only",
            "body": "Bob's notification",
        },
    )

    # USER_A should see 0
    client_a = _client_as(USER_A)
    r = client_a.get(
        "/notifications/me",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert r.status_code == 200
    assert r.json()["total"] == 0
