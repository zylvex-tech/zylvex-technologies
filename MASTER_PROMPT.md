# MASTER_PROMPT — Zylvex Technologies Canonical Context

## 1. What Zylvex Is
Zylvex Technologies is a spatial-social computing platform that overlays digital content onto physical locations via AR and maps cognitive focus as shareable knowledge trees. Products: **Spatial Canvas** (AR anchor platform) and **Mind Mapper** (BCI-driven mind-mapping app).

---

## 2. Products & Tech Stacks

**Spatial Canvas**
- Backend: FastAPI + PostGIS (geoalchemy2), PostgreSQL 15, Alembic, SQLAlchemy, port 8000
- Mobile: React Native + Expo (JavaScript), expo-camera, expo-location, React Navigation

**Mind Mapper**
- Backend: FastAPI, PostgreSQL 15, Alembic, SQLAlchemy, port 8002
- Mobile: React Native + Expo (TypeScript), React Navigation, react-native-svg, @react-native-community/slider
- Desktop: Electron (stub only)
- ML/BCI: Python models (stub only)

**Shared**
- Auth service: FastAPI, PostgreSQL 15, JWT (HS256), bcrypt, slowapi, Alembic, port 8001
- Social graph service: FastAPI, PostgreSQL 15, Alembic, SQLAlchemy, port 8003

---

## 3. Directory Map

```
shared/auth/                   JWT auth service (register/login/refresh/logout/verify)
shared/social/                 Social graph service (follow/unfollow, reactions, feeds)
shared/analytics|billing|notifications/  STUB (empty)
spatial-canvas/backend/        FastAPI + PostGIS anchor CRUD + radius search
spatial-canvas/mobile/         React Native AR camera app (Expo, JS)
spatial-canvas/desktop/        STUB (empty)
mind-mapper/backend-services/  FastAPI mind map + node tree + BCI session API
mind-mapper/mobile-bci/        React Native BCI app with focus slider (Expo, TS)
mind-mapper/desktop-studio|ml-models/  STUB (empty)
web-app/                       React 18 + Vite + TS + Tailwind web frontend (both products)
infrastructure/kubernetes|terraform|monitoring/  STUB (empty)
docs/architecture/             ADRs + auth contract (3 files)
docs/business|development/     STUB (empty)
tests/                         STUB (empty)
scripts/                       cleanup-tokens.sh
docker-compose.full-stack.yml  One-command local stack (3 backends + 3 DBs + web-app)
```

---

## 4. Complete & Production-Ready

- **Auth service**: register, login, logout, refresh token rotation, revocation, /auth/verify (used by all downstream), /auth/me, rate limiting (5/min register, 10/min login), Alembic migrations, 15 tests, Dockerfile, CI
- **Social graph service**: follow/unfollow (idempotent), paginated followers/following, nearby feed (spatial canvas integration), trending feed (7-day reaction window), emoji reactions (👍❤️🔥💡) with uniqueness per user per content, JWT auth via shared auth service, Alembic migrations, 16 tests, Dockerfile, port 8003
- **Spatial Canvas backend**: anchor CRUD, PostGIS radius search, auth middleware, Alembic, 9 tests, Dockerfile, CI
- **Mind Mapper backend**: mind map CRUD, hierarchical node tree (parent_id), BCI session recording (avg_focus, duration, focus_timeline JSON), pagination, ownership checks, rate limiting, 10 tests, Dockerfile, CI
- **Mind Mapper mobile**: Login/Register/Home/MindMapEditor/SessionStats screens, focus slider BCI simulator, color-coded nodes (green/yellow/red), session stats summary, full API integration
- **Spatial Canvas mobile**: camera view with crosshair, tap-to-place anchor with GPS, nearby anchors list, auth screens
- **Web App**: React 18 + Vite + TypeScript + TailwindCSS + Framer Motion at `/web-app/`. Landing page (animated gradient, product cards, waitlist form), auth pages (/login, /register, /forgot-password), dashboard with sidebar, Mind Mapper canvas stub, Spatial Canvas react-leaflet map with anchor pins + detail drawer, social feed skeleton, full typed API client, Dockerfile + nginx, CI in pr-checks.yml
- **CI/CD**: 6 GitHub Actions workflows + web-app CI in pr-checks.yml, Codecov integration, staging SSH deploy
- **Docker Compose full-stack**: 4 app services + 4 DBs with healthchecks, shared network

---

## 5. Stubs / Empty Paths

```
shared/analytics|billing|notifications/
spatial-canvas/desktop/
mind-mapper/desktop-studio|ml-models/
infrastructure/kubernetes|terraform|monitoring/
docs/business|development/
tests/
```

---

## 6. Core Architectural Rules

- **Auth pattern**: Single shared auth service at :8001. Downstream services (SC :8000, MM :8002, Social :8003) NEVER verify JWTs locally. Every authenticated request calls `GET /auth/verify` → `{id, sub, email, full_name, is_active}`.
- **API endpoints**: POST /auth/register, /auth/login, /auth/refresh, /auth/logout · GET /auth/verify, /auth/me
- **Social endpoints**: POST /social/follow/{user_id}, DELETE /social/follow/{user_id}, GET /social/followers/{user_id}, GET /social/following/{user_id}, GET /social/feed/nearby?lat=&lng=&radius_km=, GET /social/feed/trending, POST /social/react, DELETE /social/react/{reaction_id}, GET /social/reactions/{content_type}/{content_id}
- **PostGIS**: `Geometry('POINT', srid=4326)` on `Anchor.location`; radius queries use `radius_km / 111.0` degrees
- **Mobile config**: Both apps read `EXPO_PUBLIC_API_URL` and `EXPO_PUBLIC_AUTH_URL` from `src/config.ts` (MM) / `src/config.js` (SC)
- **JWT**: access token 15 min, refresh token 30 days — stored hashed in DB, rotated on refresh, revocable via logout
- **CORS**: all services restrict via `ALLOWED_ORIGINS` env var (comma-separated)
- **Migrations**: Alembic in all 3 backends; auto-runs on container start
- **Run**: Auth `uvicorn app.main:app --port 8001` · SC `:8000` · MM `:8002` · Social `:8003` · Mobile `expo start`

---

## 7. Environment Variables & .env.example Locations

| File | Key Variables |
|------|--------------|
| `shared/auth/.env.example` | `DATABASE_URL`, `JWT_SECRET`, `JWT_ALGORITHM=HS256`, `ACCESS_TOKEN_EXPIRE_MINUTES=15`, `REFRESH_TOKEN_EXPIRE_DAYS=30`, `BCRYPT_ROUNDS=12`, `ALLOWED_ORIGINS` |
| `shared/social/.env.example` | `DATABASE_URL`, `AUTH_SERVICE_URL`, `SPATIAL_CANVAS_URL`, `ALLOWED_ORIGINS` |
| `spatial-canvas/backend/.env.example` | `DATABASE_URL`, `AUTH_SERVICE_URL`, `ALLOWED_ORIGINS` |
| `mind-mapper/backend-services/.env.example` | `DATABASE_URL`, `AUTH_SERVICE_URL`, `JWT_SECRET`, `PORT=8002` |
| `mind-mapper/mobile-bci/.env.example` | `EXPO_PUBLIC_API_URL=http://localhost:8002`, `EXPO_PUBLIC_AUTH_URL=http://localhost:8001` |
| `spatial-canvas/mobile/.env.example` | `EXPO_PUBLIC_API_URL=http://localhost:8000`, `EXPO_PUBLIC_AUTH_URL=http://localhost:8001` |

**Critical**: Auth service uses `JWT_SECRET` (not `JWT_SECRET_KEY`).

---

## 8. CI/CD — GitHub Actions Workflows

| File | Trigger | Jobs |
|------|---------|------|
| `auth-ci.yml` | push/PR on `shared/auth/**` | test (postgres svc + coverage), lint (black+flake8), docker build |
| `spatial-canvas-ci.yml` | push/PR on `spatial-canvas/backend/**` | test, lint, docker build |
| `mind-mapper-ci.yml` | push/PR on `mind-mapper/**` | test, lint, docker build |
| `mobile-ci.yml` | push/PR on `spatial-canvas/mobile/**` | npm install, lint, type-check |
| `pr-checks.yml` | all PRs to `main` | enforce non-empty description, branch naming, post analysis comment |
| `deploy-staging.yml` | push to `main` (non-md/txt) | SSH deploy auth → spatial → mm in sequence; Slack notify |

Branch conventions: `feature/*`, `bugfix/*`, `fix/*`, `release/*`, `chore/*`, `copilot/*`
Commit format: Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`)

---

## 9. Known Issues

1. **PostGIS Geometry not Geography** (`ADR-002`): `Anchor.location` uses `Geometry`; degree-based radius approximation is ~50% wrong at 60°N. Fix: migrate to `Geography`, use `ST_DWithin` with meters.
2. **No auth token caching** (`ADR-001`): Every request hits auth service → PostgreSQL. No Redis/TTL cache; auth service is a single point of failure.
3. **No email verification**: `User.is_verified` exists in DB but is never set; no verification email sent on register.
4. **No password reset**: No forgot-password or reset-password endpoints.
5. **Mind map editor is a list, not a canvas**: Node `x`/`y` stored in DB but mobile renders a flat `ScrollView` — no graph layout engine.
6. ~~No web frontend~~: **✅ Fixed** — `/web-app/` React 18 + Vite app covers both products (Sprint 1).
7. ~~**No social features**~~: **✅ Fixed** — `/shared/social/` FastAPI microservice on port 8003. Follow/unfollow (idempotent), paginated followers/following lists, emoji reactions (👍❤️🔥💡, unique per user/content), nearby feed (integrates with Spatial Canvas), trending feed (7-day window), JWT auth via shared auth service, Alembic migrations, 16 tests, Dockerfile.
8. **Media uploads incomplete**: Anchor model supports `image|video|audio` content types but only `text` works; no file storage.

---

## 10. Sprint Backlog (Priority Order)

1. Email verification (`POST /auth/verify-email`, send token on register)
2. Password reset (`POST /auth/forgot-password`, `POST /auth/reset-password`)
3. Redis cache for auth token verification (TTL = access token lifetime)
4. Migrate PostGIS `Geometry` → `Geography` (Alembic migration)
5. ~~Social graph service: follow/unfollow, follower/following lists~~ **✅ DONE** — `/shared/social/` port 8003: full follow graph, emoji reactions, nearby+trending feeds, 16 tests, Dockerfile, docker-compose entry.
6. Anchor media uploads: S3/GCS signed URLs for image/video/audio
7. WebSocket layer: anchor proximity alerts, live mind map co-editing
8. ~~Web frontend for Mind Mapper (React + React Flow canvas)~~ **✅ DONE — Sprint 1** — Web app at `/web-app/` (React 18 + Vite + TypeScript + TailwindCSS + Framer Motion). Landing page, auth pages, dashboard, Mind Mapper canvas stub, Spatial Canvas react-leaflet map with anchor pins, social feed skeleton, full typed API client, Docker + nginx, CI integrated.
9. Kubernetes manifests + Helm charts
10. Terraform IaC (AWS/GCP)
11. Monitoring: Prometheus + Grafana + alerting
12. Notifications service (push, email, in-app)
13. Analytics service (event pipeline, funnels, retention)
14. Billing service (Stripe, Free/Pro/Team tiers)
15. Real BCI hardware adapter (Neurosity/OpenBCI/Muse)
16. E2E tests: Playwright (web) + Detox (mobile)
