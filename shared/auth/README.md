# Zylvex Shared Auth Service

Centralized JWT authentication service shared by all Zylvex products (Spatial Canvas and Mind Mapper).

## Endpoints

| Method | Path | Auth Required | Description |
|---|---|---|---|
| POST | /auth/register | No | Register a new user |
| POST | /auth/login | No | Login and receive access + refresh tokens |
| POST | /auth/refresh | No | Exchange refresh token for new token pair |
| POST | /auth/logout | No | Revoke a refresh token |
| GET | /auth/me | Yes | Return full user profile |
| GET | /auth/verify | Yes | Lightweight token verification (used by downstream services) |

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | — | PostgreSQL connection string |
| `JWT_SECRET` | — | Secret key for JWT signing (required) |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `30` | Refresh token lifetime |
| `ALLOWED_ORIGINS` | `http://localhost:3000,...` | Comma-separated CORS allowlist |

## Local Development

```bash
cp .env.example .env   # fill in JWT_SECRET and DATABASE_URL
docker compose up --build
```

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v --cov=app
```

## Inter-Service Usage

Other services verify tokens by calling `GET /auth/verify`. See `docs/architecture/auth-service-api.md` for the full contract.
