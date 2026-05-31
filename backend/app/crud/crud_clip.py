from uuid import UUID
from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.clip import Clip
from app.schemas.clip import ClipCreate, ClipUpdate

class CRUDClip(CRUDBase[Clip, ClipCreate, ClipUpdate]):
    def get_multi_by_user(self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Clip]:
        return db.query(Clip).filter(Clip.user_id == user_id, Clip.deleted_at == None).offset(skip).limit(limit).all()
        
    def get_multi_by_video(self, db: Session, *, video_id: UUID, skip: int = 0, limit: int = 100) -> List[Clip]:
        return db.query(Clip).filter(Clip.video_id == video_id, Clip.deleted_at == None).offset(skip).limit(limit).all()

clip = CRUDClip(Clip)
