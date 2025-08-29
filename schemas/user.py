from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    """
    Pydantic schema for user creation requests.
    Attributes:
        email (EmailStr): User's email.
        name (str, optional): User's name.
        password (str): Desired password.
    """
    email: EmailStr
    name: Optional[str] = None
    password: str

class UserLogin(BaseModel):
    """
    Pydantic schema for user login.
    Attributes:
        email (EmailStr): User's email.
        password (str): User's password.
    """
    email: EmailStr
    password: str

class UserOut(BaseModel):
    """
    Pydantic schema for user response.
    Attributes:
        id (int): User ID.
        email (str): Email.
        name (str, optional): User's name.
        created_at (datetime): Account creation date.
    """
    id: int
    email: str
    name: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    """
    Pydantic schema for user profile, matching the frontend interface.
    Attributes:
        id (str): User ID.
        email (str): User's email.
        name (str, optional): User's name.
        created_at (str): Account creation date as ISO string.
        trial_active (bool): Whether the trial is active.
        trial_expires_at (str, optional): When the trial expires as ISO string.
        subscription_active (bool): Whether the paid subscription is active.
        subscription_plan (str, optional): The subscription plan type.
        subscription_expires_at (str, optional): When the subscription expires as ISO string.
        upload_count (int): Number of files uploaded.
        max_uploads (int): Maximum allowed uploads based on plan.
        remaining_uploads (int): Number of uploads remaining (max_uploads - upload_count).
    """
    id: str
    email: str
    name: Optional[str] = None
    created_at: str
    trial_active: bool
    trial_expires_at: Optional[str] = None
    subscription_active: bool
    subscription_plan: Optional[str] = None
    subscription_expires_at: Optional[str] = None
    upload_count: int
    max_uploads: int
    remaining_uploads: int
    
    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    """
    Pydantic schema for user profile updates.
    Attributes:
        name (str, optional): User's name.
        email (EmailStr, optional): User's email.
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None
