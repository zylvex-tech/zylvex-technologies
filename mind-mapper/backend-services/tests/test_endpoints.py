"""Mind Mapper backend test suite (10 test cases).

Uses SQLite in-memory DB and mocks the auth service httpx call.
"""

import os
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set env vars before importing the app
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("AUTH_SERVICE_URL", "http://localhost:8001")

from app.main import app
from app.db.session import Base, get_db
from app.middleware.auth import get_current_user_id

# ---------------------------------------------------------------------------
# Test database (SQLite in-memory, UUID stored as String)
# ---------------------------------------------------------------------------

TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# SQLite doesn't natively support UUID — store as string
from sqlalchemy.dialects import sqlite
from sqlalchemy import TypeDecorator, String as SAString
import uuid as _uuid_mod


class GUID(TypeDecorator):
    """Platform-independent GUID type using String on SQLite."""

    impl = SAString
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return _uuid_mod.UUID(value)


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)

TEST_USER_ID = uuid.uuid4()


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def override_get_user_id():
    return TEST_USER_ID


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user_id] = override_get_user_id


@pytest.fixture(autouse=True)
def setup_tables():
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)


client = TestClient(app)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_mindmap(title="Test Map"):
    resp = client.post("/api/v1/mindmaps", json={"title": title})
    assert resp.status_code == 201, resp.text
    return resp.json()


NODE_PAYLOAD = {
    "text": "Root Node",
    "focus_level": 75,
    "color": "#4CAF50",
    "x": 0.0,
    "y": 0.0,
}


# ---------------------------------------------------------------------------
# 1. Health check
# ---------------------------------------------------------------------------


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# ---------------------------------------------------------------------------
# 2. Create mindmap
# ---------------------------------------------------------------------------


def test_create_mindmap():
    response = client.post("/api/v1/mindmaps", json={"title": "My Map"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Map"
    assert "id" in data


# ---------------------------------------------------------------------------
# 3. List mindmaps — verify user scoping
# ---------------------------------------------------------------------------


def test_list_mindmaps():
    _create_mindmap("Map A")
    _create_mindmap("Map B")
    response = client.get("/api/v1/mindmaps")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    titles = {m["title"] for m in data}
    assert "Map A" in titles
    assert "Map B" in titles


# ---------------------------------------------------------------------------
# 4. GET mindmap nodes — create mindmap + nodes, verify response
# ---------------------------------------------------------------------------


def test_get_mindmap_nodes():
    mm = _create_mindmap()
    mid = mm["id"]

    # Create two nodes
    client.post(f"/api/v1/mindmaps/{mid}/nodes", json=NODE_PAYLOAD)
    client.post(
        f"/api/v1/mindmaps/{mid}/nodes", json={**NODE_PAYLOAD, "text": "Child Node"}
    )

    response = client.get(f"/api/v1/mindmaps/{mid}/nodes")
    assert response.status_code == 200
    nodes = response.json()
    assert len(nodes) == 2
    texts = {n["text"] for n in nodes}
    assert "Root Node" in texts
    assert "Child Node" in texts


# ---------------------------------------------------------------------------
# 5. Create node
# ---------------------------------------------------------------------------


def test_create_node():
    mm = _create_mindmap()
    mid = mm["id"]
    response = client.post(f"/api/v1/mindmaps/{mid}/nodes", json=NODE_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == NODE_PAYLOAD["text"]
    assert data["focus_level"] == NODE_PAYLOAD["focus_level"]


# ---------------------------------------------------------------------------
# 6. Update node — verify partial update
# ---------------------------------------------------------------------------


def test_update_node():
    mm = _create_mindmap()
    mid = mm["id"]
    node_resp = client.post(f"/api/v1/mindmaps/{mid}/nodes", json=NODE_PAYLOAD)
    node_id = node_resp.json()["id"]

    update_payload = {"text": "Updated Text", "focus_level": 50}
    response = client.put(
        f"/api/v1/mindmaps/{mid}/nodes/{node_id}", json=update_payload
    )
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Updated Text"
    assert data["focus_level"] == 50
    # Unchanged fields remain
    assert data["color"] == NODE_PAYLOAD["color"]


# ---------------------------------------------------------------------------
# 7. Delete node
# ---------------------------------------------------------------------------


def test_delete_node():
    mm = _create_mindmap()
    mid = mm["id"]
    node_resp = client.post(f"/api/v1/mindmaps/{mid}/nodes", json=NODE_PAYLOAD)
    node_id = node_resp.json()["id"]

    del_resp = client.delete(f"/api/v1/mindmaps/{mid}/nodes/{node_id}")
    assert del_resp.status_code == 204

    nodes_resp = client.get(f"/api/v1/mindmaps/{mid}/nodes")
    assert nodes_resp.status_code == 200
    assert nodes_resp.json() == []


# ---------------------------------------------------------------------------
# 8. Save session
# ---------------------------------------------------------------------------


def test_save_session():
    mm = _create_mindmap()
    mid = mm["id"]
    session_payload = {
        "avg_focus": 72.5,
        "duration_seconds": 300,
        "node_count": 5,
        "focus_timeline": [70, 75, 72, 71, 74],
    }
    response = client.post(f"/api/v1/mindmaps/{mid}/sessions", json=session_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["avg_focus"] == 72.5
    assert data["duration_seconds"] == 300


# ---------------------------------------------------------------------------
# 9. Get sessions
# ---------------------------------------------------------------------------


def test_get_sessions():
    mm = _create_mindmap()
    mid = mm["id"]
    for avg in [60.0, 70.0]:
        client.post(
            f"/api/v1/mindmaps/{mid}/sessions",
            json={
                "avg_focus": avg,
                "duration_seconds": 120,
                "node_count": 3,
                "focus_timeline": [avg],
            },
        )
    response = client.get(f"/api/v1/mindmaps/{mid}/sessions")
    assert response.status_code == 200
    assert len(response.json()) == 2


# ---------------------------------------------------------------------------
# 10. Unauthenticated request — expect 401
# ---------------------------------------------------------------------------


def test_unauthenticated_request():
    # Remove the user_id override to simulate missing auth
    del app.dependency_overrides[get_current_user_id]

    response = client.get("/api/v1/mindmaps")
    # 401 or 422 (missing required header)
    assert response.status_code in (401, 422)

    # Restore for subsequent tests
    app.dependency_overrides[get_current_user_id] = override_get_user_id
