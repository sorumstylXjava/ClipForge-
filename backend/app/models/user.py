from sqlalchemy import Column, String, Boolean, BigInteger, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"
    
    # Identity
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    supabase_uid = Column(String, unique=True, index=True, nullable=True) 
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    avatar_url = Column(String)
    phone = Column(String)

    # Plan & Configuration
    plan = Column(String, nullable=False, server_default="free")
    ai_mode = Column(String, nullable=False, server_default="server")
    preferred_lang = Column(String, nullable=False, server_default="en")
    preferred_resolution = Column(String, server_default="720p")

    # Status
    is_admin = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)

    # Storage Usage
    storage_used_bytes = Column(BigInteger, nullable=False, default=0)
    storage_quota_bytes = Column(BigInteger, nullable=False, default=5368709120)

    # Timestamps
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()"), nullable=False)
    deleted_at = Column(DateTime(timezone=True))
