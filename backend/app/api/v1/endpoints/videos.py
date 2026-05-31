from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps
import uuid

router = APIRouter()

@router.post("/import", response_model=schemas.Video)
def import_youtube_video(
    *,
    db: Session = Depends(deps.get_db),
    video_in: schemas.VideoCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Import a YouTube video.
    """
    # Check quota or storage limit (placeholder for business logic)
    
    # Force user_id to current user
    video_in.user_id = current_user.id
    
    # Check if already imported
    existing = crud.video.get_by_youtube_id(db, user_id=current_user.id, youtube_id=video_in.youtube_id)
    if existing:
        return existing
        
    video = crud.video.create(db, obj_in=video_in)
    
    # Add usage log
    log = schemas.UsageLogCreate(
        action="video_import",
        user_id=current_user.id,
        video_id=video.id,
        plan_at_time=current_user.plan
    )
    crud.usage_log.create(db, obj_in=log)
    
    return video

@router.get("/", response_model=List[schemas.Video])
def read_videos(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve videos.
    """
    videos = crud.video.get_multi_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return videos

@router.delete("/{id}", response_model=schemas.Video)
def delete_video(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a video.
    """
    video = crud.video.get(db=db, id=id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    video = crud.video.remove(db=db, id=id)
    return video
