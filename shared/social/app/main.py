import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.social import router as social_router

app = FastAPI(
    title="Zylvex Social Graph Service",
    description=(
        "Social graph microservice for Zylvex Technologies. "
        "Handles follow/unfollow relationships, emoji reactions on anchors and "
        "mind maps, and personalised + trending social feeds."
    ),
    version="1.0.0",
)

# CORS middleware — origins sourced from environment variable
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8081"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(social_router, prefix="/social", tags=["social"])

Instrumentator().instrument(app).expose(app)


@app.get("/")
def root():
    return {
        "message": "Zylvex Social Graph Service",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
