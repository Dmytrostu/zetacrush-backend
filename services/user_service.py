from sqlalchemy.orm import Session
from crud.user_crud import create_user, get_user_by_username, authenticate_user
from schemas.user import UserCreate, UserOut
from fastapi import HTTPException
import logging
from utils.auth import create_jwt_token

logger = logging.getLogger(__name__)

def register_user(db: Session, user: UserCreate) -> UserOut:
    """
    Service to register a new user.
    Args:
        db (Session): SQLAlchemy session.
        user (UserCreate): User creation schema.
    Returns:
        UserOut: Created user ORM object.
    """
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="User already exists")
    return create_user(db, user)


def auth_user(db: Session, user: UserCreate) -> dict:
    """
    Service to authenticate a user and return a JWT access token.
    Args:
        db (Session): SQLAlchemy session.
        user (UserCreate): User creation schema.
    Returns:
        dict: Access token and token type if successful.
    """
    db_user = authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_jwt_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
