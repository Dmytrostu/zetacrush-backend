from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from jwt import DecodeError, ExpiredSignatureError
from fastapi import HTTPException, Depends
import os
import logging
from datetime import datetime, timedelta
from core.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES

logger = logging.getLogger(__name__)

# OAuth2 scheme for FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/users/login")

# Password hashing context
# Using bcrypt_sha256 instead of bcrypt to avoid compatibility issues
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

# JWT settings - using config values
SECRET_KEY = JWT_SECRET_KEY
ALGORITHM = JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = JWT_ACCESS_TOKEN_EXPIRE_MINUTES


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hashed version.
    Args:
        plain_password (str): User's plain password.
        hashed_password (str): Hashed password from DB.
    Returns:
        bool: True if password matches, False otherwise.
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Password verification error: {str(e)}")
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using the configured password context.
    Args:
        password (str): Plain password to hash.
    Returns:
        str: Hashed password.
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Password hashing error: {str(e)}")
        raise


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


def validate_token(token: str) -> dict:
    """
    Validate and decode JWT token, returning the payload.
    Args:
        token (str): JWT token string.
    Returns:
        dict: Token payload containing user info.
    Raises:
        HTTPException: If token is invalid or expired.
    """
    payload = decode_jwt_token(token)
    email = payload.get("sub")
    user_id = payload.get("user_id")
    
    if not email or not isinstance(email, str):
        raise HTTPException(status_code=401, detail="Invalid token or email.")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token: missing user ID.")
        
    return {"email": email, "user_id": user_id}


async def get_current_user_email(token: str = Depends(oauth2_scheme)) -> str:
    """
    Dependency to get current user's email from token.
    
    Args:
        token (str): JWT token from Authorization header.
        
    Returns:
        str: User's email.
    """
    user_data = validate_token(token)
    return user_data["email"]


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """
    Dependency to get current user's ID from token.
    
    Args:
        token (str): JWT token from Authorization header.
        
    Returns:
        int: User's ID.
    """
    user_data = validate_token(token)
    return user_data["user_id"]
