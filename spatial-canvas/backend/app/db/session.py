"""Database session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Build engine kwargs — pool_size/max_overflow only work with non-SQLite dialects
_engine_kwargs = {
    "pool_pre_ping": True,
    "echo": settings.ENVIRONMENT == "development",
}
if not settings.DATABASE_URL.startswith("sqlite"):
    _engine_kwargs.update({"pool_size": 20, "max_overflow": 30})

# Create engine
engine = create_engine(settings.DATABASE_URL, **_engine_kwargs)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
