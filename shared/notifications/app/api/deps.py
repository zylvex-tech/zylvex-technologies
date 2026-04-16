"""Dependencies shared by notification endpoints."""

import os
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Validate JWT token by calling the shared auth service GET /auth/verify.

    Returns the user dict: {id, sub, email, full_name, is_active}.
    """
    token = credentials.credentials

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/auth/verify",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0,
            )

        if response.status_code == 200:
            return response.json()

        if response.status_code in (401, 403):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth service error: {response.status_code}",
        )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cannot connect to auth service: {exc}",
        )
