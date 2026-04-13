"""Application configuration."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:19006"

    @property
    def allowed_origins_list(self) -> List[str]:
        return self.ALLOWED_ORIGINS.split(",")

    class Config:
        env_file = ".env"


settings = Settings()
