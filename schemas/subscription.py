from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SubscriptionOut(BaseModel):
    """
    Pydantic schema for subscription response.
    Attributes:
        id (int): Subscription ID.
        trial_active (bool): Whether the trial is active.
        trial_expires_at (datetime, optional): When the trial expires.
        subscription_active (bool): Whether the paid subscription is active.
        subscription_plan (str, optional): The subscription plan type.
        subscription_expires_at (datetime, optional): When the subscription expires.
        upload_count (int): Number of files uploaded by the user.
        max_uploads (int): Maximum allowed uploads based on plan.
        remaining_uploads (int): Number of uploads remaining.
    """
    id: int
    trial_active: bool
    trial_expires_at: Optional[datetime] = None
    subscription_active: bool
    subscription_plan: Optional[str] = None
    subscription_expires_at: Optional[datetime] = None
    upload_count: int
    max_uploads: int
    remaining_uploads: int
class Config:
    from_attributes = True

class SubscriptionCreate(BaseModel):
    """
    Pydantic schema for subscription creation.
    Attributes:
        plan (str): Subscription plan (e.g. "basic", "premium").
    """
    plan: str = "basic"

class SubscriptionPlan(BaseModel):
    """
    Pydantic schema for subscription plans.
    Attributes:
        id (str): Plan ID.
        name (str): Plan name.
        description (str): Plan description.
        price (float): Monthly price.
        max_uploads (int): Maximum uploads allowed per month.
        features (List[str]): List of features included in this plan.
    """
    id: str
    name: str
    description: str
    price: float
    max_uploads: int
    features: List[str]
