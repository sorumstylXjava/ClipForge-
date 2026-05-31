from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate

class CRUDSubscription(CRUDBase[Subscription, SubscriptionCreate, SubscriptionUpdate]):
    def get_active_by_user(self, db: Session, *, user_id: UUID) -> Optional[Subscription]:
        return db.query(Subscription).filter(Subscription.user_id == user_id, Subscription.status == "active").first()

subscription = CRUDSubscription(Subscription)
