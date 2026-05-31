from typing import Optional
from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel

class UsageLogBase(BaseModel):
    action: str
    duration_seconds: Optional[int] = None
    filesize_bytes: Optional[int] = None
    plan_at_time: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class UsageLogCreate(UsageLogBase):
    user_id: UUID
    video_id: Optional[UUID] = None
    clip_id: Optional[UUID] = None
    ai_job_id: Optional[UUID] = None

class UsageLogInDBBase(UsageLogBase):
    id: UUID
    user_id: UUID
    video_id: Optional[UUID] = None
    clip_id: Optional[UUID] = None
    ai_job_id: Optional[UUID] = None
    date: date
    created_at: datetime

    class Config:
        from_attributes = True

class UsageLog(UsageLogInDBBase):
    pass
