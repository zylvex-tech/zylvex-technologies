"""Authentication middleware for Mind Mapper backend."""

import httpx
from fastapi import HTTPException, Header
import logging
import uuid

from app.core.config import settings

logger = logging.getLogger(__name__)


async def get_current_user_id(authorization: str = Header(...)) -> uuid.UUID:
    """Verify JWT token via auth service and return the user's UUID."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ", 1)[1]

    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                f"{settings.AUTH_SERVICE_URL}/auth/verify",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0,
            )
            r.raise_for_status()
            data = r.json()
            return uuid.UUID(data["sub"])
        except httpx.HTTPStatusError as exc:
            logger.warning("Auth service rejected token: %s", exc.response.status_code)
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        except (httpx.RequestError, httpx.TimeoutException) as exc:
            logger.error("Auth service unreachable: %s", exc)
            raise HTTPException(status_code=503, detail="Authentication service unavailable")
        except Exception as exc:
            logger.exception("Unexpected error during token verification: %s", exc)
            raise HTTPException(status_code=503, detail="Authentication service unavailable")
