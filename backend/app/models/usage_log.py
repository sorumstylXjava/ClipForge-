from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Integer, BigInteger, text
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="SET NULL"))
    clip_id = Column(UUID(as_uuid=True), ForeignKey("clips.id", ondelete="SET NULL"))
    ai_job_id = Column(UUID(as_uuid=True), ForeignKey("ai_jobs.id", ondelete="SET NULL"))

    action = Column(String, nullable=False)
    date = Column(Date, nullable=False, server_default=text("CURRENT_DATE"))

    duration_seconds = Column(Integer)
    filesize_bytes = Column(BigInteger)

    plan_at_time = Column(String)
    ip_address = Column(INET)
    user_agent = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)

    user = relationship("User", backref="usage_logs")
    video = relationship("Video", backref="usage_logs")
    clip = relationship("Clip", backref="usage_logs")
    ai_job = relationship("AIJob", backref="usage_logs")
