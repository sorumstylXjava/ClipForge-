from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app import crud, models, schemas
from app.api import deps
import yt_dlp

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
    """Import a YouTube video."""
    existing = crud.video.get_by_youtube_id(
        db, user_id=current_user.id, youtube_id=video_in.youtube_id
    )
    if existing:
        return existing

    # Fetch info dari YouTube pakai yt-dlp
    try:
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_in.youtube_url, download=False)

        title = info.get("title", "") or video_in.title or ""
        thumbnail_url = info.get("thumbnail", "") or video_in.thumbnail_url or ""
        duration_seconds = info.get("duration", 0) or video_in.duration_seconds or 0
        channel_name = info.get("uploader", "") or info.get("channel", "") or ""
        channel_id = info.get("channel_id", "") or ""
        description = info.get("description", "") or ""
        width = info.get("width") or None
        height = info.get("height") or None
        fps = info.get("fps") or None
        youtube_id = info.get("id", video_in.youtube_id)
    except Exception as e:
        # Fallback ke data dari request
        title = video_in.title or ""
        thumbnail_url = video_in.thumbnail_url or ""
        duration_seconds = video_in.duration_seconds or 0
        channel_name = ""
        channel_id = ""
        description = ""
        width = None
        height = None
        fps = None
        youtube_id = video_in.youtube_id

    video_create = schemas.VideoCreate(
        youtube_url=video_in.youtube_url,
        youtube_id=youtube_id,
        title=title,
        thumbnail_url=thumbnail_url,
        duration_seconds=duration_seconds,
        channel_name=channel_name,
        channel_id=channel_id,
        description=description,
        width=width,
        height=height,
        fps=fps,
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
    """Retrieve videos."""
    videos = crud.video.get_multi_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return videos

@router.delete("/{id}", response_model=schemas.Video)
def delete_video(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Delete a video."""
    video = crud.video.get(db=db, id=id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    video = crud.video.remove(db=db, id=id)
    return video
