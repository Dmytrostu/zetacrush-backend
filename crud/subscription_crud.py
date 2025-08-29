from sqlalchemy.orm import Session
from models.subscription import Subscription
from models.user import User
from datetime import datetime, timedelta
from typing import Optional
from core.constants import BASIC_MAX_UPLOADS, PREMIUM_MAX_UPLOADS, UNLIMITED_MAX_UPLOADS, DEFAULT_MAX_UPLOADS


def get_subscription_by_user(db: Session, user_id: int):
    """
    Retrieve a subscription by user ID.
    Args:
        db (Session): SQLAlchemy session.
        user_id (int): User's ID.
    Returns:
        Subscription or None: Subscription ORM object if found, else None.
    """
    return db.query(Subscription).filter(Subscription.user_id == user_id).first()


def activate_subscription(db: Session, user_id: int, plan: str = "basic"):
    """
    Activate a paid subscription for a user.
    Args:
        db (Session): SQLAlchemy session.
        user_id (int): User's ID.
        plan (str): Subscription plan name ("basic", "premium", etc).
    Returns:
        Subscription or None: Updated Subscription ORM object if found, else None.
    """
    sub = get_subscription_by_user(db, user_id)
    user = db.query(User).filter(User.id == user_id).first()
    
    if sub and user:
        # Set subscription details
        sub.subscription_active = True
        sub.subscription_plan = plan
        sub.subscription_expires_at = datetime.utcnow() + timedelta(days=30)
          # Update upload limits based on plan
        if plan == "basic":
            user.max_uploads = BASIC_MAX_UPLOADS
        elif plan == "premium":
            user.max_uploads = PREMIUM_MAX_UPLOADS
        elif plan == "unlimited":
            user.max_uploads = UNLIMITED_MAX_UPLOADS
        
        db.commit()
        return sub
    return None


def check_subscription_status(db: Session, user_id: int):
    """
    Check and update the status of a user's subscription.
    Args:
        db (Session): SQLAlchemy session.
        user_id (int): User's ID.
    Returns:
        dict: Status of trial and paid subscription.
    """
    sub = get_subscription_by_user(db, user_id)
    now = datetime.utcnow()
    
    if not sub:
        return {
            "trial_active": False,
            "subscription_active": False
        }
    
    # Check and update trial status
    if sub.trial_active and sub.trial_expires_at and sub.trial_expires_at < now:
        sub.trial_active = False
        db.commit()
    
    # Check and update subscription status
    if sub.subscription_active and sub.subscription_expires_at and sub.subscription_expires_at < now:
        sub.subscription_active = False
        db.commit()
    
    return {
        "trial_active": sub.trial_active,
        "subscription_active": sub.subscription_active
    }


def cancel_user_subscription(db: Session, user_id: int) -> Optional[Subscription]:
    """
    Cancel a user's subscription.
    Args:
        db (Session): SQLAlchemy session.
        user_id (int): User's ID.
    Returns:
        Subscription or None: Updated Subscription ORM object if found, else None.
    """
    sub = get_subscription_by_user(db, user_id)
    
    if sub:
        # Deactivate subscription
        sub.subscription_active = False
        sub.subscription_expires_at = None
        
        # Reset user to basic uploads
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.max_uploads = 5  # Reset to free tier
        
        db.commit()
        return sub
    return None
