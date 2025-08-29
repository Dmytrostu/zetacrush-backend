from core.database import SessionLocal
from utils.auth import get_current_user_email, get_current_user_id
from fastapi import Depends

def get_db():
    """
    Dependency to get a database session.
    
    Yields:
        Session: SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Re-export auth dependencies for convenience
__all__ = ["get_db", "get_current_user_email", "get_current_user_id"]
