---
id: auth-api
title: Auth API Reference
sidebar_label: Auth API
slug: /api-reference/auth-api
---

# Auth API Reference

**Base URL:** `http://localhost:8001`  
**Swagger UI:** [http://localhost:8001/docs](http://localhost:8001/docs)

The Auth service is the **single JWT authority** for the entire Zylvex platform. All downstream services call `GET /auth/verify` — none verify tokens locally.

---

## Register

**`POST /auth/register`**

Rate limited: **5 requests/minute per IP**

### Request

```json
{
  "email": "alice@example.com",
  "password": "StrongPass123!",
  "full_name": "Alice Smith"
}
```

### Response `201 Created`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@example.com",
  "full_name": "Alice Smith",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Errors

| Code | Reason |
|------|--------|
| `400` | Email already registered |
| `422` | Validation error (invalid email format) |
| `429` | Rate limit exceeded (5/min) |

---

## Login

**`POST /auth/login`**

Rate limited: **10 requests/minute per IP**

### Request

```json
{
  "email": "alice@example.com",
  "password": "StrongPass123!"
}
```

### Response `200 OK`

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<opaque>",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Token lifetimes:**
- Access token: **15 minutes**
- Refresh token: **30 days** (stored hashed in DB, rotated on each refresh)

### Errors

| Code | Reason |
|------|--------|
| `401` | Invalid credentials |
| `422` | Validation error |
| `429` | Rate limit exceeded (10/min) |

---

## Refresh Token

**`POST /auth/refresh`**

### Request

```json
{
  "refresh_token": "<opaque>"
}
```

### Response `200 OK`

```json
{
  "access_token": "<new-jwt>",
  "refresh_token": "<new-opaque>",
  "token_type": "bearer",
  "expires_in": 900
}
```

:::info Token Rotation
The old refresh token is invalidated on every call. Always store the new refresh token returned in each response.
:::

---

## Logout

**`POST /auth/logout`**

Requires: `Authorization: Bearer <access_token>`

### Request

```json
{
  "refresh_token": "<opaque>"
}
```

### Response `200 OK`

```json
{
  "message": "Successfully logged out"
}
```

Both the access token and refresh token are revoked in the database immediately.

---

## Verify Token

**`GET /auth/verify`**

Used internally by all downstream services. Requires: `Authorization: Bearer <access_token>`

### Response `200 OK`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "sub": "alice@example.com",
  "email": "alice@example.com",
  "full_name": "Alice Smith",
  "is_active": true
}
```

### Errors

| Code | Reason |
|------|--------|
| `401` | Token invalid, expired, or revoked |
| `403` | User account inactive |

---

## Get Current User

**`GET /auth/me`**

Requires: `Authorization: Bearer <access_token>`

### Response `200 OK`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@example.com",
  "full_name": "Alice Smith",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## JWT Token Structure

**Algorithm:** `HS256` — symmetric HMAC SHA-256

### Access Token Payload

```json
{
  "sub": "alice@example.com",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "exp": 1705312800,
  "iat": 1705311900,
  "type": "access"
}
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET` | **required** | HMAC signing secret (32+ chars recommended) |
| `JWT_ALGORITHM` | `HS256` | Signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `30` | Refresh token lifetime |
| `BCRYPT_ROUNDS` | `12` | bcrypt cost factor |
| `ALLOWED_ORIGINS` | **required** | Comma-separated CORS origins |

:::caution
The auth service uses `JWT_SECRET` — **not** `JWT_SECRET_KEY`. Double-check your `.env` file.
:::
