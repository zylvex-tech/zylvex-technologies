# Spatial Canvas Backend

Backend API for Spatial Canvas - a persistent AR creation platform that allows users to place 3D objects and text anchors in the real world.

## Features

- **Spatial Anchors**: Store and retrieve 3D objects/text in real-world locations
- **Geospatial Queries**: Find anchors near specific coordinates using PostGIS
- **RESTful API**: FastAPI-based endpoints with OpenAPI documentation
- **Production Ready**: Error handling, logging, Docker support
- **Database Migrations**: Alembic for schema management

## API Endpoints

### POST /api/v1/anchors
Create a new spatial anchor.

**Request Body:**
```json
{
  "user_id": "user123",
  "content_type": "3d_object",
  "content_data": "{\"url\":\"https://example.com/model.glb\"}",
  "title": "My 3D Model",
  "description": "A cool 3D model placed here",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "altitude": 10.5
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "content_type": "3d_object",
  "content_data": "{\"url\":\"https://example.com/model.glb\"}",
  "title": "My 3D Model",
  "description": "A cool 3D model placed here",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "altitude": 10.5,
  "created_at": "2026-04-10T17:20:00Z",
  "updated_at": null,
  "is_active": "Y"
}
```

### GET /api/v1/anchors
Get anchors near a location.

**Query Parameters:**
- `latitude` (required): Latitude in decimal degrees (-90 to 90)
- `longitude` (required): Longitude in decimal degrees (-180 to 180)
- `radius_km` (optional, default=1.0): Search radius in kilometers (0.1 to 100)

**Example:**
```
GET /api/v1/anchors?latitude=40.7128&longitude=-74.0060&radius_km=0.5
```

**Response:**
```json
{
  "anchors": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "user123",
      "content_type": "3d_object",
      "content_data": "{\"url\":\"https://example.com/model.glb\"}",
      "title": "My 3D Model",
      "description": "A cool 3D model placed here",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "altitude": 10.5,
      "created_at": "2026-04-10T17:20:00Z",
      "updated_at": null,
      "is_active": "Y"
    }
  ],
  "count": 1,
  "radius_km": 0.5
}
```

### GET /api/v1/anchors/{anchor_id}
Get a specific anchor by ID.

## Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)

### Local Development

1. Clone the repository
2. Navigate to the backend directory:
```bash
cd spatial-canvas
```

3. Copy environment configuration:
```bash
cp backend/.env.example backend/.env
# Update .env with your values if needed
```

4. Start services:
```bash
docker-compose up -d
```

5. Run database migrations:
```bash
docker-compose exec backend alembic upgrade head
```

6. Access the API:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Development

### Running Tests
```bash
docker-compose exec backend pytest
```

### Creating Migrations
```bash
docker-compose exec backend alembic revision --autogenerate -m "Description of changes"
docker-compose exec backend alembic upgrade head
```

### Code Quality
```bash
# Format code
docker-compose exec backend black .

# Sort imports
docker-compose exec backend isort .
```

## Environment Variables

Required variables in `.env`:
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `ENVIRONMENT`: `development`, `staging`, or `production`
- `CORS_ORIGINS`: Comma-separated list of allowed origins

## Database Schema

The main table is `anchors` with:
- `id`: UUID primary key
- `user_id`: User identifier
- `content_type`: Type of content (3d_object, text, image, video)
- `content_data`: JSON string or URL
- `latitude`, `longitude`, `altitude`: Spatial coordinates
- `location`: PostGIS POINTZ geometry for spatial queries
- `created_at`, `updated_at`: Timestamps
- `is_active`: Soft delete flag (Y/N)

## Technology Stack

- **Backend**: Python FastAPI
- **Database**: PostgreSQL with PostGIS extension
- **ORM**: SQLAlchemy with GeoAlchemy2
- **Migrations**: Alembic
- **Containerization**: Docker + Docker Compose
- **API Documentation**: OpenAPI (Swagger)

## Project Structure

```
spatial-canvas/backend/
├── app/
│   ├── api/v1/           # API endpoints
│   ├── core/             # Configuration
│   └── db/               # Database setup
├── models/               # SQLAlchemy models
├── schemas/              # Pydantic schemas
├── services/             # Business logic
├── utils/                # Utility functions
├── alembic/              # Database migrations
├── requirements.txt      # Dependencies
├── Dockerfile            # Container definition
└── README.md            # This file
```

## License

Proprietary - © Zylvex Technologies Ltd
