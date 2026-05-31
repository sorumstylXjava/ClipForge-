from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Numeric, BigInteger, Boolean, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Clip(Base):
    __tablename__ = "clips"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    ai_job_id = Column(UUID(as_uuid=True), ForeignKey("ai_jobs.id", ondelete="SET NULL"))

    title = Column(String)
    clip_type = Column(String, nullable=False)

    start_time = Column(Numeric(10, 3), nullable=False)
    end_time = Column(Numeric(10, 3), nullable=False)
    # duration is GENERATED ALWAYS in postgres, we can use server_default or just omit on insert
    # duration = Column(Numeric(10, 3), text("GENERATED ALWAYS AS (end_time - start_time) STORED"))
    # for simplicity in sqlalchemy we can skip GENERATED or define it as Computed.
    # using Computed
    from sqlalchemy import Computed
    duration = Column(Numeric(10, 3), Computed("end_time - start_time"))

    output_path = Column(String)
    thumbnail_path = Column(String)
    filesize_bytes = Column(BigInteger)
    resolution = Column(String)
    width = Column(Integer)
    height = Column(Integer)
    fps = Column(Numeric(5, 2))

    highlight_score = Column(Numeric(4, 3))
    
    is_vertical = Column(Boolean, nullable=False, server_default="false")
    has_subtitle = Column(Boolean, nullable=False, server_default="false")
    subtitle_path = Column(String)

    has_watermark = Column(Boolean, nullable=False, server_default="true")

    status = Column(String, nullable=False, server_default="processing")
    error_message = Column(String)

    metadata_ = Column("metadata", JSONB) # avoid reserved word

    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()"), nullable=False)
    deleted_at = Column(DateTime(timezone=True))

    user = relationship("User", backref="clips")
    video = relationship("Video", backref="clips")
    ai_job = relationship("AIJob", backref="clips")
