from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class AIJobBase(BaseModel):
    job_type: str
    params: Optional[dict] = None
    processing_mode: Optional[str] = "server"
    priority: Optional[int] = 5

class AIJobCreate(AIJobBase):
    user_id: UUID
    video_id: UUID

class AIJobUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[int] = None
    progress_message: Optional[str] = None
    result_count: Optional[int] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    gpu_seconds_used: Optional[float] = None
    model_used: Optional[str] = None
    celery_task_id: Optional[str] = None

class AIJobInDBBase(AIJobBase):
    id: UUID
    user_id: UUID
    video_id: UUID
    celery_task_id: Optional[str] = None
    celery_queue: Optional[str] = None
    status: str
    progress: int
    progress_message: Optional[str] = None
    result_count: Optional[int] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    created_at: datetime
    queued_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    gpu_seconds_used: float
    model_used: Optional[str] = None

    class Config:
        from_attributes = True

class AIJob(AIJobInDBBase):
    pass
