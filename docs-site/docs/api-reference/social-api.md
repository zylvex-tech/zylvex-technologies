---
id: social-api
title: Social API Reference
sidebar_label: Social API
slug: /api-reference/social-api
---

# Social API Reference

**Base URL:** `http://localhost:8003`  
**Swagger UI:** [http://localhost:8003/docs](http://localhost:8003/docs)  
**Auth:** All endpoints require `Authorization: Bearer <token>`

---

## Social Graph

### Follow a User

**`POST /social/follow/{user_id}`**

Follows the target user. **Idempotent** — following an already-followed user returns `200` without error.

#### Response `200 OK`

```json
{
  "follower_id": "my-user-uuid",
  "following_id": "target-user-uuid",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### Unfollow a User

**`DELETE /social/follow/{user_id}`**

Removes the follow relationship. Idempotent — unfollowing a non-followed user returns `200`.

---

### Get Followers

**`GET /social/followers/{user_id}`**

Returns a paginated list of users who follow the given user.

#### Query Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `skip` | `0` | Pagination offset |
| `limit` | `20` | Results per page |

#### Response `200 OK`

```json
{
  "user_id": "target-user-uuid",
  "followers": [
    { "user_id": "follower-uuid", "followed_at": "2024-01-15T10:30:00Z" }
  ],
  "total": 142,
  "skip": 0,
  "limit": 20
}
```

---

### Get Following

**`GET /social/following/{user_id}`**

Returns a paginated list of users that the given user follows.

---

## Reactions

Reactions are emoji engagements on content (anchors, mind maps). Each user can have **one reaction per content item** — enforced by a unique constraint on `(user_id, content_type, content_id, emoji)`.

**Supported emojis:** 👍 ❤️ 🔥 💡

### Add Reaction

**`POST /social/react`**

#### Request

```json
{
  "content_type": "anchor",
  "content_id": "anchor-uuid",
  "emoji": "🔥"
}
```

**`content_type`:** `anchor` | `mindmap`

#### Response `201 Created`

```json
{
  "id": "reaction-uuid",
  "user_id": "user-uuid",
  "content_type": "anchor",
  "content_id": "anchor-uuid",
  "emoji": "🔥",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### Remove Reaction

**`DELETE /social/react/{reaction_id}`**

Only the reaction owner can delete it. Returns `403` if not owned by the authenticated user.

---

### Get Reactions for Content

**`GET /social/reactions/{content_type}/{content_id}`**

Returns all reactions for a specific content item, grouped by emoji.

#### Response `200 OK`

```json
{
  "content_type": "anchor",
  "content_id": "anchor-uuid",
  "reactions": [
    { "emoji": "🔥", "count": 12, "user_reacted": true },
    { "emoji": "❤️",  "count": 8,  "user_reacted": false },
    { "emoji": "👍", "count": 5,  "user_reacted": false },
    { "emoji": "💡", "count": 3,  "user_reacted": false }
  ],
  "total": 28
}
```

---

## Social Feeds

### Nearby Feed

**`GET /social/feed/nearby`**

Returns recent social activity (anchors + reactions) within a geographic radius. Integrates with the Spatial Canvas service.

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lat` | float | ✅ | Latitude |
| `lng` | float | ✅ | Longitude |
| `radius_km` | float | ✅ | Radius in kilometres |
| `limit` | int | | Max results (default 20) |

#### Example

```bash
curl "http://localhost:8003/social/feed/nearby?lat=37.7749&lng=-122.4194&radius_km=2.0" \
  -H "Authorization: Bearer <token>"
```

#### Response `200 OK`

```json
[
  {
    "type": "anchor_created",
    "anchor_id": "anchor-uuid",
    "title": "Hidden Coffee Shop",
    "user_id": "user-uuid",
    "lat": 37.7749,
    "lng": -122.4194,
    "distance_km": 0.45,
    "created_at": "2024-01-15T10:30:00Z"
  },
  {
    "type": "reaction",
    "anchor_id": "anchor-uuid",
    "emoji": "🔥",
    "user_id": "reactor-uuid",
    "created_at": "2024-01-15T10:35:00Z"
  }
]
```

---

### Trending Feed

**`GET /social/feed/trending`**

Returns content with the most reactions in the last **7 days**, sorted by reaction count descending.

#### Response `200 OK`

```json
[
  {
    "content_type": "anchor",
    "content_id": "anchor-uuid",
    "title": "The Best View in SF",
    "reaction_count": 47,
    "top_emojis": ["🔥", "❤️", "💡"],
    "created_at": "2024-01-10T08:00:00Z"
  }
]
```

---

## Realtime Events

Social actions trigger WebSocket events via the Realtime Gateway on port 8004:

| Action | WS Event Type | Recipients |
|--------|--------------|-----------|
| Follow | `new_follow` | The followed user |
| Reaction | `new_reaction` | Content owner |
| Nearby anchor created | `new_nearby_anchor` | Nearby users |
| Collaboration invite | `new_collaboration_invite` | Invited user |

WebSocket connection: `ws://localhost:8004/ws/{user_id}?token=<access_token>`

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `AUTH_SERVICE_URL` | ✅ | Auth service base URL |
| `SPATIAL_CANVAS_URL` | ✅ | Spatial Canvas URL (for nearby feed) |
| `ALLOWED_ORIGINS` | ✅ | Comma-separated CORS origins |
