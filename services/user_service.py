from sqlalchemy.orm import Session
from crud.user_crud import create_user, get_user_by_email, authenticate_user, get_user_by_id, update_user
from crud.subscription_crud import get_subscription_by_user, check_subscription_status
from schemas.user import UserCreate, UserOut, UserLogin, UserProfile, UserUpdate
from fastapi import HTTPException
import logging
from utils.auth import create_jwt_token
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

def register_user(db: Session, user: UserCreate) -> dict:
    """
    Service to register a new user.
    Args:
        db (Session): SQLAlchemy session.
        user (UserCreate): User creation schema.
    Returns:
        dict: Response matching SignUpResponse interface with user data and token.
    """
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Create the user
    db_user = create_user(db, user)
    
    # Get subscription info to include trial and subscription status
    sub = get_subscription_by_user(db, db_user.id)
    trial_active = False
    subscription_active = False
    subscription_expires_at = None
    
    if sub:
        trial_active = sub.trial_active
        subscription_active = sub.subscription_active
        subscription_expires_at = sub.subscription_expires_at.isoformat() if sub.subscription_expires_at else None
    
    # Create JWT token
    token = create_jwt_token({"sub": user.email, "user_id": db_user.id})
    
    # Format response according to SignUpResponse interface
    return {
        "token": token,
        "user": {
            "id": str(db_user.id),
            "email": db_user.email,
            "name": db_user.name,
            "trialActive": trial_active,
            "subscriptionActive": subscription_active,
            "subscriptionExpiresAt": subscription_expires_at
        }
    }


def auth_user(db: Session, user: UserLogin) -> dict:
    """
    Service to authenticate a user and return a JWT access token.
    Args:
        db (Session): SQLAlchemy session.
        user (UserLogin): User login schema.
    Returns:
        dict: Auth response with token and user information matching AuthResponse interface.
    """
    db_user = authenticate_user(db, user.email, user.password)
    print(db_user)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Get subscription info to include trial and subscription status
    sub = get_subscription_by_user(db, db_user.id)
    trial_active = False
    subscription_active = False
    
    if sub:
        trial_active = sub.trial_active
        subscription_active = sub.subscription_active
    
    token = create_jwt_token({"sub": user.email, "user_id": db_user.id})
    
    # Format response according to AuthResponse interface
    return {
        "token": token, 
        "user": {
            "id": str(db_user.id),
            "email": db_user.email,
            "name": db_user.name,
            "trialActive": trial_active,
            "subscriptionActive": subscription_active
        }
    }


def get_user_profile(db: Session, user_id: int) -> UserProfile:
    """
    Get a user's profile information including subscription details.
    
    Args:
        db (Session): SQLAlchemy session.
        user_id (int): User ID.
        
    Returns:
        UserProfile: User profile data formatted according to frontend expectations.
        
    Raises:
        HTTPException: If user not found.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Get subscription info
    sub = get_subscription_by_user(db, user_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Check subscription status (updates if expired)
    check_subscription_status(db, user_id)
    
    # Format dates as ISO strings for frontend compatibility
    created_at_iso = user.created_at.isoformat() if user.created_at else None
    trial_expires_iso = sub.trial_expires_at.isoformat() if sub.trial_expires_at else None
    subscription_expires_iso = sub.subscription_expires_at.isoformat() if sub.subscription_expires_at else None
    # Calculate remaining uploads
    remaining_uploads = max(0, user.max_uploads - user.upload_count)
    
    # Create the profile object
    profile = UserProfile(
        id=str(user.id),  # Convert to string as specified in the interface
        email=user.email,
        name=user.name,
        created_at=created_at_iso,
        trial_active=sub.trial_active,
        trial_expires_at=trial_expires_iso,
        subscription_active=sub.subscription_active,
        subscription_plan=sub.subscription_plan,
        subscription_expires_at=subscription_expires_iso,
        upload_count=user.upload_count,
        max_uploads=user.max_uploads,
        remaining_uploads=remaining_uploads
    )
    
    return profile

def update_user_profile(db: Session, user_id: int, user_data: UserUpdate) -> UserProfile:
    """
    Update a user's profile information.
    
    Args:
        db (Session): SQLAlchemy session.
        user_id (int): User ID.
        user_data (UserUpdate): Updated user data.
        
    Returns:
        UserProfile: Updated user profile.
        
    Raises:
        HTTPException: If user not found or email already exists.
    """
    # Get current user
    user = get_user_by_id(db, user_id)
    if not user:
        logger.error(f"User not found with ID: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if email is being updated and if it already exists
    if user_data.email and user_data.email != user.email:
        existing_user = get_user_by_email(db, user_data.email)
        if existing_user and existing_user.id != user_id:
            logger.error(f"Email {user_data.email} already in use")
            raise HTTPException(status_code=400, detail="Email already in use")
    
    # Update user
    updated_user = update_user(db, user_id, user_data)
    
    # Return updated profile
    return get_user_profile(db, user_id)
