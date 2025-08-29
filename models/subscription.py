from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from core.database import Base

class Subscription(Base):
    """
    SQLAlchemy ORM model for the Subscription table.
    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key to User.
        trial_active (bool): Whether the trial is active.
        trial_expires_at (datetime): When the trial expires.
        subscription_active (bool): Whether the paid subscription is active.
        subscription_plan (str): The subscription plan type (e.g. "basic", "premium").
        subscription_expires_at (datetime): When the subscription expires.
        user (User): Relationship to User.
    """
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trial_active = Column(Boolean, default=True)
    trial_expires_at = Column(DateTime, nullable=True)
    subscription_active = Column(Boolean, default=False)
    subscription_plan = Column(String, nullable=True)
    subscription_expires_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="subscriptions")
