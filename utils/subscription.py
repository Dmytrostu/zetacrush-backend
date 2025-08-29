from fastapi import HTTPException
from sqlalchemy.orm import Session
from crud.subscription_crud import get_subscription_by_user, check_subscription_status
from datetime import datetime

def validate_subscription(db: Session, user_id: int) -> None:
    """
    Validate if the user has an active subscription (trial or paid).
    
    This function checks if the user has an active trial or paid subscription.
    It first updates the subscription status based on current date/time, then
    validates if the user has access rights.
    
    Args:
        db (Session): SQLAlchemy session.
        user_id (int): User's ID.
        
    Raises:
        HTTPException: If subscription is not active.
    """
    # Get subscription and check/update its status
    sub = get_subscription_by_user(db, user_id)
    if not sub:
        raise HTTPException(status_code=404, detail="No subscription found for this user.")
    
    # Check subscription status (this updates the status if needed)
    status = check_subscription_status(db, user_id)
    
    # Check if user has access
    if not (status["trial_active"] or status["subscription_active"]):
        raise HTTPException(
            status_code=402, 
            detail="Subscription required. Your trial has expired or your subscription is inactive."
        )
