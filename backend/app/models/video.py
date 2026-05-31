from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Numeric, BigInteger, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    youtube_url = Column(String, nullable=False)
    youtube_id = Column(String, nullable=False)
    title = Column(String)
    description = Column(String)
    channel_name = Column(String)
    channel_id = Column(String)
    thumbnail_url = Column(String)
    published_at = Column(DateTime(timezone=True))

    duration_seconds = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    fps = Column(Numeric(5, 2))
    resolution = Column(String)
    filesize_bytes = Column(BigInteger)
    codec_video = Column(String)
    codec_audio = Column(String)
    bitrate_kbps = Column(Integer)

    file_path = Column(String)
    thumbnail_path = Column(String)

    status = Column(String, nullable=False, server_default="pending")
    error_message = Column(String)

    download_started_at = Column(DateTime(timezone=True))
    download_finished_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()"), nullable=False)
    deleted_at = Column(DateTime(timezone=True))

    user = relationship("User", backref="videos")
