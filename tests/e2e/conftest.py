"""Pytest configuration and shared fixtures for E2E tests."""

import os
import time
import uuid

import httpx
import pytest

# ---------------------------------------------------------------------------
# Base URLs — configurable via environment variables
# ---------------------------------------------------------------------------
AUTH_URL = os.getenv("AUTH_URL", "http://localhost:8001")
SPATIAL_URL = os.getenv("SPATIAL_URL", "http://localhost:8000")
MINDMAP_URL = os.getenv("MINDMAP_URL", "http://localhost:8002")
SOCIAL_URL = os.getenv("SOCIAL_URL", "http://localhost:8003")
REALTIME_URL = os.getenv("REALTIME_URL", "http://localhost:8004")
NOTIFICATIONS_URL = os.getenv("NOTIFICATIONS_URL", "http://localhost:8005")
WEB_APP_URL = os.getenv("WEB_APP_URL", "http://localhost:3000")


# ---------------------------------------------------------------------------
# Service readiness helper — retry with exponential back-off (max 30 s)
# ---------------------------------------------------------------------------
def _wait_for_service(url: str, path: str = "/health", timeout: float = 30.0):
    """Block until *url/path* returns HTTP 200 or *timeout* seconds elapse."""
    deadline = time.monotonic() + timeout
    delay = 0.5
    last_exc: Exception | None = None
    while time.monotonic() < deadline:
        try:
            resp = httpx.get(f"{url}{path}", timeout=5)
            if resp.status_code == 200:
                return
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
        time.sleep(delay)
        delay = min(delay * 2, 4)
    raise RuntimeError(
        f"Service at {url}{path} not ready after {timeout}s "
        f"(last error: {last_exc})"
    )


# ---------------------------------------------------------------------------
# Session-scoped fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def wait_for_services():
    """Wait for all backend services to be healthy before running tests."""
    for url in [AUTH_URL, SPATIAL_URL, MINDMAP_URL, SOCIAL_URL]:
        _wait_for_service(url)


@pytest.fixture(scope="session")
def http_client():
    """Shared httpx client with generous timeout."""
    with httpx.Client(timeout=30) as client:
        yield client


# ---------------------------------------------------------------------------
# Unique identity helpers — avoid state conflicts across test runs
# ---------------------------------------------------------------------------
def _unique_email() -> str:
    return f"e2e-{uuid.uuid4().hex[:12]}@zylvex-test.io"


def _unique_name() -> str:
    return f"E2E User {uuid.uuid4().hex[:8]}"


@pytest.fixture()
def unique_email():
    return _unique_email()


@pytest.fixture()
def unique_name():
    return _unique_name()


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------
def register_user(
    client: httpx.Client,
    email: str | None = None,
    password: str = "SecurePass123!",
    full_name: str | None = None,
):
    """Register a new user and return the response."""
    email = email or _unique_email()
    full_name = full_name or _unique_name()
    return client.post(
        f"{AUTH_URL}/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": full_name,
        },
    )


def login_user(client: httpx.Client, email: str, password: str = "SecurePass123!"):
    """Login and return the response (contains access_token, refresh_token)."""
    return client.post(
        f"{AUTH_URL}/auth/login",
        json={"email": email, "password": password},
    )


def auth_headers(access_token: str) -> dict[str, str]:
    """Return Authorization header dict."""
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture()
def registered_user(http_client):
    """Register a fresh user and return (email, password, register_response)."""
    email = _unique_email()
    password = "SecurePass123!"
    resp = register_user(http_client, email=email, password=password)
    return email, password, resp


@pytest.fixture()
def authenticated_user(http_client, registered_user):
    """Register + login, return (email, password, access_token, refresh_token)."""
    email, password, _ = registered_user
    resp = login_user(http_client, email, password)
    data = resp.json()
    return email, password, data["access_token"], data["refresh_token"]
