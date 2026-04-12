import httpx
from fastapi import HTTPException, Header
import os
import uuid

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")


async def get_current_user_id(authorization: str = Header(...)) -> uuid.UUID:
    """Verify JWT token via auth service and return the user's UUID."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ", 1)[1]

    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                f"{AUTH_SERVICE_URL}/auth/verify",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0,
            )
            r.raise_for_status()
            data = r.json()
            return uuid.UUID(data["sub"])
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        except Exception:
            raise HTTPException(status_code=503, detail="Authentication service unavailable")
