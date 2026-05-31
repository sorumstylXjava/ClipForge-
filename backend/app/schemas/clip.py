from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class ClipBase(BaseModel):
    title: Optional[str] = None
    clip_type: str
    start_time: float
    end_time: float
    output_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    filesize_bytes: Optional[int] = None
    resolution: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    highlight_score: Optional[float] = None
    is_vertical: Optional[bool] = False
    has_subtitle: Optional[bool] = False
    subtitle_path: Optional[str] = None
    has_watermark: Optional[bool] = True
    metadata_: Optional[dict] = None

class ClipCreate(ClipBase):
    user_id: UUID
    video_id: UUID
    ai_job_id: Optional[UUID] = None

class ClipUpdate(BaseModel):
    status: Optional[str] = None
    output_path: Optional[str] = None
    filesize_bytes: Optional[int] = None
    error_message: Optional[str] = None
    thumbnail_path: Optional[str] = None

class ClipInDBBase(ClipBase):
    id: UUID
    user_id: UUID
    video_id: UUID
    ai_job_id: Optional[UUID] = None
    duration: float
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Clip(ClipInDBBase):
    pass
