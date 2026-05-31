"""
ai_job_service.py
-----------------
Business logic for AI job lifecycle management.

Rules enforced here:
- Premium-only job type gating (speech_search, object_tracking, face_tracking,
  gesture_tracking, shorts_generator)
- Free users: shared low-priority queue (priority=5)
- Premium users: high-priority queue (priority=1)
- Free users limited to first 60s of video duration for AI processing
- Job status transitions: queued → processing → completed | failed | cancelled
- Prevent duplicate active jobs for the same video + job_type
- Activity logging for all job actions
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.models.ai_job import AIJob
from app.models.user import User
from app.models.video import Video


# ─── Plan Constants ───────────────────────────────────────────────────────────

PREMIUM_PLAN_NAMES = {"premium", "pro"}

FREE_PRIORITY = 5        # Lower priority = longer queue wait
PREMIUM_PRIORITY = 1     # Higher priority = processed first

FREE_MAX_DURATION_SECONDS = 60

# Job types accessible to all users
FREE_JOB_TYPES = {
    "ai_highlight",
    "scene_detection",
    "manual",  # not technically an AI job but consistent
}

# Job types that require Premium
PREMIUM_JOB_TYPES = {
    "speech_search",
    "object_tracking",
    "face_tracking",
    "gesture_tracking",
    "shorts_generator",
}

ALL_JOB_TYPES = FREE_JOB_TYPES | PREMIUM_JOB_TYPES

# Statuses from which a job cannot transition further
TERMINAL_STATUSES = {"completed", "failed", "cancelled"}


# ─── Plan Helpers ─────────────────────────────────────────────────────────────

def _is_premium(user: User) -> bool:
    return user.plan in PREMIUM_PLAN_NAMES


def _resolve_queue(user: User) -> str:
    """Return the Celery queue name based on user plan."""
    return "priority" if _is_premium(user) else "default"


def _resolve_priority(user: User) -> int:
    return PREMIUM_PRIORITY if _is_premium(user) else FREE_PRIORITY


def _validate_job_type_access(job_type: str, user: User) -> None:
    """Raise 400/403 for unknown or plan-restricted job types."""
    if job_type not in ALL_JOB_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Unknown job type '{job_type}'. "
                f"Valid types: {sorted(ALL_JOB_TYPES)}."
            ),
        )
    if job_type in PREMIUM_JOB_TYPES and not _is_premium(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"'{job_type}' is a Premium feature. "
                "Upgrade to unlock all AI capabilities."
            ),
        )


def _validate_video_ready(video: Video) -> None:
    """AI jobs can only be queued for videos that have finished downloading."""
    if video.status != "ready":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Video is not ready (status: '{video.status}'). "
                "Please wait for the download to complete before starting an AI job."
            ),
        )


def _check_duplicate_active_job(db: Session, video: Video, job_type: str) -> None:
    """
    Prevent submitting the same job type on the same video while a
    previous instance is still running.
    """
    active = (
        db.query(AIJob)
        .filter(
            AIJob.video_id == video.id,
            AIJob.job_type == job_type,
            AIJob.status.notin_(TERMINAL_STATUSES),
        )
        .first()
    )
    if active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"A '{job_type}' job for this video is already "
                f"in progress (status: '{active.status}', id: {active.id}). "
                "Please wait for it to finish or cancel it first."
            ),
        )


def _get_processing_duration(user: User, video: Video) -> Optional[int]:
    """
    Return how many seconds of the video will be processed.
    Free users are capped at FREE_MAX_DURATION_SECONDS.
    """
    raw = video.duration_seconds
    if raw is None:
        return None
    if _is_premium(user):
        return raw
    return min(raw, FREE_MAX_DURATION_SECONDS)


# ─── Service Functions ────────────────────────────────────────────────────────

def submit_job(
    db: Session,
    *,
    user: User,
    video: Video,
    job_type: str,
    params: Optional[dict] = None,
    processing_mode: str = "server",
) -> AIJob:
    """
    Validate and register a new AI job in the database.

    Business rules:
    1. Job type must be valid and user must have access (plan gate).
    2. Video must be in 'ready' status.
    3. No duplicate active job of the same type on the same video.
    4. Priority and queue are set based on user plan.
    5. Effective duration is injected into params so workers respect the cap.
    6. Activity is logged.
    """
    _validate_job_type_access(job_type, user)
    _validate_video_ready(video)
    _check_duplicate_active_job(db, video, job_type)

    # Inject effective duration into params for the worker to respect
    effective_duration = _get_processing_duration(user, video)
    enriched_params = dict(params or {})
    if effective_duration is not None:
        enriched_params["effective_duration_seconds"] = effective_duration

    job_in = schemas.AIJobCreate(
        user_id=user.id,
        video_id=video.id,
        job_type=job_type,
        params=enriched_params if enriched_params else None,
        processing_mode=processing_mode,
        priority=_resolve_priority(user),
    )
    job = crud.ai_job.create(db, obj_in=job_in)

    # Stamp the queue name directly after creation
    crud.ai_job.update(db, db_obj=job, obj_in={"celery_queue": _resolve_queue(user)})

    _log_action(
        db,
        user_id=user.id,
        action=f"ai_job_submit_{job_type}",
        video_id=video.id,
        ai_job_id=job.id,
        plan_at_time=user.plan,
    )

    return job


def get_job_or_404(db: Session, *, job_id: UUID, user: User) -> AIJob:
    """Fetch a job by ID, enforcing ownership."""
    job = crud.ai_job.get(db, id=job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI Job not found.")
    if job.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    return job


def get_jobs_for_user(
    db: Session,
    *,
    user: User,
    skip: int = 0,
    limit: int = 50,
) -> List[AIJob]:
    """Return all AI jobs submitted by the user."""
    return crud.ai_job.get_multi_by_user(db, user_id=user.id, skip=skip, limit=limit)


def get_jobs_for_video(
    db: Session,
    *,
    video: Video,
    skip: int = 0,
    limit: int = 50,
) -> List[AIJob]:
    """Return all AI jobs for a specific video."""
    return crud.ai_job.get_multi_by_video(db, video_id=video.id, skip=skip, limit=limit)


def update_job_progress(
    db: Session,
    *,
    job: AIJob,
    progress: int,
    progress_message: Optional[str] = None,
) -> AIJob:
    """
    Update job progress percentage (0–100) and optional human-readable message.
    Called by the worker during processing; not exposed directly via API.
    """
    if not (0 <= progress <= 100):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="progress must be between 0 and 100.",
        )
    update_data: dict = {"progress": progress}
    if progress_message:
        update_data["progress_message"] = progress_message
    if progress > 0 and job.status == "queued":
        update_data["status"] = "processing"
        update_data["started_at"] = datetime.now(timezone.utc)

    return crud.ai_job.update(db, db_obj=job, obj_in=update_data)


def complete_job(
    db: Session,
    *,
    job: AIJob,
    result_count: int,
    gpu_seconds_used: float = 0.0,
    model_used: Optional[str] = None,
) -> AIJob:
    """
    Mark a job as completed after the worker finishes processing.
    """
    if job.status in TERMINAL_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job is already in terminal state '{job.status}'.",
        )
    return crud.ai_job.update(db, db_obj=job, obj_in={
        "status": "completed",
        "progress": 100,
        "result_count": result_count,
        "finished_at": datetime.now(timezone.utc),
        "gpu_seconds_used": gpu_seconds_used,
        "model_used": model_used,
    })


def fail_job(
    db: Session,
    *,
    job: AIJob,
    error_message: str,
    error_code: Optional[str] = None,
) -> AIJob:
    """Mark a job as failed with an error message."""
    if job.status in TERMINAL_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job is already in terminal state '{job.status}'.",
        )
    return crud.ai_job.update(db, db_obj=job, obj_in={
        "status": "failed",
        "error_message": error_message,
        "error_code": error_code,
        "finished_at": datetime.now(timezone.utc),
    })


def cancel_job(db: Session, *, job: AIJob, user: User) -> AIJob:
    """
    Cancel a queued or in-progress job.

    Business rules:
    - Terminal jobs cannot be cancelled.
    - Returns the updated job.
    """
    if job.status in TERMINAL_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot cancel a job that is already '{job.status}'.",
        )
    updated = crud.ai_job.update(db, db_obj=job, obj_in={
        "status": "cancelled",
        "finished_at": datetime.now(timezone.utc),
    })
    _log_action(
        db,
        user_id=user.id,
        action="ai_job_cancel",
        video_id=job.video_id,
        ai_job_id=job.id,
        plan_at_time=user.plan,
    )
    return updated


def start_job(db: Session, *, job: AIJob, celery_task_id: str) -> AIJob:
    """Record the Celery task ID and mark the job as 'processing'."""
    if job.status != "queued":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job must be 'queued' before starting (current: '{job.status}').",
        )
    return crud.ai_job.update(db, db_obj=job, obj_in={
        "status": "processing",
        "celery_task_id": celery_task_id,
        "started_at": datetime.now(timezone.utc),
    })


# ─── Private Helpers ──────────────────────────────────────────────────────────

def _log_action(
    db: Session,
    *,
    user_id: UUID,
    action: str,
    video_id: Optional[UUID] = None,
    ai_job_id: Optional[UUID] = None,
    plan_at_time: Optional[str] = None,
) -> None:
    try:
        log_in = schemas.UsageLogCreate(
            user_id=user_id,
            video_id=video_id,
            ai_job_id=ai_job_id,
            action=action,
            plan_at_time=plan_at_time,
        )
        crud.usage_log.create(db, obj_in=log_in)
    except Exception:
        pass
