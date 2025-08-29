from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from core.dependencies import get_db, get_current_user_id, get_current_user_email
from services.user_service import register_user, auth_user, get_user_profile, update_user_profile
from schemas.user import UserCreate, UserOut, UserLogin, UserProfile, UserUpdate
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", summary="Register a new user", description="Create a new user account and start a free trial subscription.")
def register(user: UserCreate, db: Session = Depends(get_db)) -> dict:
    """
    Create a new user account and start a free trial subscription.
    - **email**: User's email address
    - **name**: User's name (optional)
    - **password**: Desired password
    
    Returns:
        A response with the user information and access token:
        {
            "token": "JWT token",
            "user": {
                "id": "user ID",
                "email": "user email",
                "name": "optional user name",
                "trialActive": true/false,
                "subscriptionActive": true/false,
                "subscriptionExpiresAt": "optional expiration date"
            }
        }
    """
    logger.info(f"Register request for email: {user.email}")
    try:
        result = register_user(db, user)
        logger.info(f"User registered: {user.email}")
        return result
    except HTTPException as e:
        logger.error(f"Registration error for email {user.email}: {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during registration for email {user.email}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/login", summary="Authenticate user and get access token", description="Authenticate a user and return a JWT access token.")
def login(user: UserLogin, db: Session = Depends(get_db)) -> dict:
    """
    Authenticate a user and return a JWT access token.
    - **email**: User's email
    - **password**: User's password
    Returns an access token if authentication is successful.
    """
    logger.info(f"Login request for email: {user.email}")
    try:
        result = auth_user(db, user)
        logger.info(f"User authenticated: {user.email}")
        return result
    except HTTPException as e:
        logger.error(f"Login error for email {user.email}: {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during login for email {user.email}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/me", response_model=UserProfile, summary="Get current user profile", description="Get the profile of the currently authenticated user.")
def get_current_user_profile(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)) -> UserProfile:
    """
    Get the profile of the currently authenticated user.
    Requires valid JWT token in Authorization header.
    
    Returns:
        UserProfile: User profile information including subscription details.
    """
    logger.info(f"Profile request for user ID: {user_id}")
    try:
        profile = get_user_profile(db, user_id)
        return profile
    except HTTPException as e:
        logger.error(f"Profile retrieval error for user ID {user_id}: {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error retrieving profile for user ID {user_id}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/logout", summary="Logout user", description="Logout current user and invalidate token.")
def logout(user_id: int = Depends(get_current_user_id)) -> dict:
    """
    Logout current user and invalidate token.
    
    Note: Since we're using JWT tokens, actual invalidation would require a token blacklist
    which is not implemented in this simple version. This endpoint is provided for API
    completeness and could log logout events or handle future token invalidation.
    
    Returns:
        dict: Success message.
    """
    logger.info(f"Logout request for user ID: {user_id}")
    return {"message": "Successfully logged out"}

@router.put("/profile", response_model=UserProfile, summary="Update user profile", description="Update the current user's profile information.")
def update_profile(
    user_data: UserUpdate = Body(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> UserProfile:
    """
    Update the current user's profile information.
    
    Args:
        user_data (UserUpdate): Updated user data.
        db (Session): Database session.
        user_id (int): Current user ID.
        
    Returns:
        UserProfile: Updated user profile.
    """
    logger.info(f"Profile update request for user ID: {user_id}")
    try:
        profile = update_user_profile(db, user_id, user_data)
        logger.info(f"Profile updated for user ID: {user_id}")
        return profile
    except HTTPException as e:
        logger.error(f"Profile update error for user ID {user_id}: {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error updating profile for user ID {user_id}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/subscription", summary="Get user subscription status", description="Check the user's current subscription status.")
def get_subscription_status(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Check the user's current subscription status.
    
    Args:
        db (Session): Database session.
        user_id (int): Current user ID.
        
    Returns:
        dict: Subscription details (trial status, subscription status, expiration).
    """
    logger.info(f"Subscription status request for user ID: {user_id}")
    try:
        from services.subscription_service import get_user_subscription_status
        status = get_user_subscription_status(db, user_id)
        return status
    except HTTPException as e:
        logger.error(f"Subscription status error for user ID {user_id}: {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error getting subscription status for user ID {user_id}")
        raise HTTPException(status_code=500, detail="Internal server error")
