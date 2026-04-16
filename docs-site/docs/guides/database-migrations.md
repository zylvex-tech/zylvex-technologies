---
id: database-migrations
title: Database Migrations Guide
sidebar_label: Database Migrations
slug: /guides/database-migrations
---

# Database Migrations Guide

Zylvex uses **Alembic** for all database schema migrations. This guide covers creating, applying, and rolling back migrations across all backend services.

## Services with Alembic

| Service | Directory | Database |
|---------|-----------|----------|
| Auth | `shared/auth/` | PostgreSQL |
| Spatial Canvas | `spatial-canvas/backend/` | PostGIS |
| Mind Mapper | `mind-mapper/backend-services/` | PostgreSQL |
| Social | `shared/social/` | PostgreSQL |
| Notifications | `shared/notifications/` | PostgreSQL |

---

## Automatic Migrations on Startup

All services run `alembic upgrade head` automatically when their container starts. You typically don't need to run migrations manually during development.

---

## Running Migrations Manually

### Inside Docker (recommended)

```bash
docker compose exec auth-service alembic upgrade head
docker compose exec spatial-canvas-backend alembic upgrade head
docker compose exec mind-mapper-backend alembic upgrade head
docker compose exec social-service alembic upgrade head
docker compose exec notifications-service alembic upgrade head
```

### Outside Docker

```bash
cd shared/auth
pip install -r requirements.txt
export DATABASE_URL=postgresql://auth_user:auth_pass@localhost:5432/auth_db
alembic upgrade head
```

---

## Creating a New Migration

### 1. Modify the SQLAlchemy Model

Example — adding a `bio` field to the `User` model:

```python
# shared/auth/app/models/user.py
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    bio = Column(Text, nullable=True)  # NEW FIELD
```

### 2. Generate the Migration

```bash
docker compose exec auth-service alembic revision --autogenerate -m "add_bio_to_users"
```

This creates a file like `shared/auth/alembic/versions/20240115_add_bio_to_users.py`.

### 3. Review the Generated File

Always review before applying:

```python
def upgrade() -> None:
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'bio')
```

:::warning Review Auto-Generated Migrations
Alembic's `--autogenerate` does **not** detect:
- Renamed columns (sees a drop + add instead)
- Changes to stored procedures or views
- Data migrations (backfilling data)

Always verify the generated SQL before applying to production.
:::

### 4. Apply the Migration

```bash
docker compose exec auth-service alembic upgrade head
```

---

## Checking Migration Status

```bash
# Show current revision
docker compose exec auth-service alembic current

# Show full migration history
docker compose exec auth-service alembic history --verbose
```

---

## Rolling Back

```bash
# Roll back one step
docker compose exec auth-service alembic downgrade -1

# Roll back to a specific revision ID
docker compose exec auth-service alembic downgrade 20240110_initial

# Roll back everything
docker compose exec auth-service alembic downgrade base
```

:::danger Destructive
Rolling back will **drop data**. Never run `downgrade` on production without a prior backup.
:::

---

## PostGIS Migrations (Spatial Canvas)

Spatial Canvas migrations must handle PostGIS extensions:

```python
def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')

    op.create_table(
        'anchors',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        # PostGIS geometry column
        sa.Column('location', geoalchemy2.types.Geometry('POINT', srid=4326)),
        sa.Column('is_public', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('id'),
    )
    # Spatial GiST index for fast radius queries
    op.create_index(
        'idx_anchors_location',
        'anchors',
        ['location'],
        postgresql_using='gist'
    )
```

---

## Migration File Naming Convention

```
YYYYMMDD_short_description.py

Examples:
  20240101_initial_schema.py
  20240115_add_bio_to_users.py
  20240201_add_notifications_table.py
```

---

## Alembic Configuration

Each service has its own `alembic.ini` and `alembic/env.py`. The `env.py` imports the service's `Base` metadata so Alembic can detect model changes:

```python
# alembic/env.py
from app.db.session import Base
from app.models import *  # import all models so they register with Base

target_metadata = Base.metadata
```
