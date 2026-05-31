from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, SmallInteger, Numeric, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class AIJob(Base):
    __tablename__ = "ai_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)

    celery_task_id = Column(String)
    celery_queue = Column(String)

    job_type = Column(String, nullable=False)
    status = Column(String, nullable=False, server_default="queued")
    priority = Column(Integer, nullable=False, server_default="5")

    params = Column(JSONB)
    progress = Column(SmallInteger, nullable=False, server_default="0")
    progress_message = Column(String)

    result_count = Column(Integer)
    error_message = Column(String)
    error_code = Column(String)

    processing_mode = Column(String, nullable=False, server_default="server")

    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    queued_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))

    gpu_seconds_used = Column(Numeric(10, 2), server_default="0")
    model_used = Column(String)

    user = relationship("User", backref="ai_jobs")
    video = relationship("Video", backref="ai_jobs")
