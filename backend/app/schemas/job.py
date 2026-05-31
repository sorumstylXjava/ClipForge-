import uuid

from pydantic import BaseModel, Field


class HighlightJobRequest(BaseModel):
    video_id: uuid.UUID
    max_highlights: int = Field(5, ge=1, le=20)
    auto_clip: bool = True


class SpeechSearchJobRequest(BaseModel):
    video_id: uuid.UUID
    query: str = Field(..., min_length=1, max_length=500)
    auto_clip: bool = True
    clip_padding_seconds: float = Field(5.0, ge=0, le=30)
    min_confidence: float = Field(0.7, ge=0.0, le=1.0)


class SceneDetectionJobRequest(BaseModel):
    video_id: uuid.UUID
    auto_clip: bool = False


class ObjectTrackingJobRequest(BaseModel):
    video_id: uuid.UUID
    classes: list[str] = Field(..., min_length=1)
    auto_clip: bool = True
    clip_padding_seconds: float = Field(3.0, ge=0, le=30)
    min_confidence: float = Field(0.5, ge=0.0, le=1.0)
    min_duration_seconds: float = Field(2.0, ge=0)


class FaceTrackingJobRequest(BaseModel):
    video_id: uuid.UUID
    auto_clip: bool = True
    clip_padding_seconds: float = Field(3.0, ge=0, le=30)
    front_facing_only: bool = False


class GestureTrackingJobRequest(BaseModel):
    video_id: uuid.UUID
    gestures: list[str] = Field(..., min_length=1)
    auto_clip: bool = True
    clip_padding_seconds: float = Field(3.0, ge=0, le=30)


class ShortsJobRequest(BaseModel):
    video_id: uuid.UUID
    source_clip_id: uuid.UUID | None = None
    aspect_ratio: str = "9:16"
    auto_subtitle: bool = True
    subtitle_font: str = "default"
    auto_center: bool = True
    auto_zoom: bool = True


class JobResponse(BaseModel):
    id: str
    job_type: str
    status: str
    priority: int
    progress: int
    video_id: str
    created_at: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, job) -> "JobResponse":
        return cls(
            id=str(job.id),
            job_type=job.job_type,
            status=job.status,
            priority=job.priority,
            progress=job.progress,
            video_id=str(job.video_id),
            created_at=job.created_at.isoformat(),
        )


class JobDetailResponse(JobResponse):
    celery_task_id: str | None
    params: dict | None
    error_message: str | None
    started_at: str | None
    finished_at: str | None
    progress_message: str | None = None

    @classmethod
    def from_orm(cls, job) -> "JobDetailResponse":
        return cls(
            id=str(job.id),
            job_type=job.job_type,
            status=job.status,
            priority=job.priority,
            progress=job.progress,
            video_id=str(job.video_id),
            created_at=job.created_at.isoformat(),
            celery_task_id=job.celery_task_id,
            params=job.params,
            error_message=job.error_message,
            started_at=job.started_at.isoformat() if job.started_at else None,
            finished_at=job.finished_at.isoformat() if job.finished_at else None,
        )


class JobResultItem(BaseModel):
    id: str
    result_type: str
    start_time: float | None
    end_time: float | None
    label: str | None
    score: float | None
    clip_id: str | None
    metadata: dict | None

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, result) -> "JobResultItem":
        return cls(
            id=str(result.id),
            result_type=result.result_type,
            start_time=result.start_time,
            end_time=result.end_time,
            label=result.label,
            score=result.score,
            clip_id=str(result.clip_id) if result.clip_id else None,
            metadata=result.metadata,
        )


class JobResultsResponse(BaseModel):
    job_id: str
    job_type: str
    status: str
    result_count: int
    results: list[JobResultItem]


class JobListResponse(BaseModel):
    jobs: list[JobDetailResponse]
    total: int
    limit: int
    offset: int
