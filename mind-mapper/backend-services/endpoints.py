from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
import uuid
from datetime import datetime

from database import get_db
from models import MindMap, Node, Session as MindMapSession
from schemas import (
    MindMapCreate, MindMapResponse,
    NodeCreate, NodeUpdate, NodeResponse,
    SessionCreate, SessionResponse
)
from auth import get_current_user_id

router = APIRouter()


def _get_owned_mindmap(db: Session, mindmap_id: uuid.UUID, user_id: uuid.UUID) -> MindMap:
    """Return mindmap if it exists and is owned by user, else raise 404."""
    mindmap = db.query(MindMap).filter(
        MindMap.id == mindmap_id,
        MindMap.user_id == user_id
    ).first()
    if not mindmap:
        raise HTTPException(
            status_code=404,
            detail="Mind map not found or you don't have permission"
        )
    return mindmap


# ---------------------------------------------------------------------------
# MindMap endpoints
# ---------------------------------------------------------------------------

@router.post("/mindmaps", response_model=MindMapResponse, status_code=status.HTTP_201_CREATED)
async def create_mindmap(
    mindmap: MindMapCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new mind map"""
    db_mindmap = MindMap(user_id=user_id, title=mindmap.title)
    db.add(db_mindmap)
    db.commit()
    db.refresh(db_mindmap)
    db_mindmap.node_count = 0
    return db_mindmap


@router.get("/mindmaps", response_model=List[MindMapResponse])
async def list_mindmaps(
    skip: int = 0,
    limit: int = Query(100, ge=1, le=500),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """List mind maps for the current user (paginated)"""
    mindmaps = db.query(MindMap).filter(
        MindMap.user_id == user_id
    ).order_by(desc(MindMap.updated_at)).offset(skip).limit(limit).all()

    for mindmap in mindmaps:
        mindmap.node_count = db.query(func.count(Node.id)).filter(
            Node.mindmap_id == mindmap.id
        ).scalar() or 0

    return mindmaps


@router.delete("/mindmaps/{mindmap_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mindmap(
    mindmap_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a mind map (owner only)"""
    mindmap = _get_owned_mindmap(db, mindmap_id, user_id)
    db.delete(mindmap)
    db.commit()
    return None


# ---------------------------------------------------------------------------
# Node endpoints
# ---------------------------------------------------------------------------

@router.get("/mindmaps/{mindmap_id}/nodes", response_model=List[NodeResponse])
async def list_nodes(
    mindmap_id: uuid.UUID,
    skip: int = 0,
    limit: int = Query(100, ge=1, le=500),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all nodes for a mind map"""
    _get_owned_mindmap(db, mindmap_id, user_id)
    nodes = db.query(Node).filter(
        Node.mindmap_id == mindmap_id
    ).order_by(Node.created_at).offset(skip).limit(limit).all()
    return nodes


@router.post("/mindmaps/{mindmap_id}/nodes", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
async def create_node(
    mindmap_id: uuid.UUID,
    node: NodeCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Add a node to a mind map"""
    mindmap = _get_owned_mindmap(db, mindmap_id, user_id)

    if node.parent_id:
        parent = db.query(Node).filter(
            Node.id == node.parent_id,
            Node.mindmap_id == mindmap_id
        ).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent node not found")

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

    mindmap.updated_at = datetime.utcnow()
    db.commit()

    return db_node


@router.put("/mindmaps/{mindmap_id}/nodes/{node_id}", response_model=NodeResponse)
async def update_node(
    mindmap_id: uuid.UUID,
    node_id: uuid.UUID,
    node_update: NodeUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Partially update a node (text, color, position, focus_level)"""
    mindmap = _get_owned_mindmap(db, mindmap_id, user_id)

    db_node = db.query(Node).filter(
        Node.id == node_id,
        Node.mindmap_id == mindmap_id
    ).first()
    if not db_node:
        raise HTTPException(status_code=404, detail="Node not found")

    update_data = node_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_node, field, value)

    db.commit()
    db.refresh(db_node)

    mindmap.updated_at = datetime.utcnow()
    db.commit()

    return db_node


@router.delete("/mindmaps/{mindmap_id}/nodes/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node(
    mindmap_id: uuid.UUID,
    node_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Remove a node from a mind map"""
    mindmap = _get_owned_mindmap(db, mindmap_id, user_id)

    node = db.query(Node).filter(
        Node.id == node_id,
        Node.mindmap_id == mindmap_id
    ).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    db.delete(node)
    db.commit()

    mindmap.updated_at = datetime.utcnow()
    db.commit()

    return None


# ---------------------------------------------------------------------------
# Session endpoints
# ---------------------------------------------------------------------------

@router.get("/mindmaps/{mindmap_id}/sessions", response_model=List[SessionResponse])
async def list_sessions(
    mindmap_id: uuid.UUID,
    skip: int = 0,
    limit: int = Query(100, ge=1, le=500),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all BCI sessions for a mind map (most recent first)"""
    _get_owned_mindmap(db, mindmap_id, user_id)
    sessions = db.query(MindMapSession).filter(
        MindMapSession.mindmap_id == mindmap_id
    ).order_by(desc(MindMapSession.created_at)).offset(skip).limit(limit).all()
    return sessions


@router.post("/mindmaps/{mindmap_id}/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    mindmap_id: uuid.UUID,
    session: SessionCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Save session stats for a mind map"""
    _get_owned_mindmap(db, mindmap_id, user_id)

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

