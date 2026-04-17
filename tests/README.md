# Tests — Zylvex Technologies

End-to-end and load tests for the Zylvex platform.

## Structure

```
tests/
  e2e/
    conftest.py          — pytest fixtures, base URLs, shared auth helper
    test_auth_flow.py    — full auth E2E scenarios (8 tests)
    test_anchor_flow.py  — spatial canvas E2E scenarios (8 tests)
    test_mindmap_flow.py — mind mapper E2E scenarios (6 tests)
    test_social_flow.py  — social graph E2E scenarios (6 tests)
    test_web_app.py      — web app UI E2E with Playwright (5 tests)
  load/
    locustfile.py        — Locust load test scenarios
  docker-compose.tests.yml
  requirements.txt
  README.md
```

## Running E2E Tests

### Option 1: Docker Compose (recommended)

This spins up the full stack and runs all E2E tests:

```bash
cd tests
docker compose -f docker-compose.tests.yml up --build --abort-on-container-exit e2e-runner
```

Test results (JUnit XML) will be in `tests/results/junit.xml`.

### Option 2: Local (full stack already running)

```bash
cd tests
pip install -r requirements.txt
playwright install chromium

# Set service URLs (defaults to localhost)
export AUTH_URL=http://localhost:8001
export SPATIAL_URL=http://localhost:8000
export MINDMAP_URL=http://localhost:8002
export SOCIAL_URL=http://localhost:8003
export WEB_APP_URL=http://localhost:3000

# Run all E2E tests
python -m pytest e2e/ -v

# Run specific test file
python -m pytest e2e/test_auth_flow.py -v

# Run specific test
python -m pytest e2e/test_auth_flow.py::TestAuthFlow::test_login_success -v
```

## Running Load Tests

```bash
cd tests

# Interactive web UI (localhost:8089)
locust -f load/locustfile.py --host http://localhost

# Headless: 100 users, 10 users/sec ramp, 5 min duration
locust -f load/locustfile.py --host http://localhost --headless -u 100 -r 10 -t 5m

# Run only read tasks
locust -f load/locustfile.py --host http://localhost --tags read --headless -u 50 -r 5 -t 2m
```

## CI Integration

E2E tests run automatically on PRs to `main` via `.github/workflows/e2e-tests.yml`.

The workflow:
1. Builds all service Docker images
2. Starts the full stack with Docker Compose
3. Runs `pytest e2e/` against the running services
4. Uploads JUnit XML test results as an artifact

## Test Scenarios

| File | Tests | Description |
|------|-------|-------------|
| `test_auth_flow.py` | 8 | Register, login, refresh, logout, protected endpoints |
| `test_anchor_flow.py` | 8 | Create/read/update/delete anchors, nearby search, media upload |
| `test_mindmap_flow.py` | 6 | Create/read/update/delete mind maps and nodes |
| `test_social_flow.py` | 6 | Follow/unfollow, followers list, nearby feed |
| `test_web_app.py` | 5 | Landing page, sign up, registration, dashboard, navigation |

## Configuration

All service URLs are configurable via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTH_URL` | `http://localhost:8001` | Auth service base URL |
| `SPATIAL_URL` | `http://localhost:8000` | Spatial Canvas backend URL |
| `MINDMAP_URL` | `http://localhost:8002` | Mind Mapper backend URL |
| `SOCIAL_URL` | `http://localhost:8003` | Social service URL |
| `WEB_APP_URL` | `http://localhost:3000` | Web app URL |
