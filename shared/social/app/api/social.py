"""Social graph API endpoints."""

import os
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import List
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.social import Follow, Reaction, VALID_EMOJIS
from app.schemas.social import (
    AnchorFeedItem,
    FollowResponse,
    PaginatedUserList,
    ReactionCreate,
    ReactionListResponse,
    ReactionResponse,
    TrendingFeedResponse,
    TrendingItem,
    UserListItem,
)

router = APIRouter()
logger = logging.getLogger(__name__)

SPATIAL_CANVAS_URL = os.getenv("SPATIAL_CANVAS_URL", "http://localhost:8000")


# ---------------------------------------------------------------------------
# Follow / Unfollow
# ---------------------------------------------------------------------------


@router.post(
    "/follow/{user_id}",
    response_model=FollowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Follow a user",
    description=(
        "Follow the user identified by *user_id*. "
        "If the follow relationship already exists the existing record is returned "
        "with HTTP 200. Self-follow is rejected with HTTP 400. "
        "Requires JWT authentication."
    ),
)
async def follow_user(
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Follow a user. Idempotent — following an already-followed user returns 200."""
    follower_id = UUID(current_user["id"])

    if follower_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot follow yourself.",
        )

    existing = (
        db.query(Follow)
        .filter(Follow.follower_id == follower_id, Follow.following_id == user_id)
        .first()
    )
    if existing:
        from fastapi.responses import JSONResponse
        from fastapi.encoders import jsonable_encoder

        # Idempotent: return existing record with 200
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(FollowResponse.model_validate(existing)),
        )

    follow = Follow(follower_id=follower_id, following_id=user_id)
    db.add(follow)
    db.commit()
    db.refresh(follow)
    return follow


@router.delete(
    "/follow/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unfollow a user",
    description=(
        "Remove a follow relationship. Idempotent — unfollowing a user you "
        "do not currently follow returns HTTP 204 without error. "
        "Requires JWT authentication."
    ),
)
async def unfollow_user(
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Unfollow a user. Idempotent — no error if the follow does not exist."""
    follower_id = UUID(current_user["id"])

    existing = (
        db.query(Follow)
        .filter(Follow.follower_id == follower_id, Follow.following_id == user_id)
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()

    return None


# ---------------------------------------------------------------------------
# Followers / Following lists
# ---------------------------------------------------------------------------


@router.get(
    "/followers/{user_id}",
    response_model=PaginatedUserList,
    summary="List followers",
    description=(
        "Return a paginated list of users who follow *user_id*. "
        "Each item includes the follower's user ID and the time they followed. "
        "Public endpoint — no authentication required."
    ),
)
def get_followers(
    user_id: UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum records to return"),
    db: Session = Depends(get_db),
):
    """Return paginated followers for a user."""
    query = db.query(Follow).filter(Follow.following_id == user_id)
    total = query.count()
    follows = query.order_by(desc(Follow.created_at)).offset(skip).limit(limit).all()
    items = [
        UserListItem(user_id=f.follower_id, created_at=f.created_at) for f in follows
    ]
    return PaginatedUserList(items=items, total=total, skip=skip, limit=limit)


@router.get(
    "/following/{user_id}",
    response_model=PaginatedUserList,
    summary="List following",
    description=(
        "Return a paginated list of users that *user_id* follows. "
        "Each item includes the followed user's ID and the time the follow was made. "
        "Public endpoint — no authentication required."
    ),
)
def get_following(
    user_id: UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum records to return"),
    db: Session = Depends(get_db),
):
    """Return paginated list of users that user_id follows."""
    query = db.query(Follow).filter(Follow.follower_id == user_id)
    total = query.count()
    follows = query.order_by(desc(Follow.created_at)).offset(skip).limit(limit).all()
    items = [
        UserListItem(user_id=f.following_id, created_at=f.created_at) for f in follows
    ]
    return PaginatedUserList(items=items, total=total, skip=skip, limit=limit)


# ---------------------------------------------------------------------------
# Feeds
# ---------------------------------------------------------------------------


async def _fetch_nearby_anchors(lat: float, lng: float, radius_km: float) -> list:
    """Call the Spatial Canvas backend to fetch anchors near a location."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{SPATIAL_CANVAS_URL}/api/v1/anchors",
                params={"latitude": lat, "longitude": lng, "radius_km": radius_km},
                timeout=10.0,
            )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("anchors", [])
    except httpx.RequestError as exc:
        logger.warning("Could not reach Spatial Canvas service: %s", exc)
    return []


@router.get(
    "/feed/nearby",
    response_model=List[AnchorFeedItem],
    summary="Nearby social feed",
    description=(
        "Return spatial anchors near *lat*/*lng* within *radius_km* kilometres. "
        "Anchors created by users you follow are annotated with `is_followed=true` "
        "and sorted before public anchors. Results are ordered by recency. "
        "Requires JWT authentication."
    ),
)
async def get_nearby_feed(
    lat: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees"),
    radius_km: float = Query(5.0, ge=0.1, le=100, description="Search radius in km"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return nearby anchors, prioritising anchors from followed users."""
    requester_id = UUID(current_user["id"])

    # Fetch IDs of users the requester follows
    following_ids = {
        str(f.following_id)
        for f in db.query(Follow).filter(Follow.follower_id == requester_id).all()
    }

    anchors_raw = await _fetch_nearby_anchors(lat, lng, radius_km)

    # Annotate with reaction counts
    content_ids = [a["id"] for a in anchors_raw if "id" in a]
    reaction_counts: dict = {}
    if content_ids:
        rows = (
            db.query(Reaction.content_id, func.count(Reaction.id).label("cnt"))
            .filter(
                Reaction.content_type == "anchor",
                Reaction.content_id.in_(
                    [uuid.UUID(cid) for cid in content_ids]
                ),
            )
            .group_by(Reaction.content_id)
            .all()
        )
        reaction_counts = {str(r.content_id): r.cnt for r in rows}

    feed_items = []
    for anchor in anchors_raw:
        aid = anchor.get("id", "")
        feed_items.append(
            AnchorFeedItem(
                id=uuid.UUID(aid) if aid else uuid.uuid4(),
                user_id=uuid.UUID(anchor.get("user_id", str(uuid.uuid4()))),
                title=anchor.get("title", ""),
                content=anchor.get("content", ""),
                content_type=anchor.get("content_type", "text"),
                latitude=anchor.get("latitude", 0.0),
                longitude=anchor.get("longitude", 0.0),
                created_at=anchor.get("created_at"),
                is_followed=str(anchor.get("user_id", "")) in following_ids,
                reaction_count=reaction_counts.get(aid, 0),
            )
        )

    # Sort: followed-user anchors first, then by recency
    feed_items.sort(
        key=lambda a: (not a.is_followed, -(a.created_at.timestamp() if a.created_at else 0)),
    )
    return feed_items


@router.get(
    "/feed/trending",
    response_model=TrendingFeedResponse,
    summary="Trending feed",
    description=(
        "Return the top anchors and mind maps ranked by reaction count "
        "over the last 7 days. Public endpoint — no authentication required."
    ),
)
def get_trending_feed(
    limit: int = Query(20, ge=1, le=100, description="Maximum items to return"),
    db: Session = Depends(get_db),
):
    """Return top-reacted anchors and mind maps in the last 7 days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    rows = (
        db.query(
            Reaction.content_type,
            Reaction.content_id,
            func.count(Reaction.id).label("cnt"),
        )
        .filter(Reaction.created_at >= cutoff)
        .group_by(Reaction.content_type, Reaction.content_id)
        .order_by(desc("cnt"))
        .limit(limit)
        .all()
    )

    items = [
        TrendingItem(
            content_type=r.content_type,
            content_id=r.content_id,
            reaction_count=r.cnt,
        )
        for r in rows
    ]
    return TrendingFeedResponse(items=items, window_days=7)


# ---------------------------------------------------------------------------
# Reactions
# ---------------------------------------------------------------------------


@router.post(
    "/react",
    response_model=ReactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="React to content",
    description=(
        "Add an emoji reaction to an anchor or mind map. "
        "Allowed emojis: 👍 ❤️ 🔥 💡. "
        "Each user may have at most one reaction per content item "
        "(unique per user + content_type + content_id). "
        "Requires JWT authentication."
    ),
)
async def create_reaction(
    reaction_data: ReactionCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """React to an anchor or mind map. One reaction per user per content item."""
    user_id = UUID(current_user["id"])

    if reaction_data.emoji not in VALID_EMOJIS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid emoji. Allowed: {sorted(VALID_EMOJIS)}",
        )

    existing = (
        db.query(Reaction)
        .filter(
            Reaction.user_id == user_id,
            Reaction.content_type == reaction_data.content_type,
            Reaction.content_id == reaction_data.content_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already reacted to this content.",
        )

    reaction = Reaction(
        user_id=user_id,
        content_type=reaction_data.content_type,
        content_id=reaction_data.content_id,
        emoji=reaction_data.emoji,
    )
    db.add(reaction)
    db.commit()
    db.refresh(reaction)
    return reaction


@router.delete(
    "/react/{reaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a reaction",
    description=(
        "Remove a reaction by its ID. "
        "Only the user who created the reaction may delete it. "
        "Requires JWT authentication."
    ),
)
async def delete_reaction(
    reaction_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a reaction. Only the owning user may delete it."""
    user_id = UUID(current_user["id"])

    reaction = db.query(Reaction).filter(Reaction.id == reaction_id).first()
    if not reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reaction not found."
        )
    if reaction.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this reaction.",
        )

    db.delete(reaction)
    db.commit()
    return None


@router.get(
    "/reactions/{content_type}/{content_id}",
    response_model=ReactionListResponse,
    summary="Get reactions for content",
    description=(
        "Return all reactions for a given piece of content identified by "
        "*content_type* (anchor or mindmap) and *content_id* (UUID). "
        "Public endpoint — no authentication required."
    ),
)
def get_reactions(
    content_type: str,
    content_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Return paginated reactions for a content item."""
    if content_type not in ("anchor", "mindmap"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="content_type must be 'anchor' or 'mindmap'.",
        )

    query = db.query(Reaction).filter(
        Reaction.content_type == content_type,
        Reaction.content_id == content_id,
    )
    total = query.count()
    reactions = query.order_by(desc(Reaction.created_at)).offset(skip).limit(limit).all()
    return ReactionListResponse(reactions=reactions, total=total)
