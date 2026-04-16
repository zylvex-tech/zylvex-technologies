"""Authentication middleware for Mind Mapper backend."""

import logging
import uuid

import httpx
from fastapi import HTTPException, Header

from app.core.config import settings
from app.core.token_cache import get_cached_user, make_redis_client, set_cached_user

logger = logging.getLogger(__name__)

# Build the Redis client once at module load time (None if Redis is unavailable).
_redis_client = make_redis_client(settings.REDIS_URL) if settings.REDIS_URL else None


async def get_current_user_id(authorization: str = Header(...)) -> uuid.UUID:
    """Verify JWT token via auth service and return the user's UUID.

    Checks the Redis token cache first (TTL = 300 s).  On cache hit the auth
    service is not contacted.  If Redis is unreachable the function falls
    through transparently to the auth service.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ", 1)[1]

    # --- Redis cache lookup ---
    cached = get_cached_user(_redis_client, token)
    if cached is not None:
        return uuid.UUID(cached["user_id"])

    # --- Cache miss: call auth service ---
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                f"{settings.AUTH_SERVICE_URL}/auth/verify",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0,
            )
            r.raise_for_status()
            data = r.json()
            # Populate cache so subsequent requests for this token are fast.
            set_cached_user(_redis_client, token, {"id": data["sub"], "roles": []})
            return uuid.UUID(data["sub"])
        except httpx.HTTPStatusError as exc:
            logger.warning("Auth service rejected token: %s", exc.response.status_code)
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        except (httpx.RequestError, httpx.TimeoutException) as exc:
            logger.error("Auth service unreachable: %s", exc)
            raise HTTPException(
                status_code=503, detail="Authentication service unavailable"
            )
        except Exception as exc:
            logger.exception("Unexpected error during token verification: %s", exc)
            raise HTTPException(
                status_code=503, detail="Authentication service unavailable"
            )
