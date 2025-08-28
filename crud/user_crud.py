from sqlalchemy.orm import Session
from models.user import User
from models.subscription import Subscription
from schemas.user import UserCreate, UserOut
from datetime import datetime, timedelta
from utils.auth import get_password_hash, verify_password


def create_user(db: Session, user: UserCreate):
    """
    Create a new user and initialize their subscription with a 3-day trial.
    Args:
        db (Session): SQLAlchemy database session.
        user (UserCreate): Pydantic model with username and password.
    Returns:
        User: The created User ORM object.
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    sub = Subscription(user_id=db_user.id, trial_end=datetime.utcnow() + timedelta(days=3), paid_until=datetime.utcnow())
    db.add(sub)
    db.commit()
    return db_user


def get_user_by_username(db: Session, username: str):
    """
    Retrieve a user by their username.
    Args:
        db (Session): SQLAlchemy database session.
        username (str): Username to search for.
    Returns:
        User or None: User ORM object if found, else None.
    """
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    """
    Authenticate a user by verifying their password.
    Args:
        db (Session): SQLAlchemy database session.
        username (str): Username to authenticate.
        password (str): Plain text password to verify.
    Returns:
        User or None: User ORM object if authentication succeeds, else None.
    """
    user = get_user_by_username(db, username)
    if user and verify_password(password, user.password):
        return user
    return None
