"""
ClipForge Backend — Pydantic Schemas untuk Authentication
"""

import re
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


# ─────────────────────────────────────────────────────────────────────────────
# Request Schemas
# ─────────────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    """POST /auth/register"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str | None = Field(None, max_length=255)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Minimal: 1 huruf + 1 angka."""
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password harus mengandung minimal 1 huruf.")
        if not re.search(r"\d", v):
            raise ValueError("Password harus mengandung minimal 1 angka.")
        return v


class LoginRequest(BaseModel):
    """POST /auth/login"""
    email: EmailStr
    password: str = Field(..., min_length=1)


class GoogleAuthRequest(BaseModel):
    """POST /auth/google — Google OAuth ID Token dari Android"""
    id_token: str = Field(..., min_length=1)


class RefreshTokenRequest(BaseModel):
    """POST /auth/refresh"""
    refresh_token: str = Field(..., min_length=1)


class UpdateProfileRequest(BaseModel):
    """PATCH /auth/me — semua field opsional"""
    full_name: str | None = Field(None, max_length=255)
    ai_mode: Literal["local", "server"] | None = None
    preferred_resolution: Literal["480p", "720p", "1080p", "4k"] | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Response Schemas
# ─────────────────────────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    """Schema user untuk response API."""
    id: str
    email: str
    full_name: str | None
    avatar_url: str | None
    plan: str
    ai_mode: str
    preferred_resolution: str
    storage_used_bytes: int
    storage_quota_bytes: int
    is_admin: bool
    is_active: bool
    created_at: str
    last_login_at: str | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, user) -> "UserResponse":
        return cls(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            plan=user.plan,
            ai_mode=user.ai_mode,
            preferred_resolution=user.preferred_resolution,
            storage_used_bytes=user.storage_used_bytes,
            storage_quota_bytes=user.storage_quota_bytes,
            is_admin=user.is_admin,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
        )


class TokenPair(BaseModel):
    """Access + Refresh token pair."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    """Response untuk register dan login."""
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    is_new_user: bool = False


class LogoutResponse(BaseModel):
    message: str = "Logged out successfully."
