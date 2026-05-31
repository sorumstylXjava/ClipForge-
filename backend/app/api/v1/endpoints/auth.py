from datetime import timedelta
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app import crud, schemas
from app.api import deps
from app.core.config import settings
from app.core import security

router = APIRouter()

class GoogleAuthRequest(BaseModel):
    id_token: str

def _make_token(user_id: Any) -> dict:
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(user_id, expires_delta=expires),
        "token_type": "bearer",
    }

@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = crud.user.get_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return _make_token(user.id)

@router.post("/auth/google", response_model=schemas.Token)
def login_with_google(
    payload: GoogleAuthRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    try:
        idinfo = id_token.verify_oauth2_token(
            payload.id_token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Google token: {str(e)}")

    email = idinfo.get("email")
    full_name = idinfo.get("name", "")

    if not email:
        raise HTTPException(status_code=400, detail="Email not found in Google token")

    user = crud.user.get_by_email(db, email=email)
    if not user:
        user_in = schemas.UserCreate(
            email=email,
            full_name=full_name,
            password=None,
        )
        user = crud.user.create(db, obj_in=user_in)

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return _make_token(user.id)
