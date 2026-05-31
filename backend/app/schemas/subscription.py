from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from pydantic.types import Json

class SubscriptionBase(BaseModel):
    plan: str
    status: str
    started_at: datetime
    expires_at: Optional[datetime] = None
    trial_ends_at: Optional[datetime] = None
    payment_provider: Optional[str] = None
    provider_sub_id: Optional[str] = None
    provider_product_id: Optional[str] = None
    provider_data: Optional[dict] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None

class SubscriptionCreate(SubscriptionBase):
    user_id: UUID

class SubscriptionUpdate(BaseModel):
    plan: Optional[str] = None
    status: Optional[str] = None
    expires_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None

class SubscriptionInDBBase(SubscriptionBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Subscription(SubscriptionInDBBase):
    pass
