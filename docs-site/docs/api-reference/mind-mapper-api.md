---
id: mind-mapper-api
title: Mind Mapper API Reference
sidebar_label: Mind Mapper API
slug: /api-reference/mind-mapper-api
---

# Mind Mapper API Reference

**Base URL:** `http://localhost:8002`  
**Swagger UI:** [http://localhost:8002/docs](http://localhost:8002/docs)  
**Auth:** All endpoints require `Authorization: Bearer <token>`

---

## Mind Map Endpoints

### Create Mind Map

**`POST /api/v1/mindmaps`**

#### Request

```json
{
  "title": "Product Strategy Q1",
  "description": "Mapping out our Q1 product priorities"
}
```

#### Response `201 Created`

```json
{
  "id": "map-uuid-1234",
  "user_id": "user-uuid",
  "title": "Product Strategy Q1",
  "description": "Mapping out our Q1 product priorities",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "node_count": 0
}
```

---

### List Mind Maps

**`GET /api/v1/mindmaps`**

Returns all mind maps owned by the authenticated user.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | `0` | Pagination offset |
| `limit` | int | `20` | Results per page (max 100) |

---

### Get Mind Map

**`GET /api/v1/mindmaps/{map_id}`**

Returns mind map metadata. Use the nodes endpoint for the full node tree.

---

### Update Mind Map

**`PUT /api/v1/mindmaps/{map_id}`**

#### Request

```json
{
  "title": "Updated Title",
  "description": "Updated description"
}
```

---

### Delete Mind Map

**`DELETE /api/v1/mindmaps/{map_id}`**

Deletes the map and **all its nodes**. Returns `204 No Content`.

---

## Node Endpoints

Nodes form a **hierarchical tree** via `parent_id`. Root nodes have `parent_id: null`.

### Node Object

```json
{
  "id": "node-uuid",
  "map_id": "map-uuid-1234",
  "parent_id": null,
  "title": "Core Idea",
  "content": "The central theme",
  "focus_level": 0.85,
  "position_x": 400.0,
  "position_y": 300.0,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**`focus_level`:** Float `0.0–1.0`. BCI-derived focus score at time of creation.

| Range | Colour | Meaning |
|-------|--------|---------|
| ≥ 0.7 | 🟢 Green | High focus |
| 0.4 – 0.69 | 🟡 Yellow | Medium focus |
| < 0.4 | 🔴 Red | Low focus |

---

### Create Node

**`POST /api/v1/mindmaps/{map_id}/nodes`**

#### Request

```json
{
  "title": "Core Idea",
  "content": "The central theme",
  "parent_id": null,
  "focus_level": 0.85,
  "position_x": 400.0,
  "position_y": 300.0
}
```

#### Response `201 Created`

Returns the created node object.

---

### Get Node Tree

**`GET /api/v1/mindmaps/{map_id}/nodes`**

Returns all nodes for a mind map as a **flat list**. The client builds the hierarchy from `parent_id` fields.

#### Response `200 OK`

```json
[
  {
    "id": "node-1",
    "parent_id": null,
    "title": "Root Node",
    "focus_level": 0.9,
    "position_x": 400.0,
    "position_y": 300.0
  },
  {
    "id": "node-2",
    "parent_id": "node-1",
    "title": "Child Node",
    "focus_level": 0.7,
    "position_x": 550.0,
    "position_y": 200.0
  }
]
```

---

### Update Node

**`PUT /api/v1/mindmaps/{map_id}/nodes/{node_id}`**

#### Request

```json
{
  "title": "Updated Title",
  "content": "Updated content",
  "position_x": 500.0,
  "position_y": 350.0
}
```

Used by the web canvas to persist drag-and-drop positions.

---

### Delete Node

**`DELETE /api/v1/mindmaps/{map_id}/nodes/{node_id}`**

:::warning Cascade Delete
Deleting a parent node also deletes all child nodes recursively.
:::

---

## BCI Session Endpoints

BCI sessions record a focus timeline during a mind-mapping session, linking cognitive data to the resulting map.

### BCI Session Object

```json
{
  "id": "session-uuid",
  "map_id": "map-uuid-1234",
  "user_id": "user-uuid",
  "avg_focus": 0.78,
  "duration_seconds": 1800,
  "focus_timeline": [0.6, 0.7, 0.8, 0.9, 0.85, 0.7, 0.65],
  "started_at": "2024-01-15T10:00:00Z",
  "ended_at": "2024-01-15T10:30:00Z"
}
```

**`focus_timeline`:** Array of focus samples recorded throughout the session (one per ~30 seconds).

---

### Record BCI Session

**`POST /api/v1/mindmaps/{map_id}/sessions`**

#### Request

```json
{
  "avg_focus": 0.78,
  "duration_seconds": 1800,
  "focus_timeline": [0.6, 0.7, 0.8, 0.9, 0.85, 0.7, 0.65]
}
```

---

### List BCI Sessions

**`GET /api/v1/mindmaps/{map_id}/sessions`**

Returns all BCI sessions for a mind map, ordered by most recent first.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `AUTH_SERVICE_URL` | ✅ | Auth service base URL |
| `ALLOWED_ORIGINS` | ✅ | Comma-separated CORS origins |
| `PORT` | | Service port (default: `8002`) |
