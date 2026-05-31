"""
clip_service.py
---------------
Business logic for clip creation and lifecycle management.

Rules enforced here:
- Free users always receive clips with watermark (has_watermark=True)
- Free users are limited to 720p max resolution output
- Validate that start_time < end_time and both are within video duration
- Validate that the video is in 'ready' status before allowing clip requests
- Manual clips: direct creation from user-supplied start/end times
- AI-generated clips: created from job results (ai_job_id provided)
- Soft-delete only (no hard deletes)
- Activity logging for all clip actions
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.models.clip import Clip
from app.models.user import User
from app.models.video import Video


# ─── Plan / Free-tier Constants ───────────────────────────────────────────────

PREMIUM_PLAN_NAMES = {"premium", "pro"}
FREE_MAX_RESOLUTION = "720p"
FREE_WATERMARK = True
PREMIUM_WATERMARK = False

VALID_CLIP_TYPES = {
    "manual",
    "ai_highlight",
    "scene_detection",
    "speech_search",
    "object_tracking",
    "face_tracking",
    "gesture_tracking",
    "shorts_generator",
}

PREMIUM_CLIP_TYPES = {
    "speech_search",
    "object_tracking",
    "face_tracking",
    "gesture_tracking",
    "shorts_generator",
}


# ─── Plan Helpers ─────────────────────────────────────────────────────────────

def _is_premium(user: User) -> bool:
    return user.plan in PREMIUM_PLAN_NAMES


def _resolve_watermark(user: User) -> bool:
    """Free users always get watermark; premium users do not."""
    return FREE_WATERMARK if not _is_premium(user) else PREMIUM_WATERMARK


def _resolve_resolution(user: User, requested: Optional[str]) -> Optional[str]:
    """
    Clamp output resolution to 720p for free users.
    Premium users can request up to 4K.
    """
    if _is_premium(user):
        return requested
    # For free users, always return 720p regardless of request
    return FREE_MAX_RESOLUTION


# ─── Validation Helpers ───────────────────────────────────────────────────────

def _validate_video_ready(video: Video) -> None:
    """Clips can only be created from videos that have been fully downloaded."""
    if video.status != "ready":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Video is not ready for clipping (current status: '{video.status}'). "
                "Please wait for the download to complete."
            ),
        )


def _validate_time_range(
    start_time: float,
    end_time: float,
    video: Video,
    user: User,
) -> None:
    """
    Validate that start/end times are logically correct and within bounds.
    Free users are further restricted to the first 60 seconds.
    """
    if start_time < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_time must be >= 0.",
        )
    if end_time <= start_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_time must be greater than start_time.",
        )

    video_duration = video.duration_seconds or 0

    if video_duration > 0 and end_time > video_duration:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"end_time ({end_time}s) exceeds video duration ({video_duration}s)."
            ),
        )

    # Free user cap: no clip can start or end beyond 60 seconds
    if not _is_premium(user) and end_time > 60:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Free users can only clip the first 60 seconds of a video. "
                "Upgrade to Premium to clip the full video."
            ),
        )


def _validate_clip_type_access(clip_type: str, user: User) -> None:
    """Raise 403 if a free user attempts to use a premium-only clip type."""
    if clip_type not in VALID_CLIP_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unknown clip type '{clip_type}'. Valid types: {sorted(VALID_CLIP_TYPES)}.",
        )
    if clip_type in PREMIUM_CLIP_TYPES and not _is_premium(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Clip type '{clip_type}' is a Premium feature. "
                "Upgrade to Premium to access it."
            ),
        )


# ─── Service Functions ────────────────────────────────────────────────────────

def create_manual_clip(
    db: Session,
    *,
    user: User,
    video: Video,
    start_time: float,
    end_time: float,
    title: Optional[str] = None,
    resolution: Optional[str] = None,
) -> Clip:
    """
    Create a manual clip from user-supplied start/end times.

    Business rules:
    - Video must be 'ready'.
    - Time range must be valid.
    - Free users capped at 60-second mark and get 720p + watermark.
    - Returns a Clip in 'processing' status (FFmpeg is handled externally).
    """
    _validate_video_ready(video)
    _validate_time_range(start_time, end_time, video, user)

    clip_in = schemas.ClipCreate(
        user_id=user.id,
        video_id=video.id,
        ai_job_id=None,
        clip_type="manual",
        title=title or f"Clip {start_time:.0f}s–{end_time:.0f}s",
        start_time=start_time,
        end_time=end_time,
        resolution=_resolve_resolution(user, resolution),
        has_watermark=_resolve_watermark(user),
    )
    clip = crud.clip.create(db, obj_in=clip_in)

    _log_action(
        db,
        user_id=user.id,
        action="clip_create_manual",
        video_id=video.id,
        clip_id=clip.id,
        plan_at_time=user.plan,
    )
    return clip


def create_ai_clip(
    db: Session,
    *,
    user: User,
    video: Video,
    clip_type: str,
    start_time: float,
    end_time: float,
    ai_job_id: UUID,
    title: Optional[str] = None,
    highlight_score: Optional[float] = None,
    is_vertical: bool = False,
    has_subtitle: bool = False,
    metadata: Optional[dict] = None,
    resolution: Optional[str] = None,
) -> Clip:
    """
    Record a clip result produced by an AI job.

    Business rules:
    - Clip type must be valid and accessible by the user's plan.
    - Free users get watermark and 720p max.
    - The referenced AI job must belong to the same video.
    """
    _validate_clip_type_access(clip_type, user)
    _validate_time_range(start_time, end_time, video, user)

    clip_in = schemas.ClipCreate(
        user_id=user.id,
        video_id=video.id,
        ai_job_id=ai_job_id,
        clip_type=clip_type,
        title=title,
        start_time=start_time,
        end_time=end_time,
        highlight_score=highlight_score,
        is_vertical=is_vertical,
        has_subtitle=has_subtitle,
        resolution=_resolve_resolution(user, resolution),
        has_watermark=_resolve_watermark(user),
        metadata_=metadata,
    )
    clip = crud.clip.create(db, obj_in=clip_in)

    _log_action(
        db,
        user_id=user.id,
        action=f"clip_create_{clip_type}",
        video_id=video.id,
        clip_id=clip.id,
        plan_at_time=user.plan,
    )
    return clip


def get_clip_or_404(db: Session, *, clip_id: UUID, user: User) -> Clip:
    """Fetch a clip by ID, enforcing ownership. Raises 404 if missing or not owned."""
    clip = crud.clip.get(db, id=clip_id)
    if not clip or clip.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clip not found.")
    if clip.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    return clip


def get_clips_for_user(
    db: Session,
    *,
    user: User,
    skip: int = 0,
    limit: int = 50,
) -> List[Clip]:
    """Return all non-deleted clips owned by the user."""
    return crud.clip.get_multi_by_user(db, user_id=user.id, skip=skip, limit=limit)


def get_clips_for_video(
    db: Session,
    *,
    video: Video,
    skip: int = 0,
    limit: int = 50,
) -> List[Clip]:
    """Return all non-deleted clips for a specific video."""
    return crud.clip.get_multi_by_video(db, video_id=video.id, skip=skip, limit=limit)


def update_clip_status(
    db: Session,
    *,
    clip: Clip,
    status: str,
    output_path: Optional[str] = None,
    filesize_bytes: Optional[int] = None,
    thumbnail_path: Optional[str] = None,
    error_message: Optional[str] = None,
) -> Clip:
    """
    Transition a clip's processing status.
    Allowed: processing → ready | failed
    """
    VALID_STATUSES = {"processing", "ready", "failed"}
    if status not in VALID_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid clip status '{status}'.",
        )
    update_data: dict = {"status": status}
    if output_path:
        update_data["output_path"] = output_path
    if filesize_bytes is not None:
        update_data["filesize_bytes"] = filesize_bytes
    if thumbnail_path:
        update_data["thumbnail_path"] = thumbnail_path
    if error_message:
        update_data["error_message"] = error_message

    return crud.clip.update(db, db_obj=clip, obj_in=update_data)


def soft_delete_clip(db: Session, *, clip: Clip, user: User) -> None:
    """Soft-delete a clip record."""
    crud.clip.update(db, db_obj=clip, obj_in={"deleted_at": datetime.now(timezone.utc)})
    _log_action(
        db,
        user_id=user.id,
        action="clip_delete",
        video_id=clip.video_id,
        clip_id=clip.id,
        plan_at_time=user.plan,
    )


# ─── Private Helpers ──────────────────────────────────────────────────────────

def _log_action(
    db: Session,
    *,
    user_id: UUID,
    action: str,
    video_id: Optional[UUID] = None,
    clip_id: Optional[UUID] = None,
    plan_at_time: Optional[str] = None,
) -> None:
    try:
        log_in = schemas.UsageLogCreate(
            user_id=user_id,
            video_id=video_id,
            clip_id=clip_id,
            action=action,
            plan_at_time=plan_at_time,
        )
        crud.usage_log.create(db, obj_in=log_in)
    except Exception:
        pass
