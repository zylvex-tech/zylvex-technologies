from pydantic_settings import BaseSettings
from pydantic import model_validator


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

    @model_validator(mode="after")
    def validate_secrets(self) -> "Settings":
        if not self.JWT_SECRET or len(self.JWT_SECRET) < 16:
            raise ValueError(
                "JWT_SECRET is missing or too short. "
                "Set a strong random value (≥16 chars) via the JWT_SECRET env var. "
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        return self

    class Config:
        env_file = ".env"


settings = Settings()
