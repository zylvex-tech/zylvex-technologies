---
id: roadmap
title: Roadmap
sidebar_label: Roadmap
slug: /business/roadmap
---

# Product Roadmap

## Visual Timeline

```mermaid
gantt
    title Zylvex Technologies — Product Roadmap
    dateFormat  YYYY-MM
    axisFormat  %b '%y

    section Phase 1 — Foundation
    Auth service + social graph           :done,    p1a, 2024-01, 2024-03
    Spatial Canvas backend + mobile       :done,    p1b, 2024-01, 2024-03
    Mind Mapper backend + mobile          :done,    p1c, 2024-02, 2024-04
    Web app (React 18 + Vite)             :done,    p1d, 2024-03, 2024-05
    Realtime gateway (WebSocket + Redis)  :done,    p1e, 2024-04, 2024-05
    Notifications service (SendGrid)      :done,    p1f, 2024-05, 2024-06
    Docker Compose full-stack             :done,    p1g, 2024-01, 2024-06
    Documentation site (Docusaurus)       :done,    p1h, 2024-06, 2024-07

    section Phase 2 — Quality and Scale
    Email verification                    :active,  p2a, 2024-07, 2024-08
    Password reset flow                   :active,  p2b, 2024-07, 2024-08
    Redis auth token cache                :         p2c, 2024-08, 2024-09
    PostGIS Geometry to Geography         :         p2d, 2024-08, 2024-09
    Anchor media uploads (S3/GCS)         :         p2e, 2024-09, 2024-10
    Kubernetes manifests + Helm charts    :         p2f, 2024-09, 2024-11
    Terraform IaC (AWS/GCP)              :         p2g, 2024-10, 2024-12
    Prometheus + Grafana monitoring       :         p2h, 2024-10, 2024-12
    E2E tests (Playwright + Detox)        :         p2i, 2024-11, 2025-01

    section Phase 3 — Platform
    Real BCI hardware adapter            :         p3a, 2025-01, 2025-04
    AR glasses SDK (Vision Pro / Quest)  :         p3b, 2025-02, 2025-06
    Collaborative real-time canvas       :         p3c, 2025-03, 2025-07
    Analytics service (event pipeline)   :         p3d, 2025-01, 2025-05
    Billing service (Stripe tiers)       :         p3e, 2025-02, 2025-04
    Creator marketplace                  :         p3f, 2025-04, 2025-09
    Spatial knowledge graph (AI + LLM)   :         p3g, 2025-06, 2025-12
    Enterprise SDK + SSO                 :         p3h, 2025-09, 2026-03
```

---

## Phase 1 — Foundation ✅ Complete

The core platform is live and production-ready.

| Milestone | Status | Details |
|-----------|--------|---------|
| Auth service | ✅ | Register, login, JWT rotation, revocation, 15 tests |
| Spatial Canvas backend | ✅ | Anchor CRUD, PostGIS radius search, 9 tests |
| Mind Mapper backend | ✅ | Mind maps, nodes, BCI sessions, 10 tests |
| Web app (React 18) | ✅ | Vite + ReactFlow canvas, dark/light mode |
| Social graph service | ✅ | Follow graph, reactions, feeds, 16 tests |
| Realtime gateway | ✅ | WebSocket + Redis pub/sub, heartbeat |
| Notifications service | ✅ | In-app + SendGrid email + push stubs, 10 tests |
| Docker Compose full-stack | ✅ | One-command local dev environment |
| Documentation site | ✅ | This Docusaurus site |

---

## Phase 2 — Quality & Scale (Q3–Q4 2024)

Focus: production hardening, remaining auth features, infrastructure.

### Auth Completions

**Email Verification**
- `POST /auth/verify-email` endpoint
- Send verification email on register (SendGrid)
- Set `User.is_verified = true` on verification

**Password Reset**
- `POST /auth/forgot-password` — send reset token via email
- `POST /auth/reset-password` — consume token, update password

### Performance

**Redis Auth Token Cache**
- Cache `/auth/verify` responses in Redis (TTL = access token lifetime)
- Eliminates PostgreSQL roundtrip on every authenticated request
- Expected ~90% reduction in auth service DB load

**PostGIS Geometry → Geography**
- Alembic migration: `Anchor.location` from `Geometry` to `Geography`
- Use `ST_DWithin` with meters instead of degree approximation
- Fixes the ~50% accuracy error at high latitudes (ADR-002)

### Storage

**Anchor Media Uploads**
- S3/GCS signed URL generation for `image/video/audio` content types
- CDN integration for low-latency delivery

### Infrastructure

**Kubernetes + Terraform**
- Helm charts for all 6 services
- Terraform modules for AWS (EKS + RDS + ElastiCache) and GCP (GKE + Cloud SQL + Memorystore)

**Monitoring**
- Prometheus metrics on all services
- Grafana dashboards (request rate, error rate, p50/p99 latency)
- PagerDuty alerting

---

## Phase 3 — Platform (2025)

Focus: AR hardware, real BCI, monetization, enterprise.

### BCI Hardware Integration

Native adapters for:
- **Neurosity Crown** — 8-channel EEG, focus/calm scores via Neurosity SDK
- **OpenBCI Ganglion** — raw EEG, custom FFT-based focus algorithm
- **Muse 2** — 4-channel EEG, lowest-cost entry point

### AR Integration

- **Apple Vision Pro** — visionOS spatial anchors, SharePlay for collaborative viewing
- **Meta Quest / WebXR** — cross-platform anchor viewer
- **Ray-Ban Meta smart glasses** — overlay anchors in field of view

### Collaborative Real-Time Canvas

- Multiple users editing the same mind map simultaneously
- CRDT-based conflict resolution
- Presence indicators and cursor sharing

### Analytics Service

- Kafka event pipeline
- User funnel analysis, anchor engagement metrics
- BCI correlation analysis (focus vs. node quality over time)

### Billing Service

- Stripe integration
- Free/Pro/Team/Enterprise tier enforcement (see [Monetization](./monetization))
- Usage metering (API calls, anchor storage, BCI session hours)

---

## Sprint Backlog (Immediate Next Steps)

In priority order:

1. Email verification (`POST /auth/verify-email`)
2. Password reset (`POST /auth/forgot-password` + `/auth/reset-password`)
3. Redis cache for auth token verification
4. PostGIS `Geometry` → `Geography` migration
5. Anchor media uploads (S3/GCS signed URLs)
6. Kubernetes manifests + Helm charts
7. Terraform IaC (AWS/GCP)
8. Prometheus + Grafana monitoring
9. E2E tests: Playwright (web) + Detox (mobile)
10. Real BCI hardware adapter (Neurosity Crown first)
