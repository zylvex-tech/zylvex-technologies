"""Comprehensive auth service test suite (15 test cases)."""

import os
import time
import pytest
import jwt
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set required env vars before importing the app
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_auth.db")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-ci")

from app.main import app
from app.db.base import Base
from app.db.session import get_db

# ---------------------------------------------------------------------------
# Test database setup (SQLite in-memory)
# ---------------------------------------------------------------------------

SQLALCHEMY_DATABASE_URL = "sqlite://"  # in-memory
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_USER_PAYLOAD = {
    "email": "alice@example.com",
    "password": "securepass123",
    "full_name": "Alice Test",
}


def _register_and_login(email=None, password=None):
    payload = dict(_USER_PAYLOAD)
    if email:
        payload["email"] = email
    if password:
        payload["password"] = password
    client.post("/auth/register", json=payload)
    resp = client.post(
        "/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    return resp.json()


# ---------------------------------------------------------------------------
# 1. Health check
# ---------------------------------------------------------------------------

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# ---------------------------------------------------------------------------
# 2. Register
# ---------------------------------------------------------------------------

def test_register_user():
    response = client.post("/auth/register", json=_USER_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == _USER_PAYLOAD["email"]
    assert data["full_name"] == _USER_PAYLOAD["full_name"]
    assert "id" in data
    assert data["is_active"] is True
    assert data["is_verified"] is False


# ---------------------------------------------------------------------------
# 3. Duplicate email
# ---------------------------------------------------------------------------

def test_register_duplicate_email():
    client.post("/auth/register", json=_USER_PAYLOAD)
    response = client.post("/auth/register", json=_USER_PAYLOAD)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


# ---------------------------------------------------------------------------
# 4. Login — success
# ---------------------------------------------------------------------------

def test_login_success():
    client.post("/auth/register", json=_USER_PAYLOAD)
    response = client.post(
        "/auth/login",
        json={"email": _USER_PAYLOAD["email"], "password": _USER_PAYLOAD["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


# ---------------------------------------------------------------------------
# 5. Login — wrong password
# ---------------------------------------------------------------------------

def test_login_wrong_password():
    client.post("/auth/register", json=_USER_PAYLOAD)
    response = client.post(
        "/auth/login",
        json={"email": _USER_PAYLOAD["email"], "password": "wrongpassword"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# 6. Login — unknown email
# ---------------------------------------------------------------------------

def test_login_unknown_email():
    response = client.post(
        "/auth/login",
        json={"email": "ghost@example.com", "password": "pass"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# 7. GET /auth/me — authenticated
# ---------------------------------------------------------------------------

def test_get_me_authenticated():
    tokens = _register_and_login()
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == _USER_PAYLOAD["email"]


# ---------------------------------------------------------------------------
# 8. GET /auth/me — no token
# ---------------------------------------------------------------------------

def test_get_me_no_token():
    response = client.get("/auth/me")
    assert response.status_code in (401, 403)


# ---------------------------------------------------------------------------
# 9. GET /auth/me — expired token
# ---------------------------------------------------------------------------

def test_get_me_expired_token():
    secret = os.environ.get("JWT_SECRET", "test-secret-key-for-ci")
    expired_token = jwt.encode(
        {"sub": "00000000-0000-0000-0000-000000000001", "exp": int(time.time()) - 3600, "type": "access"},
        secret,
        algorithm="HS256",
    )
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# 10. GET /auth/verify — valid token
# ---------------------------------------------------------------------------

def test_verify_token():
    tokens = _register_and_login()
    response = client.get(
        "/auth/verify",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "sub" in data
    assert data["email"] == _USER_PAYLOAD["email"]
    assert data["is_active"] is True


# ---------------------------------------------------------------------------
# 11. Refresh token — exchange for new access token
# ---------------------------------------------------------------------------

def test_refresh_token():
    tokens = _register_and_login()
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


# ---------------------------------------------------------------------------
# 12. Refresh token rotation — old token revoked after use
# ---------------------------------------------------------------------------

def test_refresh_token_rotation():
    tokens = _register_and_login()
    old_refresh = tokens["refresh_token"]

    # Use the refresh token once
    resp1 = client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert resp1.status_code == 200

    # Using the same refresh token again should fail
    resp2 = client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert resp2.status_code == 401


# ---------------------------------------------------------------------------
# 13. Logout — returns 200
# ---------------------------------------------------------------------------

def test_logout():
    tokens = _register_and_login()
    response = client.post(
        "/auth/logout",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# 14. Logout revokes token — refresh after logout should fail
# ---------------------------------------------------------------------------

def test_logout_revokes_token():
    tokens = _register_and_login()
    refresh = tokens["refresh_token"]

    # Logout
    client.post("/auth/logout", json={"refresh_token": refresh})

    # Attempt to use the revoked token
    response = client.post("/auth/refresh", json={"refresh_token": refresh})
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# 15. Deactivated user cannot login
# ---------------------------------------------------------------------------

def test_deactivated_user_cannot_login():
    # Register & get token with admin-style direct DB manipulation
    client.post("/auth/register", json=_USER_PAYLOAD)

    # Deactivate the user directly via the DB
    db = next(override_get_db())
    from app.models.user import User
    user = db.query(User).filter(User.email == _USER_PAYLOAD["email"]).first()
    user.is_active = False
    db.commit()
    db.close()

    # Attempt login
    response = client.post(
        "/auth/login",
        json={"email": _USER_PAYLOAD["email"], "password": _USER_PAYLOAD["password"]},
    )
    assert response.status_code == 403
