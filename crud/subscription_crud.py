from sqlalchemy.orm import Session
from models.subscription import Subscription
from datetime import datetime, timedelta


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


def update_subscription_paid(db: Session, user_id: int):
    """
    Update a user's subscription to extend paid period by 30 days.
    Args:
        db (Session): SQLAlchemy session.
        user_id (int): User's ID.
    Returns:
        Subscription or None: Updated Subscription ORM object if found, else None.
    """
    sub = get_subscription_by_user(db, user_id)
    if sub:
        sub.paid_until = datetime.utcnow() + timedelta(days=30)
        db.commit()
        return sub
    return None
