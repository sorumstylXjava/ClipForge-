from uuid import UUID
from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.video import Video
from app.schemas.video import VideoCreate, VideoUpdate

class CRUDVideo(CRUDBase[Video, VideoCreate, VideoUpdate]):
    def get_multi_by_user(self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Video]:
        return db.query(Video).filter(Video.user_id == user_id, Video.deleted_at == None).offset(skip).limit(limit).all()

    def get_by_youtube_id(self, db: Session, *, user_id: UUID, youtube_id: str) -> Video:
        return db.query(Video).filter(Video.user_id == user_id, Video.youtube_id == youtube_id, Video.deleted_at == None).first()

video = CRUDVideo(Video)
