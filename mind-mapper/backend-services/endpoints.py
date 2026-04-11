from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
import uuid
from datetime import datetime

from database import get_db
from models import MindMap, Node, Session as MindMapSession
from schemas import (
    MindMapCreate, MindMapResponse, 
    NodeCreate, NodeResponse,
    SessionCreate, SessionResponse
)
from auth import get_current_user_id

router = APIRouter()

# MindMap endpoints
@router.post("/mindmaps", response_model=MindMapResponse, status_code=status.HTTP_201_CREATED)
def create_mindmap(
    mindmap: MindMapCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new mind map"""
    db_mindmap = MindMap(
        user_id=user_id,
        title=mindmap.title
    )
    db.add(db_mindmap)
    db.commit()
    db.refresh(db_mindmap)
    return db_mindmap

@router.get("/mindmaps", response_model=List[MindMapResponse])
def list_mindmaps(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """List all mind maps for the current user"""
    mindmaps = db.query(MindMap).filter(
        MindMap.user_id == user_id
    ).order_by(desc(MindMap.updated_at)).all()
    
    # Add node count to each mindmap
    for mindmap in mindmaps:
        mindmap.node_count = db.query(func.count(Node.id)).filter(
            Node.mindmap_id == mindmap.id
        ).scalar() or 0
    
    return mindmaps

@router.delete("/mindmaps/{mindmap_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mindmap(
    mindmap_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a mind map (owner only)"""
    mindmap = db.query(MindMap).filter(
        MindMap.id == mindmap_id,
        MindMap.user_id == user_id
    ).first()
    
    if not mindmap:
        raise HTTPException(
            status_code=404,
            detail="Mind map not found or you don't have permission"
        )
    
    db.delete(mindmap)
    db.commit()
    return None

# Node endpoints
@router.post("/mindmaps/{mindmap_id}/nodes", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
def create_node(
    mindmap_id: uuid.UUID,
    node: NodeCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Add a node to a mind map"""
    # Verify mindmap exists and belongs to user
    mindmap = db.query(MindMap).filter(
        MindMap.id == mindmap_id,
        MindMap.user_id == user_id
    ).first()
    
    if not mindmap:
        raise HTTPException(
            status_code=404,
            detail="Mind map not found or you don't have permission"
        )
    
    # Verify parent exists if specified
    if node.parent_id:
        parent = db.query(Node).filter(
            Node.id == node.parent_id,
            Node.mindmap_id == mindmap_id
        ).first()
        if not parent:
            raise HTTPException(
                status_code=404,
                detail="Parent node not found"
            )
    
    db_node = Node(
        mindmap_id=mindmap_id,
        text=node.text,
        focus_level=node.focus_level,
        color=node.color,
        x=node.x,
        y=node.y,
        parent_id=node.parent_id
    )
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    
    # Update mindmap updated_at
    mindmap.updated_at = datetime.utcnow()
    db.commit()
    
    return db_node

@router.delete("/mindmaps/{mindmap_id}/nodes/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node(
    mindmap_id: uuid.UUID,
    node_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Remove a node from a mind map"""
    # Verify mindmap exists and belongs to user
    mindmap = db.query(MindMap).filter(
        MindMap.id == mindmap_id,
        MindMap.user_id == user_id
    ).first()
    
    if not mindmap:
        raise HTTPException(
            status_code=404,
            detail="Mind map not found or you don't have permission"
        )
    
    node = db.query(Node).filter(
        Node.id == node_id,
        Node.mindmap_id == mindmap_id
    ).first()
    
    if not node:
        raise HTTPException(
            status_code=404,
            detail="Node not found"
        )
    
    db.delete(node)
    db.commit()
    
    # Update mindmap updated_at
    mindmap.updated_at = datetime.utcnow()
    db.commit()
    
    return None

# Session endpoints
@router.post("/mindmaps/{mindmap_id}/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    mindmap_id: uuid.UUID,
    session: SessionCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Save session stats for a mind map"""
    # Verify mindmap exists and belongs to user
    mindmap = db.query(MindMap).filter(
        MindMap.id == mindmap_id,
        MindMap.user_id == user_id
    ).first()
    
    if not mindmap:
        raise HTTPException(
            status_code=404,
            detail="Mind map not found or you don't have permission"
        )
    
    db_session = MindMapSession(
        mindmap_id=mindmap_id,
        avg_focus=session.avg_focus,
        duration_seconds=session.duration_seconds,
        node_count=session.node_count,
        focus_timeline=session.focus_timeline
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    return db_session
