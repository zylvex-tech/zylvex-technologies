"""Social graph service test suite — 16 test cases.

Uses SQLite in-memory (same pattern as shared/auth tests).
Auth dependency is overridden to skip HTTP calls to the auth service.
The _fetch_nearby_anchors helper is patched for feed/nearby tests.
"""

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
os.environ.setdefault("SPATIAL_CANVAS_URL", "http://localhost:8000")

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


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

USER_A_ID = uuid.uuid4()
USER_B_ID = uuid.uuid4()
USER_C_ID = uuid.uuid4()

USER_A = {"id": str(USER_A_ID), "sub": str(USER_A_ID), "email": "alice@example.com",
          "full_name": "Alice", "is_active": True}
USER_B = {"id": str(USER_B_ID), "sub": str(USER_B_ID), "email": "bob@example.com",
          "full_name": "Bob", "is_active": True}


def auth_as(user: dict):
    """Return a dependency override that authenticates as *user*."""
    async def _override():
        return user
    return _override


app.dependency_overrides[get_db] = override_get_db


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
# 2. Follow a user — success
# ---------------------------------------------------------------------------


def test_follow_user():
    client = _client_as(USER_A)
    response = client.post(
        f"/social/follow/{USER_B_ID}",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["follower_id"] == str(USER_A_ID)
    assert data["following_id"] == str(USER_B_ID)


# ---------------------------------------------------------------------------
# 3. Follow idempotency — following the same user a second time returns 200
# ---------------------------------------------------------------------------


def test_follow_user_idempotency():
    client = _client_as(USER_A)
    headers = {"Authorization": "Bearer fake-token"}

    # First follow → 201
    r1 = client.post(f"/social/follow/{USER_B_ID}", headers=headers)
    assert r1.status_code == 201

    # Second follow → 200 (already following)
    r2 = client.post(f"/social/follow/{USER_B_ID}", headers=headers)
    assert r2.status_code == 200


# ---------------------------------------------------------------------------
# 4. Self-follow prevention
# ---------------------------------------------------------------------------


def test_self_follow_prevention():
    client = _client_as(USER_A)
    response = client.post(
        f"/social/follow/{USER_A_ID}",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 400
    assert "yourself" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# 5. Unfollow — success
# ---------------------------------------------------------------------------


def test_unfollow_user():
    client = _client_as(USER_A)
    headers = {"Authorization": "Bearer fake-token"}

    client.post(f"/social/follow/{USER_B_ID}", headers=headers)
    response = client.delete(f"/social/follow/{USER_B_ID}", headers=headers)
    assert response.status_code == 204

    # Confirm no longer following
    r = client.get(f"/social/following/{USER_A_ID}")
    assert r.status_code == 200
    assert r.json()["total"] == 0


# ---------------------------------------------------------------------------
# 6. Unfollow idempotency — unfollowing a non-followed user returns 204
# ---------------------------------------------------------------------------


def test_unfollow_nonexistent_is_idempotent():
    client = _client_as(USER_A)
    response = client.delete(
        f"/social/follow/{USER_C_ID}",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 204


# ---------------------------------------------------------------------------
# 7. Get followers — paginated
# ---------------------------------------------------------------------------


def test_get_followers():
    # USER_A follows USER_B
    client_a = _client_as(USER_A)
    client_a.post(f"/social/follow/{USER_B_ID}", headers={"Authorization": "Bearer x"})

    client = TestClient(app)
    response = client.get(f"/social/followers/{USER_B_ID}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["user_id"] == str(USER_A_ID)


# ---------------------------------------------------------------------------
# 8. Get following — paginated
# ---------------------------------------------------------------------------


def test_get_following():
    client_a = _client_as(USER_A)
    client_a.post(f"/social/follow/{USER_B_ID}", headers={"Authorization": "Bearer x"})

    client = TestClient(app)
    response = client.get(f"/social/following/{USER_A_ID}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["user_id"] == str(USER_B_ID)


# ---------------------------------------------------------------------------
# 9. React to an anchor — success
# ---------------------------------------------------------------------------

ANCHOR_ID = uuid.uuid4()


def test_react_to_anchor():
    client = _client_as(USER_A)
    response = client.post(
        "/social/react",
        json={
            "content_type": "anchor",
            "content_id": str(ANCHOR_ID),
            "emoji": "👍",
        },
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["emoji"] == "👍"
    assert data["content_type"] == "anchor"
    assert data["user_id"] == str(USER_A_ID)


# ---------------------------------------------------------------------------
# 10. Reaction uniqueness — duplicate reaction returns 409
# ---------------------------------------------------------------------------


def test_react_duplicate_prevention():
    client = _client_as(USER_A)
    headers = {"Authorization": "Bearer fake-token"}
    payload = {"content_type": "anchor", "content_id": str(ANCHOR_ID), "emoji": "❤️"}

    r1 = client.post("/social/react", json=payload, headers=headers)
    assert r1.status_code == 201

    r2 = client.post("/social/react", json=payload, headers=headers)
    assert r2.status_code == 409


# ---------------------------------------------------------------------------
# 11. Invalid emoji is rejected
# ---------------------------------------------------------------------------


def test_react_invalid_emoji():
    client = _client_as(USER_A)
    response = client.post(
        "/social/react",
        json={"content_type": "anchor", "content_id": str(ANCHOR_ID), "emoji": "😈"},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# 12. Delete a reaction — owner can delete
# ---------------------------------------------------------------------------


def test_delete_reaction():
    client = _client_as(USER_A)
    headers = {"Authorization": "Bearer fake-token"}

    r = client.post(
        "/social/react",
        json={"content_type": "mindmap", "content_id": str(uuid.uuid4()), "emoji": "🔥"},
        headers=headers,
    )
    assert r.status_code == 201
    reaction_id = r.json()["id"]

    del_r = client.delete(f"/social/react/{reaction_id}", headers=headers)
    assert del_r.status_code == 204


# ---------------------------------------------------------------------------
# 13. Delete a reaction — non-owner gets 403
# ---------------------------------------------------------------------------


def test_delete_reaction_non_owner():
    content_id = uuid.uuid4()

    # USER_A creates reaction
    client_a = _client_as(USER_A)
    r = client_a.post(
        "/social/react",
        json={"content_type": "anchor", "content_id": str(content_id), "emoji": "💡"},
        headers={"Authorization": "Bearer a"},
    )
    assert r.status_code == 201
    reaction_id = r.json()["id"]

    # USER_B tries to delete it
    client_b = _client_as(USER_B)
    del_r = client_b.delete(
        f"/social/react/{reaction_id}",
        headers={"Authorization": "Bearer b"},
    )
    assert del_r.status_code == 403


# ---------------------------------------------------------------------------
# 14. Get reactions for content
# ---------------------------------------------------------------------------


def test_get_reactions_for_content():
    content_id = uuid.uuid4()

    # Two users react to the same anchor
    client_a = _client_as(USER_A)
    client_a.post(
        "/social/react",
        json={"content_type": "anchor", "content_id": str(content_id), "emoji": "👍"},
        headers={"Authorization": "Bearer a"},
    )
    client_b = _client_as(USER_B)
    client_b.post(
        "/social/react",
        json={"content_type": "anchor", "content_id": str(content_id), "emoji": "❤️"},
        headers={"Authorization": "Bearer b"},
    )

    client = TestClient(app)
    response = client.get(f"/social/reactions/anchor/{content_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    emojis = {r["emoji"] for r in data["reactions"]}
    assert emojis == {"👍", "❤️"}


# ---------------------------------------------------------------------------
# 15. Feed trending — returns ordered reaction counts
# ---------------------------------------------------------------------------


def test_feed_trending():
    content_a = uuid.uuid4()
    content_b = uuid.uuid4()

    # content_b gets 2 reactions, content_a gets 1
    client_a = _client_as(USER_A)
    client_b = _client_as(USER_B)

    client_a.post(
        "/social/react",
        json={"content_type": "anchor", "content_id": str(content_a), "emoji": "👍"},
        headers={"Authorization": "Bearer a"},
    )
    client_a.post(
        "/social/react",
        json={"content_type": "mindmap", "content_id": str(content_b), "emoji": "🔥"},
        headers={"Authorization": "Bearer a"},
    )
    client_b.post(
        "/social/react",
        json={"content_type": "mindmap", "content_id": str(content_b), "emoji": "❤️"},
        headers={"Authorization": "Bearer b"},
    )

    client = TestClient(app)
    response = client.get("/social/feed/trending")
    assert response.status_code == 200
    data = response.json()
    assert data["window_days"] == 7
    assert len(data["items"]) >= 2
    # content_b should appear first (2 reactions vs 1)
    assert data["items"][0]["reaction_count"] >= data["items"][1]["reaction_count"]


# ---------------------------------------------------------------------------
# 16. Feed nearby — annotates followed-user anchors (mocked spatial canvas)
# ---------------------------------------------------------------------------


def test_feed_nearby(mocker):
    # USER_A follows USER_B
    client_a = _client_as(USER_A)
    client_a.post(
        f"/social/follow/{USER_B_ID}",
        headers={"Authorization": "Bearer fake-token"},
    )

    # Mock the spatial canvas call
    anchor_by_b = {
        "id": str(uuid.uuid4()),
        "user_id": str(USER_B_ID),
        "title": "Bob's Anchor",
        "content": "hello",
        "content_type": "text",
        "latitude": 51.5,
        "longitude": -0.1,
        "created_at": "2024-01-02T00:00:00",
    }
    anchor_public = {
        "id": str(uuid.uuid4()),
        "user_id": str(USER_C_ID),
        "title": "Public Anchor",
        "content": "world",
        "content_type": "text",
        "latitude": 51.51,
        "longitude": -0.11,
        "created_at": "2024-01-01T00:00:00",
    }

    mocker.patch(
        "app.api.social._fetch_nearby_anchors",
        return_value=[anchor_public, anchor_by_b],
    )

    client = _client_as(USER_A)
    response = client.get(
        "/social/feed/nearby",
        params={"lat": 51.5, "lng": -0.1, "radius_km": 2},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2
    # Bob's anchor (followed) should be first
    assert items[0]["is_followed"] is True
    assert items[0]["title"] == "Bob's Anchor"
    assert items[1]["is_followed"] is False
