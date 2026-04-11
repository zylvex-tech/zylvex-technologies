from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

# MindMap schemas
class MindMapBase(BaseModel):
    title: str = Field(..., max_length=255)

class MindMapCreate(MindMapBase):
    pass

class MindMapResponse(MindMapBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    node_count: int = 0
    
    class Config:
        from_attributes = True

# Node schemas
class NodeBase(BaseModel):
    text: str
    focus_level: int = Field(..., ge=0, le=100)
    color: str
    x: float = 0.0
    y: float = 0.0
    parent_id: Optional[uuid.UUID] = None

class NodeCreate(NodeBase):
    pass

class NodeResponse(NodeBase):
    id: uuid.UUID
    mindmap_id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# Session schemas
class SessionBase(BaseModel):
    avg_focus: float = Field(..., ge=0, le=100)
    duration_seconds: int = Field(..., gt=0)
    node_count: int = Field(..., ge=0)
    focus_timeline: List[float]

class SessionCreate(SessionBase):
    pass

class SessionResponse(SessionBase):
    id: uuid.UUID
    mindmap_id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
