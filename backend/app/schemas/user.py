from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    plan: Optional[str] = "free"
    ai_mode: Optional[str] = "server"
    preferred_lang: Optional[str] = "en"
    preferred_resolution: Optional[str] = "720p"

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: UUID
    is_active: bool
    is_admin: bool
    storage_used_bytes: int
    storage_quota_bytes: int

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str
