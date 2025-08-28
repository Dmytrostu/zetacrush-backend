from pydantic import BaseModel
from datetime import datetime

class SubscriptionOut(BaseModel):
    """
    Pydantic schema for subscription response.
    Attributes:
        id (int): Subscription ID.
        trial_end (datetime): End of trial period.
        paid_until (datetime): End of paid subscription.
    """
    id: int
    trial_end: datetime
    paid_until: datetime
    class Config:
        orm_mode = True
