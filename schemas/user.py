from pydantic import BaseModel

class UserCreate(BaseModel):
    """
    Pydantic schema for user creation requests.
    Attributes:
        username (str): Desired username.
        password (str): Desired password.
    """
    username: str
    password: str

class UserOut(BaseModel):
    """
    Pydantic schema for user response.
    Attributes:
        id (int): User ID.
        username (str): Username.
    """
    id: int
    username: str
    class Config:
        orm_mode = True
