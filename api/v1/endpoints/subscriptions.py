from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.dependencies import get_db, get_current_user_id
from services.subscription_service import subscribe_user, cancel_subscription, get_subscription_plans
from schemas.subscription import SubscriptionCreate, SubscriptionPlan
from typing import List
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/subscribe", summary="Subscribe to monthly plan", description="Activate or renew a user's monthly subscription. Requires JWT token.")
def subscribe(
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> dict:
    """
    Activate or renew a user's monthly subscription.
    
    - **plan**: Subscription plan ("basic", "premium", etc)
    
    Authentication required via Bearer token.
    Returns a message confirming subscription activation.
    """
    logger.info(f"Subscription request received for user ID: {user_id}, plan: {subscription.plan}")
    try:
        result = subscribe_user(db, user_id, subscription)
        logger.info(f"Subscription activated for user ID: {user_id}, plan: {subscription.plan}")
        return result
    except HTTPException as e:
        logger.error(f"Subscription error for user ID {user_id}: {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during subscription for user ID {user_id}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/plans", response_model=List[SubscriptionPlan], summary="Get available subscription plans", description="Get a list of available subscription plans.")
def get_plans(db: Session = Depends(get_db)) -> List[SubscriptionPlan]:
    """
    Get a list of available subscription plans.
    
    Returns:
        List[SubscriptionPlan]: List of available subscription plans.
    """
    logger.info("Subscription plans request received")
    try:
        plans = get_subscription_plans()
        return plans
    except Exception as e:
        logger.exception(f"Error retrieving subscription plans: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/cancel", summary="Cancel subscription", description="Cancel the current subscription.")
def cancel(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> dict:
    """
    Cancel the current subscription.
    
    Args:
        db (Session): Database session.
        user_id (int): Current user ID.
        
    Returns:
        dict: Success message with updated subscription status.
    """
    logger.info(f"Subscription cancellation request received for user ID: {user_id}")
    try:
        result = cancel_subscription(db, user_id)
        logger.info(f"Subscription cancelled for user ID: {user_id}")
        return result
    except HTTPException as e:
        logger.error(f"Subscription cancellation error for user ID {user_id}: {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during subscription cancellation for user ID {user_id}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("", summary="Update subscription", description="Change subscription plan.")
def update_subscription(
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> dict:
    """
    Change a user's subscription plan.
    
    Args:
        subscription (SubscriptionCreate): New subscription plan.
        db (Session): Database session.
        user_id (int): Current user ID.
        
    Returns:
        dict: Updated subscription details.
    """
    logger.info(f"Subscription update request received for user ID: {user_id}, plan: {subscription.plan}")
    try:
        # We can reuse the subscribe_user service as it handles both new subscriptions and updates
        result = subscribe_user(db, user_id, subscription)
        logger.info(f"Subscription updated for user ID: {user_id}, plan: {subscription.plan}")
        return result
    except HTTPException as e:
        logger.error(f"Subscription update error for user ID {user_id}: {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during subscription update for user ID {user_id}")
        raise HTTPException(status_code=500, detail="Internal server error")
