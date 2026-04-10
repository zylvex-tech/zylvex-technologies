"""API router for v1 endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints import anchors

api_router = APIRouter()

# Include endpoints
api_router.include_router(anchors.router, prefix="/anchors", tags=["anchors"])
