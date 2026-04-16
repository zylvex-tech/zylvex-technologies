---
id: introduction
title: Introduction to Zylvex
sidebar_label: Introduction
slug: /getting-started/introduction
---

# Introduction to Zylvex Technologies

**Zylvex Technologies** is a **spatial-social computing platform** that bridges the physical and digital worlds through two flagship products: **Spatial Canvas** and **Mind Mapper**.

## What Is Zylvex?

Zylvex enables people to attach persistent digital content to real-world locations (Spatial Canvas) and to map their cognitive focus as shareable, AI-enhanced knowledge trees (Mind Mapper). Together, they form the foundation of a new computing paradigm — one where knowledge lives *in space*, not just in files.

---

## The Two Products

### 🗺️ Spatial Canvas

Spatial Canvas is an **AR anchor platform** that lets users drop digital content (text, images, video, audio) at precise GPS coordinates, discoverable by anyone who walks nearby.

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + PostGIS (geoalchemy2), PostgreSQL 15 |
| Mobile | React Native + Expo (JavaScript), expo-camera, expo-location |
| Auth | Shared JWT service (port 8001) |

**Key capabilities:**
- Drop anchors at exact GPS coordinates
- Radius-based spatial search (PostGIS `ST_DWithin`)
- React/emoji reactions on anchors (👍 ❤️ 🔥 💡)
- AR camera overlay for discovering nearby anchors
- Social feed of nearby activity

### 🧠 Mind Mapper

Mind Mapper is a **BCI-enhanced mind-mapping application** that integrates real focus data (or a simulated slider) to colour-code knowledge nodes by cognitive intensity — showing *how hard you were thinking* when you created each idea.

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, PostgreSQL 15, Alembic |
| Mobile | React Native + Expo (TypeScript), react-native-svg |
| Web | React 18 + Vite + ReactFlow canvas |
| BCI | Python model stubs (Neurosity/OpenBCI/Muse planned) |

**Key capabilities:**
- Hierarchical node trees with parent-child relationships
- BCI session recording (avg_focus, duration, focus_timeline JSON)
- Colour-coded nodes: 🟢 green (high focus ≥0.7) / 🟡 yellow (medium 0.4–0.69) / 🔴 red (low &lt;0.4)
- Drag-and-drop canvas (ReactFlow) with inline edit
- PNG + JSON export of mind maps

---

## The Shared Platform

Both products share a robust microservices foundation:

| Service | Port | Purpose |
|---------|------|---------|
| Auth | 8001 | JWT register/login/refresh/logout/verify |
| Social | 8003 | Follow graph, emoji reactions, feeds |
| Realtime | 8004 | WebSocket gateway (Redis pub/sub) |
| Notifications | 8005 | In-app + email + push (SendGrid) |

---

## The Vision

> *"The next computing platform is not a screen — it is the world itself."*

Zylvex is building toward **spatial-social computing**: a world where knowledge, collaboration, and social connection happen *in physical space*, augmented by AI and biometric data.

**Phase 1 (Now):** AR anchors + BCI mind mapping + social graph → prove the core loop  
**Phase 2:** Email verification, password reset, Redis auth cache, media uploads, Kubernetes IaC  
**Phase 3:** AR glasses support, real BCI hardware (Neurosity Crown), collaborative real-time canvas

---

## Architecture At a Glance

All services communicate through a single shared auth service — no downstream service ever verifies a JWT locally. Every authenticated request makes a `GET /auth/verify` call to obtain `{id, sub, email, full_name, is_active}`.

See the [Architecture Overview](./architecture-overview) for a full system diagram.

---

## Next Steps

- **[Quickstart →](./quickstart)** — Run the full stack in 5 minutes
- **[Architecture Overview →](./architecture-overview)** — Understand the full system diagram
- **[API Reference →](../api-reference/auth-api)** — Explore all endpoints
