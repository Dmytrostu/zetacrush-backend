from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from jwt import DecodeError, ExpiredSignatureError
from fastapi import HTTPException
import os
from datetime import datetime, timedelta

# OAuth2 scheme for FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hashed version.
    Args:
        plain_password (str): User's plain password.
        hashed_password (str): Hashed password from DB.
    Returns:
        bool: True if password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain password for secure storage.
    Args:
        password (str): User's plain password.
    Returns:
        str: Hashed password.
    """
    return pwd_context.hash(password)


def create_jwt_token(data: dict) -> str:
    """
    Create a JWT token for authentication.
    Args:
        data (dict): Data to encode in the token (e.g., {"sub": username}).
    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    Args:
        token (str): JWT token string.
    Returns:
        dict: Decoded payload if valid.
    Raises:
        HTTPException: If token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token.")


def validate_token(token: str) -> str:
    """
    Validate and decode JWT token, returning the username.
    Args:
        token (str): JWT token string.
    Returns:
        str: Username from token payload.
    Raises:
        HTTPException: If token is invalid or expired.
    """
    payload = decode_jwt_token(token)
    username = payload.get("sub")
    if not username or not isinstance(username, str):
        raise HTTPException(status_code=401, detail="Invalid token or username.")
    username = username.strip()
    if not username.isalnum():
        raise HTTPException(status_code=400, detail="Invalid username format.")
    return username
