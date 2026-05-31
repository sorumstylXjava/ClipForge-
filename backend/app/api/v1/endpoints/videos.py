from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app import crud, models, schemas
from app.api import deps

router = APIRouter()

class VideoImportRequest(BaseModel):
    youtube_url: str
    youtube_id: str
    title: Optional[str] = ""
    thumbnail_url: Optional[str] = ""
    duration_seconds: Optional[int] = 0

@router.post("/import", response_model=schemas.Video)
def import_youtube_video(
    *,
    db: Session = Depends(deps.get_db),
    video_in: VideoImportRequest,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    existing = crud.video.get_by_youtube_id(db, user_id=current_user.id, youtube_id=video_in.youtube_id)
    if existing:
        return existing

    video_create = schemas.VideoCreate(
        youtube_url=video_in.youtube_url,
        youtube_id=video_in.youtube_id,
        title=video_in.title,
        thumbnail_url=video_in.thumbnail_url,
        duration_seconds=video_in.duration_seconds,
        user_id=current_user.id
    )
    video = crud.video.create(db, obj_in=video_create)
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
