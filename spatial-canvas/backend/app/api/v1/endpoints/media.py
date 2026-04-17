"""Media upload endpoints for anchors."""

import os
import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user_id
from app.core.config import settings
from schemas.anchor import AnchorResponse
from services.anchor import AnchorService

router = APIRouter()
logger = logging.getLogger(__name__)

# File size limits in bytes
FILE_SIZE_LIMITS = {
    "image": 10 * 1024 * 1024,   # 10 MB
    "video": 100 * 1024 * 1024,  # 100 MB
    "audio": 25 * 1024 * 1024,   # 25 MB
}

# Allowed MIME type prefixes per content_type
ALLOWED_MIME_PREFIXES = {
    "image": "image/",
    "video": "video/",
    "audio": "audio/",
}


@router.post(
    "/{anchor_id}/media",
    response_model=AnchorResponse,
    summary="Upload media for an anchor",
    description=(
        "Upload a media file for an anchor. The file content type must match "
        "the anchor's declared content_type (image, video, or audio)."
    ),
)
async def upload_anchor_media(
    anchor_id: UUID,
    file: UploadFile = File(...),
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Upload media file for an anchor."""
    # Get the anchor
    anchor = AnchorService.get_anchor_by_id(db, anchor_id)
    if not anchor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Anchor with ID {anchor_id} not found",
        )

    # Check ownership
    if anchor.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to upload media for this anchor",
        )

    # Validate content type — only image/video/audio anchors accept media
    if anchor.content_type == "text":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text anchors do not support media uploads",
        )

    # Validate MIME type matches anchor content_type
    expected_prefix = ALLOWED_MIME_PREFIXES.get(anchor.content_type)
    if expected_prefix and file.content_type and not file.content_type.startswith(expected_prefix):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"File type '{file.content_type}' does not match anchor "
                f"content_type '{anchor.content_type}'"
            ),
        )

    # Read file content and check size
    content = await file.read()
    max_size = FILE_SIZE_LIMITS.get(anchor.content_type, 10 * 1024 * 1024)
    if len(content) > max_size:
        max_mb = max_size / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"File size ({len(content) / (1024 * 1024):.1f} MB) exceeds "
                f"the {max_mb:.0f} MB limit for {anchor.content_type} files"
            ),
        )

    # Store file to disk
    # TODO: Replace local disk storage with S3/GCS upload for production
    media_dir = os.path.join(settings.MEDIA_STORAGE_PATH, str(anchor_id))
    os.makedirs(media_dir, exist_ok=True)

    filename = file.filename or f"upload.{anchor.content_type}"
    file_path = os.path.join(media_dir, filename)

    with open(file_path, "wb") as f:
        f.write(content)

    # Update anchor with media URL
    media_url = f"/media/{anchor_id}/{filename}"
    anchor.media_url = media_url
    db.commit()
    db.refresh(anchor)

    logger.info(f"Uploaded media for anchor {anchor_id}: {media_url}")

    return AnchorResponse(
        id=anchor.id,
        user_id=anchor.user_id,
        title=anchor.title,
        content=anchor.content,
        content_type=anchor.content_type,
        media_url=anchor.media_url,
        latitude=anchor.latitude,
        longitude=anchor.longitude,
        created_at=anchor.created_at,
        updated_at=anchor.updated_at,
    )


@router.get(
    "/{anchor_id}/media",
    summary="Get anchor media info",
    description="Get the media URL and content type for an anchor.",
)
def get_anchor_media(
    anchor_id: UUID,
    db: Session = Depends(get_db),
):
    """Get media URL + content_type for an anchor."""
    anchor = AnchorService.get_anchor_by_id(db, anchor_id)
    if not anchor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Anchor with ID {anchor_id} not found",
        )

    return {
        "anchor_id": str(anchor.id),
        "media_url": anchor.media_url,
        "content_type": anchor.content_type,
    }
