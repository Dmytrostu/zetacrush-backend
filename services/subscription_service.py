from sqlalchemy.orm import Session
from crud.subscription_crud import update_subscription_paid, get_subscription_by_user
from fastapi import HTTPException
from crud.user_crud import get_user_by_username
from utils.auth import decode_jwt_token
import logging

logger = logging.getLogger(__name__)

def subscribe_user(db: Session, token: str) -> dict:
    """
    Service to activate a user's subscription for 30 days.
    Security:
        - Uses JWT for authentication tokens.
        - Validates and sanitizes user input.
    Args:
        db (Session): SQLAlchemy session.
        token (str): JWT access token from the user.
    Returns:
        dict: Subscription activation message.
    Raises:
        HTTPException: If user is invalid or subscription not found.
    """
    logger.info(f"Subscription activation requested for token: {token}")
    payload = decode_jwt_token(token)
    username = payload.get("sub")
    if not username or not isinstance(username, str):
        logger.error("Invalid token or username.")
        raise HTTPException(status_code=401, detail="Invalid token or username.")
    username = username.strip()
    if not username.isalnum():
        logger.error("Invalid username format.")
        raise HTTPException(status_code=400, detail="Invalid username format.")
    user = get_user_by_username(db, username)
    if not user:
        logger.error("Invalid user.")
        raise HTTPException(status_code=401, detail="Invalid user")
    sub = update_subscription_paid(db, user.id)
    if not sub:
        logger.error("Subscription not found.")
        raise HTTPException(status_code=404, detail="Subscription not found")
    logger.info(f"Subscription activated for user: {username}")
    return {"msg": "Subscription active for 30 days."}
