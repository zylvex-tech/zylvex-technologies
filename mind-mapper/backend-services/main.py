from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from database import engine, get_db
from models import Base, MindMap, Node, Session as MindMapSession
from schemas import (
    MindMapCreate, MindMapResponse, 
    NodeCreate, NodeResponse,
    SessionCreate, SessionResponse
)
from endpoints import router as api_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mind Mapper API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:19006"],
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
