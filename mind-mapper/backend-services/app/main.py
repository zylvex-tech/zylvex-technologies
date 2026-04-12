"""Mind Mapper FastAPI application."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import engine, Base
from app.api.endpoints import router as api_router

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mind Mapper API", version="1.0.0")

# CORS middleware — origins sourced from environment variable
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:19006"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Mind Mapper API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
