"""
auth_service.py
---------------
Business logic for user authentication and session management.

Rules enforced here:
- Email uniqueness validation
- Password hashing delegated to security module
- JWT access + refresh token generation
- Token validation & rotation
- Soft-delete / active-user gate
- last_login_at timestamp update
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
)
from app.models.user import User


# ─── Constants ───────────────────────────────────────────────────────────────

ALGORITHM = "HS256"
REFRESH_TOKEN_EXPIRE_DAYS = 30


# ─── Token Helpers ───────────────────────────────────────────────────────────

def _create_refresh_token(user_id: UUID) -> str:
    """Generate a long-lived refresh token (30 days)."""
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def _decode_refresh_token(token: str) -> UUID:
    """Validate a refresh token and return the user_id it encodes."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token type mismatch – expected refresh token.",
        )
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing subject.",
        )
    return UUID(sub)


def _build_auth_response(
    user: User, is_new_user: bool = False
) -> schemas.AuthResponse:
    """Build the standard auth response payload (tokens + user snapshot)."""
    access_token = create_access_token(
        subject=user.id,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = _create_refresh_token(user.id)

    user_resp = schemas.UserResponse(
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

    return schemas.AuthResponse(
        user=user_resp,
        access_token=access_token,
        refresh_token=refresh_token,
        is_new_user=is_new_user,
    )


# ─── Service Functions ────────────────────────────────────────────────────────

def register(
    db: Session,
    *,
    email: str,
    password: str,
    full_name: Optional[str] = None,
) -> schemas.AuthResponse:
    """
    Register a new user account.

    Business rules:
    - Email must be unique.
    - New accounts default to 'free' plan.
    - Returns a full auth response (token pair + user snapshot).
    """
    existing = crud.user.get_by_email(db, email=email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    user_in = schemas.UserCreate(
        email=email,
        password=password,
        full_name=full_name,
        plan="free",
    )
    user = crud.user.create(db, obj_in=user_in)

    # Log first login
    _touch_last_login(db, user)

    # Log activity
    _log_action(db, user_id=user.id, action="register", plan_at_time=user.plan)

    return _build_auth_response(user, is_new_user=True)


def login(
    db: Session,
    *,
    email: str,
    password: str,
) -> schemas.AuthResponse:
    """
    Authenticate a user with email + password.

    Business rules:
    - User must exist and be active.
    - Password must match stored hash.
    - Updates last_login_at on success.
    - Returns a full auth response.
    """
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact support.",
        )

    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    _touch_last_login(db, user)
    _log_action(db, user_id=user.id, action="login", plan_at_time=user.plan)

    return _build_auth_response(user, is_new_user=False)


def refresh_tokens(
    db: Session,
    *,
    refresh_token: str,
) -> schemas.AuthResponse:
    """
    Issue a new token pair given a valid refresh token.

    Business rules:
    - Refresh token must be valid and not expired.
    - User must still be active.
    """
    user_id = _decode_refresh_token(refresh_token)
    user = crud.user.get(db, id=user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated.")

    _log_action(db, user_id=user.id, action="token_refresh", plan_at_time=user.plan)
    return _build_auth_response(user)


def get_current_user_profile(db: Session, *, user: User) -> schemas.UserResponse:
    """Return the public profile snapshot for the currently authenticated user."""
    return schemas.UserResponse(
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


def delete_account(db: Session, *, user: User) -> None:
    """
    Soft-delete a user account.

    Business rules:
    - Sets deleted_at to now.
    - Sets is_active to False.
    - Does NOT hard-delete the user row (data retention).
    """
    crud.user.update(db, db_obj=user, obj_in={
        "is_active": False,
        "deleted_at": datetime.now(timezone.utc),
    })
    _log_action(db, user_id=user.id, action="account_deleted", plan_at_time=user.plan)


# ─── Private Helpers ──────────────────────────────────────────────────────────

def _touch_last_login(db: Session, user: User) -> None:
    """Update the last_login_at timestamp on the user row."""
    crud.user.update(db, db_obj=user, obj_in={"last_login_at": datetime.now(timezone.utc)})


def _log_action(
    db: Session,
    *,
    user_id: UUID,
    action: str,
    plan_at_time: Optional[str] = None,
) -> None:
    """Write an entry to usage_logs for audit trail."""
    try:
        log_in = schemas.UsageLogCreate(
            user_id=user_id,
            action=action,
            plan_at_time=plan_at_time,
        )
        crud.usage_log.create(db, obj_in=log_in)
    except Exception:
        # Log failures must never break the main flow
        pass
