from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.post("/generate", response_model=schemas.Clip)
def generate_clip(
    *,
    db: Session = Depends(deps.get_db),
    clip_in: schemas.ClipCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate a new clip (manual or via AI job).
    """
    # Verify video ownership
    video = crud.video.get(db, id=clip_in.video_id)
    if not video or video.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Video not found")

    clip_in.user_id = current_user.id
    clip = crud.clip.create(db, obj_in=clip_in)
    
    # Add usage log
    log = schemas.UsageLogCreate(
        action="clip_export",
        user_id=current_user.id,
        video_id=video.id,
        clip_id=clip.id,
        plan_at_time=current_user.plan
    )
    crud.usage_log.create(db, obj_in=log)
    
    return clip

@router.get("/", response_model=List[schemas.Clip])
def read_clips(
    db: Session = Depends(deps.get_db),
    video_id: UUID = None,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve clips.
    """
    if video_id:
        clips = crud.clip.get_multi_by_video(db, video_id=video_id, skip=skip, limit=limit)
    else:
        clips = crud.clip.get_multi_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return clips

@router.delete("/{id}", response_model=schemas.Clip)
def delete_clip(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a clip.
    """
    clip = crud.clip.get(db=db, id=id)
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    if clip.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    clip = crud.clip.remove(db=db, id=id)
    return clip
