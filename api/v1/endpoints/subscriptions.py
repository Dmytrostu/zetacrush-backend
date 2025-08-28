from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.dependencies import get_db
from services.subscription_service import subscribe_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/subscribe", summary="Subscribe to monthly plan", description="Activate or renew a user's monthly subscription. Requires JWT token.")
def subscribe(token: str, db: Session = Depends(get_db)) -> dict:
    """
    Activate or renew a user's monthly subscription.
    - **token**: JWT access token
    Returns a message confirming subscription activation.
    """
    logger.info(f"Subscription request received for token: {token}")
    try:
        result = subscribe_user(db, token)
        logger.info(f"Subscription activated for token: {token}")
        return result
    except HTTPException as e:
        logger.error(f"Subscription error for token {token}: {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during subscription for token {token}")
        raise HTTPException(status_code=500, detail="Internal server error")
