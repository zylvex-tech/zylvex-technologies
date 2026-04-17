import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.notifications import router as notifications_router


app = FastAPI(
    title="Zylvex Notifications Service",
    description=(
        "Notifications microservice for Zylvex Technologies. "
        "Handles in-app, email (SendGrid), and push notification delivery "
        "for follow, reaction, nearby_anchor, and collaboration_invite events."
    ),
    version="1.0.0",
)

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

app.include_router(notifications_router)

Instrumentator().instrument(app).expose(app)


@app.get("/")
def root():
    return {
        "message": "Zylvex Notifications Service",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
