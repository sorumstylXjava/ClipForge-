from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    plan = Column(String, nullable=False)
    status = Column(String, nullable=False)

    started_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True))
    trial_ends_at = Column(DateTime(timezone=True))

    payment_provider = Column(String)
    provider_sub_id = Column(String)
    provider_product_id = Column(String)
    provider_data = Column(JSONB)

    cancelled_at = Column(DateTime(timezone=True))
    cancellation_reason = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()"), nullable=False)

    user = relationship("User", backref="subscriptions")
