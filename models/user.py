from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from core.database import Base

class User(Base):
    """
    SQLAlchemy ORM model for the User table.
    Attributes:
        id (int): Primary key.
        username (str): Unique username.
        password (str): Hashed password.
        subscriptions (list): Relationship to Subscription.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    subscriptions = relationship("Subscription", back_populates="user")
