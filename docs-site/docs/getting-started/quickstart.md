---
id: quickstart
title: Quickstart — Run the Full Stack
sidebar_label: Quickstart (5 min)
slug: /getting-started/quickstart
---

# Quickstart — Full Stack in 5 Minutes

This guide gets every Zylvex service running locally using a single `docker compose` command.

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Docker Desktop | 24+ | [docker.com](https://www.docker.com/products/docker-desktop/) |
| Docker Compose | v2 (bundled) | Included with Docker Desktop |
| Git | any | [git-scm.com](https://git-scm.com) |

> **Apple Silicon (M1/M2/M3):** Fully supported. All images are multi-arch.

---

## 1. Clone the Repository

```bash
git clone https://github.com/zylvex-tech/zylvex-technologies.git
cd zylvex-technologies
```

## 2. Set Required Environment Variables

Create a `.env` file with the only required secret:

```bash
echo "JWT_SECRET=$(openssl rand -hex 32)" > .env
```

Optional — add a SendGrid key for email notifications:

```bash
echo "SENDGRID_API_KEY=SG.your_key_here" >> .env
echo "EMAIL_FROM=noreply@yourdomain.com" >> .env
```

## 3. Start the Full Stack

```bash
docker compose -f docker-compose.full-stack.yml up --build
```

This starts **14 containers**:

| Container | Port | Role |
|-----------|------|------|
| zylvex-auth | 8001 | Auth service |
| zylvex-spatial | 8000 | Spatial Canvas backend |
| zylvex-mm | 8002 | Mind Mapper backend |
| zylvex-social | 8003 | Social graph service |
| zylvex-realtime | 8004 | WebSocket gateway |
| zylvex-notifications | 8005 | Notifications service |
| zylvex-web | 3000 | React web app |
| zylvex-docs | 3001 | This documentation site |
| zylvex-auth-db | — | PostgreSQL for auth |
| zylvex-spatial-db | — | PostGIS for spatial data |
| zylvex-mm-db | — | PostgreSQL for mind maps |
| zylvex-social-db | — | PostgreSQL for social graph |
| zylvex-notifications-db | — | PostgreSQL for notifications |
| zylvex-redis | — | Redis for pub/sub |

First-time startup takes ~3-5 minutes (building images and pulling base images).

## 4. Verify Everything Is Up

```bash
# Check all containers are healthy
docker compose -f docker-compose.full-stack.yml ps

# Quick health checks
curl http://localhost:8001/health   # Auth service
curl http://localhost:8000/health   # Spatial Canvas
curl http://localhost:8002/health   # Mind Mapper
curl http://localhost:8003/health   # Social
```

## 5. Open the Web App

Navigate to **[http://localhost:3000](http://localhost:3000)**

1. Click **Get Started** → Register an account
2. Explore the **Spatial Canvas** map — drop your first anchor
3. Open **Mind Mapper** → create a mind map → add nodes
4. Try the **notifications bell** — follow another user to see a real-time toast

## 6. Explore the APIs (Swagger UI)

All services expose interactive Swagger UI docs:

| Service | Swagger URL |
|---------|------------|
| Auth | [http://localhost:8001/docs](http://localhost:8001/docs) |
| Spatial Canvas | [http://localhost:8000/docs](http://localhost:8000/docs) |
| Mind Mapper | [http://localhost:8002/docs](http://localhost:8002/docs) |
| Social | [http://localhost:8003/docs](http://localhost:8003/docs) |
| Realtime | [http://localhost:8004/docs](http://localhost:8004/docs) |
| Notifications | [http://localhost:8005/docs](http://localhost:8005/docs) |

---

## Stopping the Stack

```bash
# Stop all containers (preserves data volumes)
docker compose -f docker-compose.full-stack.yml down

# Stop and remove all data (clean slate)
docker compose -f docker-compose.full-stack.yml down -v
```

---

## Troubleshooting

### Port conflicts

If a port is already in use, edit `docker-compose.full-stack.yml` and change the host port (first number):

```yaml
ports: ["8001:8001"]  # change left side only
```

### PostGIS container fails to start

```bash
docker pull postgis/postgis:15-3.4-alpine
docker compose -f docker-compose.full-stack.yml up postgres-spatial
```

### Auth service can't connect to database

The `depends_on: condition: service_healthy` handles ordering, but on a slow machine a restart helps:

```bash
docker compose -f docker-compose.full-stack.yml restart auth-service
```

### Resetting a single service

```bash
docker compose -f docker-compose.full-stack.yml restart mind-mapper-backend
```

---

## Running Mobile Apps

See the [Mobile Setup Guide](../guides/mobile-setup) for iOS Simulator and Android Emulator instructions.
