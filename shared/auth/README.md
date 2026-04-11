# Zylvex Shared Authentication Service

JWT Authentication service shared between SPATIAL CANVAS and MIND MAPPER applications.

## Features

- User registration and login with JWT tokens
- Access tokens (15 min expiry) and refresh tokens (30 day expiry)
- Password hashing with bcrypt (cost factor 12)
- Reusable `get_current_user` middleware for FastAPI applications
- PostgreSQL database with Alembic migrations
- Docker Compose for local development

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development without Docker)

### Using Docker Compose (Recommended)

1. Clone the repository and navigate to `shared/auth/`
2. Start the services:
   ```bash
   docker-compose up -d
   ```
3. The service will be available at `http://localhost:8001`
4. Run database migrations automatically:
   ```bash
   docker-compose exec auth-service alembic upgrade head
   ```

### Local Development

1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Start PostgreSQL database:
   ```bash
   docker-compose up -d auth-db
   ```

5. Run migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the service:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Register User
```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

### Login
```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

Response includes `access_token` and `refresh_token`.

### Get Current User Profile
```bash
curl -X GET http://localhost:8001/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Refresh Access Token
```bash
curl -X POST http://localhost:8001/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

### Logout (Revoke Refresh Token)
```bash
curl -X POST http://localhost:8001/auth/logout \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

## Using the Middleware in Other Services

SPATIAL CANVAS and MIND MAPPER backends can import the authentication middleware:

```python
# In your FastAPI application
from shared.auth.app.middleware.auth import get_current_user

@app.get("/protected-route")
def protected_route(current_user = Depends(get_current_user)):
    return {"user_id": str(current_user.id), "email": current_user.email}
```

Make sure the other services have access to:
1. The same JWT_SECRET environment variable
2. Database connection to the auth database

## Database Migrations

### Create a new migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migrations
```bash
alembic downgrade -1
```

## Environment Variables

See `.env.example` for all available environment variables.

## Health Check

```bash
curl http://localhost:8001/health
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black app/
isort app/
```

### Linting
```bash
flake8 app/
mypy app/
```
