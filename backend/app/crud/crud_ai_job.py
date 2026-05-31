from uuid import UUID
from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.ai_job import AIJob
from app.schemas.ai_job import AIJobCreate, AIJobUpdate

class CRUDAIJob(CRUDBase[AIJob, AIJobCreate, AIJobUpdate]):
    def get_multi_by_user(self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 100) -> List[AIJob]:
        return db.query(AIJob).filter(AIJob.user_id == user_id).offset(skip).limit(limit).all()
        
    def get_multi_by_video(self, db: Session, *, video_id: UUID, skip: int = 0, limit: int = 100) -> List[AIJob]:
        return db.query(AIJob).filter(AIJob.video_id == video_id).offset(skip).limit(limit).all()

ai_job = CRUDAIJob(AIJob)
