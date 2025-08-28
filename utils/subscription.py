from fastapi import HTTPException
from sqlalchemy.orm import Session
from crud.subscription_crud import get_subscription_by_user
from datetime import datetime

def validate_subscription(db: Session, user_id: int) -> None:
    """
    Validate if the user has an active subscription (trial or paid).
    Args:
        db (Session): SQLAlchemy session.
        user_id (int): User's ID.
    Raises:
        HTTPException: If subscription is not active.
    """
    sub = get_subscription_by_user(db, user_id)
    if not sub or (sub.trial_end < datetime.utcnow() and sub.paid_until < datetime.utcnow()):
        raise HTTPException(status_code=402, detail="Subscription required.")
