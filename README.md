# Zylvex Technologies

Enterprise-grade monorepo for spatial AR and mind-mapping applications.

## Products

**Spatial Canvas** — Augmented reality anchor platform. Place geo-tagged content in the physical world via mobile camera. Powered by PostGIS geospatial queries.

**Mind Mapper** — Brain-computer interface mind-mapping application. Visualize cognitive focus as interactive node trees. Ships with a focus simulator; real BCI hardware adapters planned.

## Quick Start

Prerequisites: Docker, Docker Compose

```bash
git clone https://github.com/zylvex-tech/zylvex-technologies.git
cd zylvex-technologies
cp shared/auth/.env.example shared/auth/.env          # set JWT_SECRET
cp spatial-canvas/backend/.env.example spatial-canvas/backend/.env
cp mind-mapper/backend-services/.env.example mind-mapper/backend-services/.env
docker compose -f docker-compose.full-stack.yml up --build
```

| Service | URL | Docs |
|---|---|---|
| Auth Service | http://localhost:8001 | http://localhost:8001/docs |
| Spatial Canvas API | http://localhost:8000 | http://localhost:8000/docs |
| Mind Mapper API | http://localhost:8002 | http://localhost:8002/docs |

## Repository Structure

```
zylvex-technologies/
├── shared/auth/                  Shared JWT authentication service
├── spatial-canvas/
│   ├── backend/                  FastAPI + PostGIS anchor API
│   └── mobile/                   React Native AR camera app (Expo)
├── mind-mapper/
│   ├── backend-services/         FastAPI mind map & BCI session API
│   └── mobile-bci/               React Native BCI app (Expo, TypeScript)
├── infrastructure/               Kubernetes, Terraform, monitoring (planned)
├── docs/architecture/            Architecture decision records
├── docker-compose.full-stack.yml One-command local development
└── CONTRIBUTING.md
```

## CI/CD

| Workflow | Trigger |
|---|---|
| `auth-ci.yml` | Push/PR touching `shared/auth/**` |
| `spatial-canvas-ci.yml` | Push/PR touching `spatial-canvas/backend/**` |
| `mobile-ci.yml` | Push/PR touching `spatial-canvas/mobile/**` |
| `mind-mapper-ci.yml` | Push/PR touching `mind-mapper/**` |
| `pr-checks.yml` | All PRs to `main` |
| `deploy-staging.yml` | Push to `main` |

See `CONTRIBUTING.md` for development workflow and branch conventions.

## License

MIT
