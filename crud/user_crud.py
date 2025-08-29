from sqlalchemy.orm import Session
from models.user import User
from models.subscription import Subscription
from schemas.user import UserCreate, UserOut, UserLogin, UserUpdate
from datetime import datetime, timedelta
from utils.auth import get_password_hash, verify_password
from typing import Optional
from core.constants import DEFAULT_MAX_UPLOADS


def create_user(db: Session, user: UserCreate):
    """
    Create a new user and initialize their subscription with a 3-day trial.
    Args:
        db (Session): SQLAlchemy database session.
        user (UserCreate): Pydantic model with email, optional name, and password.
    Returns:
        User: The created User ORM object.
    """
    hashed_password = get_password_hash(user.password)    
    db_user = User(
        email=user.email,
        name=user.name,
        password=hashed_password,
        created_at=datetime.utcnow(),
        upload_count=0,
        max_uploads=DEFAULT_MAX_UPLOADS  # Default for free/trial users
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    trial_expires = datetime.utcnow() + timedelta(days=3)
    sub = Subscription(
        user_id=db_user.id,
        trial_active=True,
        trial_expires_at=trial_expires,
        subscription_active=False,
        subscription_plan=None,
        subscription_expires_at=None
    )
    db.add(sub)
    db.commit()
    return db_user


def get_user_by_email(db: Session, email: str):
    """
    Retrieve a user by their email.
    Args:
        db (Session): SQLAlchemy database session.
        email (str): Email to search for.
    Returns:
        User or None: User ORM object if found, else None.
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    """
    Retrieve a user by their ID.
    Args:
        db (Session): SQLAlchemy database session.
        user_id (int): User ID to search for.
    Returns:
        User or None: User ORM object if found, else None.
    """
    return db.query(User).filter(User.id == user_id).first()


def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticate a user by verifying their password.
    Args:
        db (Session): SQLAlchemy database session.
        email (str): Email to authenticate.
        password (str): Plain text password to verify.
    Returns:
        User or None: User ORM object if authentication succeeds, else None.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    user = get_user_by_email(db, email)
    if not user:
        logger.warning(f"Authentication failed: No user found with email {email}")
        return False
    
    try:
        if not verify_password(password, user.password):
            logger.warning(f"Authentication failed: Password incorrect for {email}")
            return False
        return user
    except Exception as e:
        logger.error(f"Authentication error for {email}: {str(e)}")
        return False
    
    
def increment_upload_count(db: Session, user_id: int):
    """
    Increment the upload count for a user.
    Args:
        db (Session): SQLAlchemy database session.
        user_id (int): User ID to update.
    Returns:
        User: The updated User ORM object.
    """
    user = get_user_by_id(db, user_id)
    if user:
        user.upload_count += 1
        db.commit()
        db.refresh(user)
    return user


def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
    """
    Update user profile information.
    Args:
        db (Session): SQLAlchemy database session.
        user_id (int): User ID to update.
        user_data (UserUpdate): Updated user data.
    Returns:
        User: The updated User ORM object.
    """
    user = get_user_by_id(db, user_id)
    if user:
        # Update fields if provided in the request
        if user_data.name is not None:
            user.name = user_data.name
        if user_data.email is not None:
            user.email = user_data.email
        
        db.commit()
        db.refresh(user)
    return user
