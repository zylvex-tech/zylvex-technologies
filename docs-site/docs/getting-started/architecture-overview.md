---
id: architecture-overview
title: Architecture Overview
sidebar_label: Architecture Overview
slug: /getting-started/architecture-overview
---

# Architecture Overview

This page describes the full Zylvex system: all services, data flows, and how everything connects.

## System Diagram

```mermaid
graph TB
    subgraph Clients["Clients"]
        WEB["Web App\nReact 18 + Vite\n:3000"]
        SC_MOB["Spatial Canvas Mobile\nReact Native + Expo"]
        MM_MOB["Mind Mapper Mobile\nReact Native + Expo"]
        DOCS["Docs Site\nDocusaurus :3001"]
    end

    subgraph API_Layer["API Layer"]
        AUTH["Auth Service\nFastAPI :8001"]
        SC["Spatial Canvas\nFastAPI + PostGIS :8000"]
        MM["Mind Mapper\nFastAPI :8002"]
        SOC["Social Service\nFastAPI :8003"]
        RT["Realtime Gateway\nFastAPI + WS :8004"]
        NOTIF["Notifications\nFastAPI :8005"]
    end

    subgraph Storage["Storage"]
        AUTH_DB[("PostgreSQL\nauth_db")]
        SPATIAL_DB[("PostGIS\nspatial_db")]
        MM_DB[("PostgreSQL\nmm_db")]
        SOC_DB[("PostgreSQL\nsocial_db")]
        NOTIF_DB[("PostgreSQL\nnotifications_db")]
        REDIS[("Redis\npub/sub")]
    end

    subgraph External["External"]
        SENDGRID["SendGrid\nEmail"]
    end

    WEB -->|HTTPS| AUTH
    WEB -->|HTTPS| SC
    WEB -->|HTTPS| MM
    WEB -->|HTTPS| SOC
    WEB -->|WebSocket| RT
    WEB -->|HTTPS| NOTIF

    SC_MOB -->|HTTPS| AUTH
    SC_MOB -->|HTTPS| SC
    MM_MOB -->|HTTPS| AUTH
    MM_MOB -->|HTTPS| MM

    SC -->|GET /auth/verify| AUTH
    MM -->|GET /auth/verify| AUTH
    SOC -->|GET /auth/verify| AUTH
    RT -->|GET /auth/verify| AUTH
    NOTIF -->|GET /auth/verify| AUTH

    SOC -->|GET /api/v1/anchors| SC
    NOTIF -->|POST /internal/push| RT

    AUTH --- AUTH_DB
    SC --- SPATIAL_DB
    MM --- MM_DB
    SOC --- SOC_DB
    NOTIF --- NOTIF_DB
    RT --- REDIS
    NOTIF -->|send email| SENDGRID
```

---

## Data Flow: User Creates an Anchor

```mermaid
sequenceDiagram
    participant App as Mobile App
    participant Auth as Auth :8001
    participant SC as Spatial Canvas :8000
    participant DB as PostGIS DB
    participant NOTIF as Notifications :8005
    participant RT as Realtime :8004

    App->>Auth: POST /auth/login
    Auth-->>App: {access_token, refresh_token}

    App->>SC: POST /api/v1/anchors (Bearer token)
    SC->>Auth: GET /auth/verify (Bearer token)
    Auth-->>SC: {id, sub, email, full_name, is_active}
    SC->>DB: INSERT anchor (location POINT, content, user_id)
    DB-->>SC: anchor row
    SC-->>App: {id, lat, lng, content_type, ...}

    SC->>NOTIF: POST /notifications/send (type=nearby_anchor)
    NOTIF->>RT: POST /internal/push (new_nearby_anchor)
    RT-->>App: WS event {type:"new_nearby_anchor", anchor_id}
```

---

## Data Flow: Social Follow

```mermaid
sequenceDiagram
    participant A as User A
    participant Social as Social :8003
    participant Auth as Auth :8001
    participant NOTIF as Notifications :8005
    participant RT as Realtime :8004
    participant B as User B (WebSocket)

    A->>Social: POST /social/follow/{user_b_id}
    Social->>Auth: GET /auth/verify
    Auth-->>Social: user A identity
    Social->>Social: INSERT follows (follower=A, following=B)
    Social->>NOTIF: POST /notifications/send (type=follow, user_id=B)
    NOTIF->>RT: POST /internal/push (user_id=B)
    RT-->>B: WS event {type:"new_follow", from_user:"A"}
```

---

## Auth Pattern (Critical)

:::warning Single Auth Service
**No downstream service ever verifies JWTs locally.** Every authenticated endpoint calls `GET /auth/verify` on the shared auth service. This is the single source of truth for token validity and revocation.
:::

```mermaid
flowchart LR
    A["Client Request\nAuthorization: Bearer token"] --> B["Downstream Service"]
    B --> C["GET /auth/verify\n:8001"]
    C --> D{Valid?}
    D -->|Yes| E["Return user identity\n{id, sub, email, full_name}"]
    D -->|No| F["401 Unauthorized"]
    E --> G["Process Request"]
```

---

## Service Responsibilities

| Service | Port | Database | Key Responsibilities |
|---------|------|----------|---------------------|
| Auth | 8001 | PostgreSQL | Register, login, JWT issuance, token rotation, revocation |
| Spatial Canvas | 8000 | PostGIS | Anchor CRUD, radius search, content types |
| Mind Mapper | 8002 | PostgreSQL | Mind map + node CRUD, BCI session recording |
| Social | 8003 | PostgreSQL | Follow graph, reactions, nearby/trending feeds |
| Realtime | 8004 | Redis | WebSocket connections, pub/sub fan-out, heartbeat |
| Notifications | 8005 | PostgreSQL | In-app notifications, SendGrid email, push stubs |

---

## Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Auth pattern | Shared service, no local JWT verify | Centralized revocation, single source of truth |
| Spatial indexing | PostGIS Geometry + GiST index | Simplicity (known limitation: inaccurate at high latitudes — ADR-002) |
| Real-time | Redis pub/sub | Horizontal scaling of WebSocket servers |
| BCI integration | Slider simulation → real hardware stub | Allows UX development before hardware availability |
| Mobile framework | React Native + Expo | Cross-platform (iOS + Android) with web parity |

---

## Known Architectural Issues

1. **PostGIS Geometry vs Geography** (`ADR-002`): `Anchor.location` uses `Geometry` with degree-based radius approximation (~50% error at 60°N). Migration to `Geography` + `ST_DWithin` with meters is planned.
2. **No auth token caching** (`ADR-001`): Every request hits auth service → PostgreSQL. Redis TTL cache planned.
3. **No email verification**: `User.is_verified` exists in DB but verification email is not yet sent on register.
4. **Media uploads incomplete**: Anchor supports `image|video|audio` content types but only `text` is implemented; S3/GCS signed URLs planned.
