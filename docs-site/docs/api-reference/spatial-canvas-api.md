---
id: spatial-canvas-api
title: Spatial Canvas API Reference
sidebar_label: Spatial Canvas API
slug: /api-reference/spatial-canvas-api
---

# Spatial Canvas API Reference

**Base URL:** `http://localhost:8000`  
**Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)  
**Auth:** All endpoints require `Authorization: Bearer <token>`

The Spatial Canvas backend handles AR anchor CRUD and PostGIS-powered geospatial queries.

---

## Anchor Object

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-uuid",
  "title": "Hidden Coffee Shop",
  "description": "Best espresso in the city",
  "content_type": "text",
  "content": "Amazing pour-overs. Ask for the special menu.",
  "lat": 37.7749,
  "lng": -122.4194,
  "is_public": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Content types:** `text` | `image` | `video` | `audio`

:::note
Only `text` is fully implemented. `image/video/audio` are accepted but file storage (S3/GCS) is not yet wired up.
:::

---

## Create Anchor

**`POST /api/v1/anchors`**

### Request

```json
{
  "title": "Hidden Coffee Shop",
  "description": "Best espresso in the city",
  "content_type": "text",
  "content": "Amazing pour-overs. Ask for the special menu.",
  "lat": 37.7749,
  "lng": -122.4194,
  "is_public": true
}
```

**Coordinate system:** WGS84 (EPSG:4326) — standard GPS coordinates.

### Response `201 Created`

Returns the full anchor object (see above).

---

## List My Anchors

**`GET /api/v1/anchors`**

Returns all anchors created by the authenticated user.

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | `0` | Pagination offset |
| `limit` | int | `20` | Results per page (max 100) |

### Response `200 OK`

```json
[
  { "id": "...", "title": "Hidden Coffee Shop", ... }
]
```

---

## Get Anchor by ID

**`GET /api/v1/anchors/{anchor_id}`**

Returns `404` if not found or not owned by the authenticated user.

---

## Update Anchor

**`PUT /api/v1/anchors/{anchor_id}`**

### Request

```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "content": "Updated content",
  "is_public": false
}
```

All fields are optional. Location (`lat`/`lng`) cannot be changed after creation.

---

## Delete Anchor

**`DELETE /api/v1/anchors/{anchor_id}`**

Returns `204 No Content` on success.  
Returns `403` if the anchor belongs to a different user.

---

## Radius Search (PostGIS)

**`GET /api/v1/anchors/nearby`**

Finds all **public** anchors within a radius using PostGIS spatial indexing and a GiST index.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lat` | float | ✅ | Centre latitude (WGS84) |
| `lng` | float | ✅ | Centre longitude (WGS84) |
| `radius_km` | float | ✅ | Search radius in kilometres |
| `limit` | int | | Max results (default 50) |

### Example Request

```bash
curl "http://localhost:8000/api/v1/anchors/nearby?lat=37.7749&lng=-122.4194&radius_km=1.0" \
  -H "Authorization: Bearer <token>"
```

### Response `200 OK`

```json
[
  {
    "id": "anchor-uuid",
    "title": "Hidden Coffee Shop",
    "lat": 37.7749,
    "lng": -122.4194,
    "distance_km": 0.23,
    "content_type": "text",
    "user_id": "user-uuid"
  }
]
```

### PostGIS Query

```sql
SELECT *,
  ST_Distance(location, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)) * 111.0 AS distance_km
FROM anchors
WHERE
  is_public = true
  AND ST_DWithin(
    location,
    ST_SetSRID(ST_MakePoint(:lng, :lat), 4326),
    :radius_km / 111.0   -- degree approximation
  )
ORDER BY distance_km ASC
LIMIT :limit;
```

:::caution Known Limitation (ADR-002)
The degree-based radius approximation (`radius_km / 111.0`) introduces ~50% error at latitudes above 60°N (e.g., Scandinavia, Alaska). Migration to `ST_Geography` + meters is planned.
:::

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | PostgreSQL+PostGIS connection string |
| `AUTH_SERVICE_URL` | ✅ | Auth service base URL (e.g., `http://auth-service:8001`) |
| `ALLOWED_ORIGINS` | ✅ | Comma-separated CORS origins |
