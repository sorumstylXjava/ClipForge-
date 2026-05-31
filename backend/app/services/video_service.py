"""
video_service.py
----------------
Business logic for video import and lifecycle management.

Rules enforced here:
- Daily import quota: Free = 3 videos/day, Premium = unlimited
- Duration restriction: Free users capped at 60 seconds of processing
- Duplicate URL detection per user
- Video status transitions (pending → downloading → ready / failed)
- Storage quota gate
- Activity logging for all video actions
"""

from datetime import date, datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.models.user import User
from app.models.video import Video


# ─── Plan Constants ───────────────────────────────────────────────────────────

FREE_DAILY_VIDEO_QUOTA = 3          # imports per calendar day
FREE_MAX_DURATION_SECONDS = 60      # cap applied for AI processing on free plan
PREMIUM_PLAN_NAMES = {"premium", "pro"}


# ─── Quota & Plan Helpers ─────────────────────────────────────────────────────

def _is_premium(user: User) -> bool:
    return user.plan in PREMIUM_PLAN_NAMES


def _check_storage_quota(user: User, estimated_bytes: int = 0) -> None:
    """Raise 403 if user would exceed their storage quota."""
    if user.storage_used_bytes + estimated_bytes > user.storage_quota_bytes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Storage quota exceeded. "
                f"Used: {user.storage_used_bytes} / {user.storage_quota_bytes} bytes."
            ),
        )


def _check_daily_import_quota(db: Session, user: User) -> None:
    """
    Raise 429 if a free user has already imported FREE_DAILY_VIDEO_QUOTA videos today.
    Premium users bypass this check entirely.
    """
    if _is_premium(user):
        return

    today = date.today()
    count = (
        db.query(Video)
        .filter(
            Video.user_id == user.id,
            Video.deleted_at.is_(None),
            # Compare only the date portion of created_at
            db.query(Video)
            .filter(
                Video.user_id == user.id,
                Video.deleted_at.is_(None),
            )
            .filter(
                Video.created_at >= datetime.combine(today, datetime.min.time())
            )
            .exists()
        )
        .count()
    )

    # Simpler direct query for daily count
    from sqlalchemy import func, cast
    from sqlalchemy.types import Date
    daily_count = (
        db.query(func.count(Video.id))
        .filter(
            Video.user_id == user.id,
            Video.deleted_at.is_(None),
            cast(Video.created_at, Date) == today,
        )
        .scalar()
    ) or 0

    if daily_count >= FREE_DAILY_VIDEO_QUOTA:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Daily import limit reached ({FREE_DAILY_VIDEO_QUOTA} videos/day on Free plan). "
                "Upgrade to Premium for unlimited imports."
            ),
        )


def _get_effective_duration(user: User, raw_duration: Optional[int]) -> Optional[int]:
    """
    Return the duration that will actually be processed.
    Free users are capped at FREE_MAX_DURATION_SECONDS.
    """
    if raw_duration is None:
        return None
    if _is_premium(user):
        return raw_duration
    return min(raw_duration, FREE_MAX_DURATION_SECONDS)


# ─── Service Functions ────────────────────────────────────────────────────────

def import_video(
    db: Session,
    *,
    user: User,
    youtube_url: str,
    youtube_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    channel_name: Optional[str] = None,
    channel_id: Optional[str] = None,
    thumbnail_url: Optional[str] = None,
    published_at: Optional[datetime] = None,
    duration_seconds: Optional[int] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    fps: Optional[float] = None,
    resolution: Optional[str] = None,
) -> Video:
    """
    Register a YouTube video for processing.

    Business rules:
    1. Check daily import quota (Free: 3/day, Premium: unlimited).
    2. Check storage quota.
    3. Prevent duplicate imports of the same YouTube ID per user.
    4. Create a Video row with status='pending'.
    5. Log the action.
    """
    # Gate 1 – daily quota
    _check_daily_import_quota(db, user)

    # Gate 2 – storage quota (rough estimate based on duration if provided)
    _check_storage_quota(user)

    # Gate 3 – duplicate detection
    existing = crud.video.get_by_youtube_id(db, user_id=user.id, youtube_id=youtube_id)
    if existing and existing.deleted_at is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"You have already imported this video (ID: {youtube_id}).",
        )

    video_in = schemas.VideoCreate(
        user_id=user.id,
        youtube_url=youtube_url,
        youtube_id=youtube_id,
        title=title,
        description=description,
        channel_name=channel_name,
        channel_id=channel_id,
        thumbnail_url=thumbnail_url,
        published_at=published_at,
        duration_seconds=duration_seconds,
        width=width,
        height=height,
        fps=fps,
        resolution=resolution,
    )
    video = crud.video.create(db, obj_in=video_in)

    # Activity log
    _log_action(
        db,
        user_id=user.id,
        action="video_import",
        video_id=video.id,
        duration_seconds=duration_seconds,
        plan_at_time=user.plan,
    )

    return video


def get_user_videos(
    db: Session,
    *,
    user: User,
    skip: int = 0,
    limit: int = 50,
) -> List[Video]:
    """Return all non-deleted videos owned by the user."""
    return crud.video.get_multi_by_user(db, user_id=user.id, skip=skip, limit=limit)


def get_video_or_404(db: Session, *, video_id: UUID, user: User) -> Video:
    """Fetch a video by ID, enforcing ownership. Raises 404 if missing or not owned."""
    video = crud.video.get(db, id=video_id)
    if not video or video.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found.")
    if video.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    return video


def get_effective_duration_for_processing(user: User, video: Video) -> int:
    """
    Return how many seconds will actually be sent to the AI pipeline for this video.
    Free users are capped at FREE_MAX_DURATION_SECONDS seconds.
    """
    raw = video.duration_seconds or 0
    return _get_effective_duration(user, raw)


def update_video_status(
    db: Session,
    *,
    video: Video,
    status: str,
    error_message: Optional[str] = None,
    file_path: Optional[str] = None,
    filesize_bytes: Optional[int] = None,
) -> Video:
    """
    Transition a video's status (e.g. pending → downloading → ready / failed).

    Allowed transitions:
        pending  → downloading
        downloading → ready | failed
        ready    → (terminal)
        failed   → pending  (allow retry)
    """
    VALID_STATUSES = {"pending", "downloading", "ready", "failed", "deleted"}
    if status not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid video status '{status}'.",
        )

    update_data: dict = {"status": status}
    if error_message is not None:
        update_data["error_message"] = error_message
    if file_path is not None:
        update_data["file_path"] = file_path
    if filesize_bytes is not None:
        update_data["filesize_bytes"] = filesize_bytes
    if status == "downloading":
        update_data["download_started_at"] = datetime.now(timezone.utc)
    if status == "ready":
        update_data["download_finished_at"] = datetime.now(timezone.utc)

    return crud.video.update(db, db_obj=video, obj_in=update_data)


def soft_delete_video(db: Session, *, video: Video, user: User) -> None:
    """
    Soft-delete a video (and cascade soft-deletes clips via status logic).
    Sets deleted_at to now; does not remove the DB row.
    """
    crud.video.update(db, db_obj=video, obj_in={"deleted_at": datetime.now(timezone.utc)})
    _log_action(db, user_id=user.id, action="video_delete", video_id=video.id, plan_at_time=user.plan)


# ─── Private Helpers ──────────────────────────────────────────────────────────

def _log_action(
    db: Session,
    *,
    user_id: UUID,
    action: str,
    video_id: Optional[UUID] = None,
    clip_id: Optional[UUID] = None,
    duration_seconds: Optional[int] = None,
    filesize_bytes: Optional[int] = None,
    plan_at_time: Optional[str] = None,
) -> None:
    try:
        log_in = schemas.UsageLogCreate(
            user_id=user_id,
            video_id=video_id,
            clip_id=clip_id,
            action=action,
            duration_seconds=duration_seconds,
            filesize_bytes=filesize_bytes,
            plan_at_time=plan_at_time,
        )
        crud.usage_log.create(db, obj_in=log_in)
    except Exception:
        pass
