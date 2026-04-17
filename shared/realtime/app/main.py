import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.connection_manager import manager
from app.api.ws import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await manager.startup()
    yield
    await manager.shutdown()


app = FastAPI(
    title="Zylvex Realtime Gateway",
    description=(
        "WebSocket gateway for Zylvex Technologies. "
        "Pushes real-time events (new_anchor_nearby, new_reaction, "
        "new_follower, new_mindmap_node) to connected clients via "
        "WebSocket + Redis pub/sub fan-out."
    ),
    version="1.0.0",
    lifespan=lifespan,
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

app.include_router(ws_router)

Instrumentator().instrument(app).expose(app)


@app.get("/")
def root():
    return {
        "message": "Zylvex Realtime Gateway",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "realtime-gateway",
        "connections": manager.connection_count,
    }
