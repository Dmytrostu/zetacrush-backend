from sqlalchemy.orm import Session
from crud.subscription_crud import activate_subscription, get_subscription_by_user, cancel_user_subscription, check_subscription_status
from fastapi import HTTPException
from crud.user_crud import get_user_by_id
from schemas.subscription import SubscriptionCreate, SubscriptionPlan
from typing import List
import logging
from core.constants import BASIC_MAX_UPLOADS, PREMIUM_MAX_UPLOADS, UNLIMITED_MAX_UPLOADS

logger = logging.getLogger(__name__)

def subscribe_user(db: Session, user_id: int, subscription_data: SubscriptionCreate) -> dict:
    """
    Service to activate a user's subscription for 30 days.
    
    Args:
        db (Session): SQLAlchemy session.
        user_id (int): User ID from the JWT token.
        subscription_data (SubscriptionCreate): Subscription details including plan.
        
    Returns:
        dict: Subscription activation message and details.
        
    Raises:
        HTTPException: If user is invalid or subscription not found.
    """
    logger.info(f"Subscription activation requested for user ID: {user_id}, plan: {subscription_data.plan}")
    
    # Verify user exists
    user = get_user_by_id(db, user_id)
    if not user:
        logger.error(f"User not found with ID: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    # Activate subscription with specified plan
    sub = activate_subscription(db, user_id, subscription_data.plan)
    if not sub:
        logger.error("Subscription not found.")
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    logger.info(f"Subscription activated for user ID: {user_id}, plan: {subscription_data.plan}")
      # Return subscription details with upload info
    remaining_uploads = max(0, user.max_uploads - user.upload_count)
    
    return {
        "message": f"{subscription_data.plan.capitalize()} subscription activated for 30 days.",
        "plan": subscription_data.plan,
        "active": True,
        "expires_at": sub.subscription_expires_at.isoformat() if sub.subscription_expires_at else None,
        "upload_count": user.upload_count,
        "max_uploads": user.max_uploads,
        "remaining_uploads": remaining_uploads
    }

def cancel_subscription(db: Session, user_id: int) -> dict:
    """
    Cancel a user's subscription.
    
    Args:
        db (Session): SQLAlchemy session.
        user_id (int): User ID.
        
    Returns:
        dict: Cancellation message and subscription status.
        
    Raises:
        HTTPException: If user is invalid or subscription not found.
    """
    logger.info(f"Cancellation requested for user ID: {user_id}")
    
    # Verify user exists
    user = get_user_by_id(db, user_id)
    if not user:
        logger.error(f"User not found with ID: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    # Cancel subscription
    sub = cancel_user_subscription(db, user_id)
    if not sub:
        logger.error("Subscription not found.")
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    logger.info(f"Subscription cancelled for user ID: {user_id}")
    
    # Return updated status
    remaining_uploads = max(0, user.max_uploads - user.upload_count)
    
    return {
        "message": "Subscription cancelled successfully.",
        "trial_active": sub.trial_active,
        "subscription_active": False,
        "upload_count": user.upload_count,
        "max_uploads": user.max_uploads,
        "remaining_uploads": remaining_uploads
    }

def get_user_subscription_status(db: Session, user_id: int) -> dict:
    """
    Get a user's subscription status.
    
    Args:
        db (Session): SQLAlchemy session.
        user_id (int): User ID.
        
    Returns:
        dict: Subscription status details.
        
    Raises:
        HTTPException: If user is invalid or subscription not found.
    """
    logger.info(f"Getting subscription status for user ID: {user_id}")
    
    # Verify user exists
    user = get_user_by_id(db, user_id)
    if not user:
        logger.error(f"User not found with ID: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get subscription
    sub = get_subscription_by_user(db, user_id)
    if not sub:
        logger.error(f"Subscription not found for user ID: {user_id}")
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Check current status (this may update the status if expired)
    status = check_subscription_status(db, user_id)
    
    # Calculate remaining uploads
    remaining_uploads = max(0, user.max_uploads - user.upload_count)
    
    # Format dates as ISO strings for frontend compatibility
    trial_expires_iso = sub.trial_expires_at.isoformat() if sub.trial_expires_at else None
    subscription_expires_iso = sub.subscription_expires_at.isoformat() if sub.subscription_expires_at else None
    
    return {
        "trial_active": status["trial_active"],
        "trial_expires_at": trial_expires_iso,
        "subscription_active": status["subscription_active"],
        "subscription_plan": sub.subscription_plan,
        "subscription_expires_at": subscription_expires_iso,
        "upload_count": user.upload_count,
        "max_uploads": user.max_uploads,
        "remaining_uploads": remaining_uploads
    }

def get_subscription_plans() -> List[SubscriptionPlan]:
    """
    Get available subscription plans.
    
    Returns:
        List[SubscriptionPlan]: List of available subscription plans.
    """
    # In a real application, these would be retrieved from a database
    return [
        SubscriptionPlan(
            id="basic",
            name="Basic",
            description="Basic subscription with up to 1000 uploads per month",
            price=9.99,
            max_uploads=1000,
            features=["Upload PDF, TXT, and DOC files", "Character extraction", "Synopsis generation", "Easter egg finding"]
        ),
        SubscriptionPlan(
            id="premium",
            name="Premium",
            description="Premium subscription with up to 2500 uploads per month",
            price=19.99,
            max_uploads=2500,
            features=["All Basic features", "Priority processing", "Full character details", "Extended synopsis"]
        ),
        SubscriptionPlan(
            id="unlimited",
            name="Unlimited",
            description="Unlimited subscription with unlimited uploads",
            price=39.99,
            max_uploads=10000,
            features=["All Premium features", "Unlimited uploads", "Advanced analytics", "API access"]
        )
    ]
