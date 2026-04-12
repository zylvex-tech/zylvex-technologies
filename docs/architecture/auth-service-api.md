# Auth Service — Inter-Service API Contract

Base URL configured via `AUTH_SERVICE_URL` environment variable.

## GET /auth/me
Returns full profile of the authenticated user.
**Required header:** `Authorization: Bearer <access_token>`
**Response:** `{ id, email, full_name, is_active, is_verified, created_at }`
**Errors:** 401 (invalid/expired token), 503 (DB unavailable)

## GET /auth/verify
Lightweight token verification returning minimal identity payload.
Used by all downstream services to authenticate requests.
**Required header:** `Authorization: Bearer <access_token>`
**Response:** `{ id, sub, email, full_name, is_active }`
**Errors:** 401 (invalid/expired token)

Both endpoints must be called with a valid Bearer token obtained from `/auth/login` or `/auth/refresh`.
