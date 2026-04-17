"""Application configuration."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Spatial Canvas API"
    VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str

    # Security
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Environment
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Media storage
    MEDIA_STORAGE_PATH: str = "./media"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
