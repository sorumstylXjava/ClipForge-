"""
subscription_service.py
-----------------------
Business logic for subscription lifecycle management.

Rules enforced here:
- Check if a user currently holds an active subscription
- Determine effective plan (free vs premium)
- Sync user.plan field to match active subscription status
- Expire subscriptions that have passed their expires_at date
- Cancel subscription flow (sets cancelled_at, keeps plan active until expiry)
- Activity logging for all subscription events

NOTE: No payment gateway is implemented here.
      Payment verification is expected to be handled externally (e.g. Google Play webhook)
      and only the resulting subscription record is managed by this service.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.models.subscription import Subscription
from app.models.user import User


# ─── Plan Constants ───────────────────────────────────────────────────────────

PREMIUM_PLAN_NAMES = {"premium", "pro"}
FREE_PLAN = "free"


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _is_premium(user: User) -> bool:
    return user.plan in PREMIUM_PLAN_NAMES


def _sync_user_plan(db: Session, user: User, new_plan: str) -> None:
    """Ensure user.plan is consistent with their active subscription."""
    if user.plan != new_plan:
        crud.user.update(db, db_obj=user, obj_in={"plan": new_plan})


# ─── Service Functions ────────────────────────────────────────────────────────

def get_active_subscription(
    db: Session,
    *,
    user: User,
) -> Optional[Subscription]:
    """
    Return the user's current active subscription, or None if they are on Free.

    Side effect:
    - If a subscription's expires_at has passed, it is automatically expired
      and user.plan is reset to 'free'.
    """
    subscription = crud.subscription.get_active_by_user(db, user_id=user.id)

    if subscription is None:
        # No subscription row; ensure user is on free plan
        _sync_user_plan(db, user, FREE_PLAN)
        return None

    now = datetime.now(timezone.utc)

    # Auto-expire subscriptions that have passed their expiry date
    if subscription.expires_at and subscription.expires_at < now:
        _expire_subscription(db, subscription=subscription, user=user)
        return None

    return subscription


def get_subscription_summary(db: Session, *, user: User) -> dict:
    """
    Return a concise plan summary for API responses.

    Returns a dict with:
    - plan: 'free' | 'premium' | ...
    - is_premium: bool
    - status: 'active' | 'none'
    - expires_at: ISO8601 string or None
    - daily_video_quota: int (remaining today) — read-only snapshot
    """
    subscription = get_active_subscription(db, user=user)

    if subscription is None:
        return {
            "plan": FREE_PLAN,
            "is_premium": False,
            "status": "none",
            "expires_at": None,
        }

    return {
        "plan": subscription.plan,
        "is_premium": subscription.plan in PREMIUM_PLAN_NAMES,
        "status": subscription.status,
        "expires_at": subscription.expires_at.isoformat() if subscription.expires_at else None,
    }


def activate_subscription(
    db: Session,
    *,
    user: User,
    plan: str,
    payment_provider: str,
    provider_sub_id: str,
    provider_product_id: Optional[str] = None,
    provider_data: Optional[dict] = None,
    expires_at: Optional[datetime] = None,
    trial_ends_at: Optional[datetime] = None,
) -> Subscription:
    """
    Activate or upgrade a subscription for a user.

    This is called after external payment verification succeeds.

    Business rules:
    - If user already has an active subscription, update it.
    - Otherwise, create a new subscription record.
    - Sync user.plan to the new plan.
    - Log the activation.
    """
    if plan not in PREMIUM_PLAN_NAMES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan '{plan}'. Valid premium plans: {sorted(PREMIUM_PLAN_NAMES)}.",
        )

    existing = crud.subscription.get_active_by_user(db, user_id=user.id)
    now = datetime.now(timezone.utc)

    if existing:
        # Upgrade / renewal: update existing record
        subscription = crud.subscription.update(db, db_obj=existing, obj_in={
            "plan": plan,
            "status": "active",
            "payment_provider": payment_provider,
            "provider_sub_id": provider_sub_id,
            "provider_product_id": provider_product_id,
            "provider_data": provider_data,
            "expires_at": expires_at,
            "trial_ends_at": trial_ends_at,
            "cancelled_at": None,
            "cancellation_reason": None,
        })
    else:
        sub_in = schemas.SubscriptionCreate(
            user_id=user.id,
            plan=plan,
            status="active",
            started_at=now,
            expires_at=expires_at,
            trial_ends_at=trial_ends_at,
            payment_provider=payment_provider,
            provider_sub_id=provider_sub_id,
            provider_product_id=provider_product_id,
            provider_data=provider_data,
        )
        subscription = crud.subscription.create(db, obj_in=sub_in)

    # Sync user.plan field
    _sync_user_plan(db, user, plan)

    _log_action(
        db,
        user_id=user.id,
        action="subscription_activated",
        plan_at_time=plan,
    )

    return subscription


def cancel_subscription(
    db: Session,
    *,
    user: User,
    reason: Optional[str] = None,
) -> Subscription:
    """
    Cancel the user's active subscription.

    Business rules:
    - Subscription stays 'active' until its expires_at date (cancel-at-period-end).
    - cancelled_at is set to now.
    - user.plan remains unchanged until the subscription actually expires.
    - Raises 404 if no active subscription exists.
    """
    subscription = crud.subscription.get_active_by_user(db, user_id=user.id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found to cancel.",
        )

    now = datetime.now(timezone.utc)
    updated = crud.subscription.update(db, db_obj=subscription, obj_in={
        "cancelled_at": now,
        "cancellation_reason": reason,
        # Status remains 'active' — access continues until expires_at
    })

    _log_action(
        db,
        user_id=user.id,
        action="subscription_cancelled",
        plan_at_time=user.plan,
    )
    return updated


def verify_premium_access(db: Session, *, user: User) -> bool:
    """
    Quick boolean check: does the user currently have an active premium subscription?
    Also handles auto-expiry as a side effect.
    """
    subscription = get_active_subscription(db, user=user)
    return subscription is not None and subscription.plan in PREMIUM_PLAN_NAMES


def require_premium(db: Session, *, user: User, feature_name: str = "This feature") -> None:
    """
    Raise HTTP 403 if the user does not have an active premium subscription.
    Use this as a guard inside endpoints or other services.
    """
    if not verify_premium_access(db, user=user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"{feature_name} requires a Premium subscription. "
                "Upgrade to unlock all features."
            ),
        )


# ─── Internal Lifecycle ───────────────────────────────────────────────────────

def _expire_subscription(db: Session, *, subscription: Subscription, user: User) -> None:
    """
    Mark an expired subscription as 'expired' and reset user to free plan.
    This is called automatically by get_active_subscription when expires_at < now.
    """
    crud.subscription.update(db, db_obj=subscription, obj_in={"status": "expired"})
    _sync_user_plan(db, user, FREE_PLAN)
    _log_action(
        db,
        user_id=user.id,
        action="subscription_expired",
        plan_at_time=FREE_PLAN,
    )


# ─── Private Helpers ──────────────────────────────────────────────────────────

def _log_action(
    db: Session,
    *,
    user_id: UUID,
    action: str,
    plan_at_time: Optional[str] = None,
) -> None:
    try:
        log_in = schemas.UsageLogCreate(
            user_id=user_id,
            action=action,
            plan_at_time=plan_at_time,
        )
        crud.usage_log.create(db, obj_in=log_in)
    except Exception:
        pass
