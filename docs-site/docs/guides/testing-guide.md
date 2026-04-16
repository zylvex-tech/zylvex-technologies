---
id: testing-guide
title: Testing Guide
sidebar_label: Testing Guide
slug: /guides/testing-guide
---

# Testing Guide

This guide covers running all test suites, generating coverage reports, and guidelines for what to test in each service.

## Test Suites Overview

| Service | Test File | Tests | Framework |
|---------|-----------|-------|-----------|
| Auth | `shared/auth/tests/test_auth.py` | 15 | pytest + SQLite in-memory |
| Spatial Canvas | `spatial-canvas/backend/tests/test_anchors.py` | 9 | pytest + pytest-mock (PostGIS) |
| Mind Mapper | `mind-mapper/backend-services/tests/test_endpoints.py` | 10 | pytest + SQLite in-memory |
| Social | `shared/social/tests/test_social.py` | 16 | pytest + SQLite in-memory |
| Notifications | `shared/notifications/tests/test_notifications.py` | 10 | pytest + SQLite in-memory |

---

## Running All Tests

### With Docker (matches CI)

```bash
docker compose run --rm auth-service pytest tests/ -v
docker compose run --rm spatial-canvas-backend pytest tests/ -v
docker compose run --rm mind-mapper-backend pytest tests/ -v
docker compose run --rm social-service pytest tests/ -v
docker compose run --rm notifications-service pytest tests/ -v
```

### Without Docker

```bash
# Auth
cd shared/auth
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v

# Spatial Canvas
cd spatial-canvas/backend
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v

# Mind Mapper
cd mind-mapper/backend-services
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v

# Social
cd shared/social
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v
```

---

## Coverage Reports

```bash
pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html
open htmlcov/index.html
```

Coverage is uploaded to **Codecov** automatically in CI workflows.

**Coverage targets:**
- Core auth logic: 90%+
- API endpoints: 80%+
- Utility functions: 70%+

---

## What to Test

### Auth Service

```text
1. Register — success
2. Register — duplicate email returns 400
3. Login — valid credentials return access + refresh tokens
4. Login — wrong password returns 401
5. Token refresh — rotates both tokens
6. Token refresh — revoked token returns 401
7. Logout — invalidates tokens
8. /auth/verify — valid token returns user identity
9. /auth/verify — expired token returns 401
10. /auth/me — returns current user profile
11. Rate limiting — 6th register attempt returns 429
12-15. Edge cases (inactive user, malformed tokens, etc.)
```

### Spatial Canvas

```text
1. Create anchor — success with valid coordinates
2. Create anchor — unauthorized (no token)
3. List anchors — returns only owner's anchors
4. Get anchor by ID — success
5. Get anchor — 404 for non-existent
6. Update anchor — success
7. Delete anchor — success / 403 for other user's anchor
8. Nearby search — returns anchors within radius (mocked PostGIS)
9. Nearby search — excludes private anchors of other users
```

### Mind Mapper

```text
1. Create mind map
2. List mind maps — pagination
3. Create node with parent_id
4. Get node tree — flat list with parent_id relationships
5. Update node position (drag-to-save)
6. Delete node — cascades to child nodes
7. BCI session record + retrieve
8. Ownership check — 403 for other user's map
9. Rate limiting
10. Pagination skip/limit
```

### Social Service

```text
1-2.  Follow user — success + idempotent re-follow
3.    Unfollow user
4-5.  Get followers / following — paginated
6.    Add reaction (👍 ❤️ 🔥 💡)
7.    Reaction uniqueness enforcement
8.    Remove reaction
9.    Get reactions for content
10.   Nearby feed — returns activity within radius
11.   Trending feed — 7-day window
12-16. Auth checks, edge cases
```

---

## Test Database Strategy

### SQLite In-Memory (Auth, MM, Social, Notifications)

Services that don't require PostGIS use SQLite for fast, zero-dependency testing:

```python
# tests/conftest.py pattern
SQLALCHEMY_DATABASE_URL = "sqlite://:memory:"

@pytest.fixture
def db():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
```

### pytest-mock (Spatial Canvas)

Spatial Canvas mocks PostGIS geometry operations to avoid requiring a PostGIS server in CI:

```python
@pytest.fixture
def mock_postgis(mocker):
    mocker.patch('app.api.v1.endpoints.anchors.func.ST_DWithin', return_value=True)
    mocker.patch('app.api.v1.endpoints.anchors.func.ST_Distance', return_value=0.5)
```

---

## CI Pipeline

| Workflow | Trigger | What Runs |
|----------|---------|-----------|
| `auth-ci.yml` | Push/PR on `shared/auth/**` | pytest + real PostgreSQL service container |
| `spatial-canvas-ci.yml` | Push/PR on `spatial-canvas/backend/**` | pytest with mocked PostGIS |
| `mind-mapper-ci.yml` | Push/PR on `mind-mapper/**` | pytest |
| `pr-checks.yml` | All PRs to `main` | Lint (black + flake8) + quality checks |

The auth CI uses a real PostgreSQL service container:

```yaml
services:
  postgres:
    image: postgres:15-alpine
    env:
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_pass
      POSTGRES_DB: test_db
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
```

---

## Writing a New Endpoint Test

```python
def test_new_endpoint(client, auth_headers):
    response = client.post(
        "/api/v1/new-endpoint",
        json={"field": "value"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["field"] == "value"
    assert "id" in data


@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "TestPass123!",
        "full_name": "Test User",
    })
    resp = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123!",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```
