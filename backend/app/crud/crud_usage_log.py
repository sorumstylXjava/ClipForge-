from uuid import UUID
from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.usage_log import UsageLog
from app.schemas.usage_log import UsageLogCreate

class CRUDUsageLog(CRUDBase[UsageLog, UsageLogCreate, UsageLogCreate]):
    def get_multi_by_user(self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 100) -> List[UsageLog]:
        return db.query(UsageLog).filter(UsageLog.user_id == user_id).offset(skip).limit(limit).all()

usage_log = CRUDUsageLog(UsageLog)
