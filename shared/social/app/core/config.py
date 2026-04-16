from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # External services
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    SPATIAL_CANVAS_URL: str = "http://localhost:8000"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8003
    DEBUG: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
