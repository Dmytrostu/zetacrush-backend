from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.dependencies import get_db
from services.user_service import register_user, auth_user
from schemas.user import UserCreate, UserOut
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=UserOut, summary="Register a new user", description="Create a new user account and start a free trial subscription.")
def register(user: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    """
    Create a new user account and start a free trial subscription.
    - **username**: Desired username
    - **password**: Desired password
    Returns the created user object.
    """
    logger.info(f"Register request for username: {user.username}")
    try:
        result = register_user(db, user)
        logger.info(f"User registered: {user.username}")
        return result
    except HTTPException as e:
        logger.error(f"Registration error for username {user.username}: {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during registration for username {user.username}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/login", summary="Authenticate user and get access token", description="Authenticate a user and return a JWT access token.")
def login(user: UserCreate, db: Session = Depends(get_db)) -> dict:
    """
    Authenticate a user and return a JWT access token.
    - **username**: User's username
    - **password**: User's password
    Returns an access token if authentication is successful.
    """
    logger.info(f"Login request for username: {user.username}")
    try:
        result = auth_user(db, user)
        logger.info(f"User authenticated: {user.username}")
        return result
    except HTTPException as e:
        logger.error(f"Login error for username {user.username}: {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during login for username {user.username}")
        raise HTTPException(status_code=500, detail="Internal server error")
