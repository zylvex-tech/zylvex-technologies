"""Application configuration."""

from typing import List, Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:19006"

    # Redis cache (optional — falls back to direct auth service call if unset)
    REDIS_URL: Optional[str] = None

    @property
    def allowed_origins_list(self) -> List[str]:
        return self.ALLOWED_ORIGINS.split(",")

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


settings = Settings()
