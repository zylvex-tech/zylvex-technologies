from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # External services
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    REALTIME_SERVICE_URL: str = "http://localhost:8004"

    # SendGrid
    SENDGRID_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@zylvex.io"
    EMAIL_FROM_NAME: str = "Zylvex"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8005
    DEBUG: bool = False

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8081"

    class Config:
        env_file = ".env"


settings = Settings()
