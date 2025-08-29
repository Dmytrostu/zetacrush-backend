"""
Configuration settings for the application.

This module defines configuration variables such as CORS origins,
database connection details, JWT secrets, etc.
"""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
DEBUG: bool = ENVIRONMENT == "development"

# CORS Configuration
CORS_ORIGINS: List[str] = [
    "*",  # Allow requests from any origin
]

# JWT Configuration
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "your-secret-key-for-development-only"))
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Database Configuration
DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/zetacrush")
TURSO_AUTH_TOKEN: str = os.getenv("TURSO_AUTH_TOKEN", "")

# API Configuration
API_V1_PREFIX: str = "/api/v1"

# Upload Configuration
UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "./uploads")
ALLOWED_EXTENSIONS: List[str] = ["pdf", "txt", "doc", "docx"]
MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB

# Security Configuration
PASSWORD_BCRYPT_ROUNDS: int = 12

# Rate Limiting
ENABLE_RATE_LIMITING: bool = os.getenv("ENABLE_RATE_LIMITING", "false").lower() == "true"
RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
RATE_LIMIT_MAX_REQUESTS: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "30"))
