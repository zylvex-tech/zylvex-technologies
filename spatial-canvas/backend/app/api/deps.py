"""Dependencies for API endpoints."""

import logging

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID

from app.core.config import settings
from app.core.token_cache import get_cached_user, make_redis_client, set_cached_user

logger = logging.getLogger(__name__)

security = HTTPBearer()

# Build the Redis client once at module load time (None if Redis is unavailable).
_redis_client = make_redis_client(settings.REDIS_URL) if settings.REDIS_URL else None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Validate JWT token with auth service and return user data.

    Checks the Redis token cache first (TTL = 300 s).  On cache hit the auth
    service is not contacted.  If Redis is unreachable the function falls
    through transparently to the auth service.
    """
    token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # --- Redis cache lookup ---
    cached = get_cached_user(_redis_client, token)
    if cached is not None:
        # Reconstruct a minimal user dict from cached data so callers get
        # the same shape regardless of cache hit/miss.
        return {"id": cached["user_id"], "roles": cached.get("roles", [])}

    # --- Cache miss: call auth service ---
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0,
            )

            if response.status_code == 200:
                user_data = response.json()
                set_cached_user(_redis_client, token, user_data)
                return user_data
            elif response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Auth service error: {response.status_code}",
                )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cannot connect to auth service: {str(e)}",
        )


def get_current_user_id(user_data: dict = Depends(get_current_user)) -> UUID:
    """Extract user_id from user data."""
    return UUID(user_data["id"])


def get_current_user_name(user_data: dict = Depends(get_current_user)) -> str:
    """Extract full_name from user data."""
    return user_data.get("full_name", "Unknown User")
