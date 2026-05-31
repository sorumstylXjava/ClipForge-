from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/me", response_model=schemas.Subscription)
def get_current_subscription(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user's active subscription.
    """
    subscription = crud.subscription.get_active_by_user(db, user_id=current_user.id)
    if not subscription:
        # Default to free plan logic if not found
        return schemas.Subscription(
            id="00000000-0000-0000-0000-000000000000",
            user_id=current_user.id,
            plan="free",
            status="active",
            started_at=current_user.created_at,
            created_at=current_user.created_at,
            updated_at=current_user.created_at
        )
    return subscription
