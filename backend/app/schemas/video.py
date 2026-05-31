from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class VideoBase(BaseModel):
    youtube_url: str
    youtube_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    channel_name: Optional[str] = None
    channel_id: Optional[str] = None
    thumbnail_url: Optional[str] = None
    published_at: Optional[datetime] = None

    duration_seconds: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    resolution: Optional[str] = None
    filesize_bytes: Optional[int] = None
    codec_video: Optional[str] = None
    codec_audio: Optional[str] = None
    bitrate_kbps: Optional[int] = None

    file_path: Optional[str] = None
    thumbnail_path: Optional[str] = None

class VideoCreate(VideoBase):
    user_id: UUID

class VideoUpdate(BaseModel):
    status: Optional[str] = None
    error_message: Optional[str] = None
    download_started_at: Optional[datetime] = None
    download_finished_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    file_path: Optional[str] = None
    filesize_bytes: Optional[int] = None

class VideoInDBBase(VideoBase):
    id: UUID
    user_id: UUID
    status: str
    error_message: Optional[str] = None
    download_started_at: Optional[datetime] = None
    download_finished_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Video(VideoInDBBase):
    pass
