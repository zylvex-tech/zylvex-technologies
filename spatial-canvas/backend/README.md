# Spatial Canvas Backend

Geospatial anchor REST API built with FastAPI and PostGIS. Allows mobile clients to place and discover geo-tagged AR content.

## Prerequisites

- Docker + Docker Compose (PostGIS provided via container)
- Python 3.11+ for local development

## Endpoints

| Method | Path | Auth Required | Description |
|---|---|---|---|
| POST | /api/v1/anchors | Yes | Create a new spatial anchor |
| GET | /api/v1/anchors | No | Get nearby anchors (lat/lon/radius_km query params) |
| GET | /api/v1/anchors/mine | Yes | Get anchors created by the current user |
| GET | /api/v1/anchors/{id} | No | Fetch a single anchor by ID |
| DELETE | /api/v1/anchors/{id} | Yes | Delete an anchor (owner only) |

## Coordinate System

WGS84 (SRID 4326). Radius is specified in kilometres.

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL + PostGIS connection string |
| `JWT_SECRET_KEY` | JWT signing key (must match auth service) |
| `AUTH_SERVICE_URL` | URL of the shared auth service |
| `ALLOWED_ORIGINS` | Comma-separated CORS allowlist |

## Local Development

```bash
cp .env.example .env
docker compose up --build
```

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v --cov=app
```
