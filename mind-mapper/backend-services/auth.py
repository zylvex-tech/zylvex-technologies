import jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Optional
import os
import requests
import uuid

security = HTTPBearer()
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Verify JWT token with auth service"""
    token = credentials.credentials
    
    try:
        # Call auth service to verify token
        response = requests.get(
            f"{AUTH_SERVICE_URL}/verify",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )
        
        user_data = response.json()
        return user_data
        
    except requests.RequestException:
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable"
        )

def get_current_user_id(user_data: dict = Depends(verify_token)) -> uuid.UUID:
    """Extract user ID from verified token data"""
    return uuid.UUID(user_data["sub"])  # sub contains user_id
