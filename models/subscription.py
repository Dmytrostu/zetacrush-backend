from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class Subscription(Base):
    """
    SQLAlchemy ORM model for the Subscription table.
    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key to User.
        trial_end (datetime): End of trial period.
        paid_until (datetime): End of paid subscription.
        user (User): Relationship to User.
    """
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trial_end = Column(DateTime, nullable=False)
    paid_until = Column(DateTime, nullable=False)
    user = relationship("User", back_populates="subscriptions")
