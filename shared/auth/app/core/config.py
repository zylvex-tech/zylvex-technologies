from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    # Token Expiration
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Security
    BCRYPT_ROUNDS: int = 12

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    DEBUG: bool = False

    # Email (SendGrid)
    SENDGRID_API_KEY: Optional[str] = None
    EMAIL_FROM: str = "noreply@zylvex.io"
    EMAIL_FROM_NAME: str = "Zylvex"

    # Frontend URL for email links
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()
