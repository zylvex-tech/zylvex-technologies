"""Application configuration."""

from typing import List, Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Spatial Canvas API"
    VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str

    # Auth service
    AUTH_SERVICE_URL: str

    # Redis cache (optional — falls back to direct auth service call if unset)
    REDIS_URL: Optional[str] = None

    # Security
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Environment
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    @model_validator(mode="after")
    def validate_required_settings(self) -> "Settings":
        if not self.DATABASE_URL:
            raise ValueError(
                "DATABASE_URL is not set. "
                "Provide the PostgreSQL connection string via the DATABASE_URL env var."
            )
        if not self.AUTH_SERVICE_URL:
            raise ValueError(
                "AUTH_SERVICE_URL is not set. "
                "Set AUTH_SERVICE_URL to the base URL of the auth service (e.g. http://localhost:8001)."
            )
        return self

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
