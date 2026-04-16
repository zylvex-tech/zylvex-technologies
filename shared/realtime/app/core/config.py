from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # External services
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    NOTIFICATIONS_SERVICE_URL: str = "http://localhost:8005"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CHANNEL_PREFIX: str = "zylvex:ws:"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8004
    DEBUG: bool = False

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8081"

    # WebSocket heartbeat interval in seconds
    HEARTBEAT_INTERVAL: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
