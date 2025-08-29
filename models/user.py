from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base
from core.constants import DEFAULT_MAX_UPLOADS

class User(Base):
    """
    SQLAlchemy ORM model for the User table.
    Attributes:
        id (int): Primary key.
        email (str): User's email (unique).
        name (str): User's name (optional).
        password (str): Hashed password.
        created_at (datetime): Account creation date.
        upload_count (int): Number of files uploaded.
        max_uploads (int): Maximum allowed uploads based on plan.
        subscriptions (list): Relationship to Subscription.
        books (list): Relationship to Book.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    upload_count = Column(Integer, default=0)
    max_uploads = Column(Integer, default=DEFAULT_MAX_UPLOADS)  # Default limit for free users
    subscriptions = relationship("Subscription", back_populates="user")
    # books relationship is defined via backref in Book model
