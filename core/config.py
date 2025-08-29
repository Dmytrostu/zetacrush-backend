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
# Determine if we're in a serverless environment (AWS Lambda, Vercel, etc.)
IS_SERVERLESS: bool = os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None or os.environ.get("VERCEL") is not None or os.environ.get("FUNCTION_TARGET") is not None

# Use /tmp directory for serverless environments, otherwise use configured directory
UPLOAD_FOLDER: str = "/tmp/uploads" if IS_SERVERLESS else os.getenv("UPLOAD_FOLDER", "./uploads")

# In Vercel, we can only use /tmp for file operations
IS_VERCEL: bool = os.environ.get("VERCEL") is not None
ALLOWED_EXTENSIONS: List[str] = ["pdf", "txt", "doc", "docx"]
MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB

# Google Drive Settings
USE_CLOUD_STORAGE: bool = os.getenv("USE_CLOUD_STORAGE", "false").lower() == "true"
GOOGLE_DRIVE_FOLDER_ID: str = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
GOOGLE_CREDENTIALS_FILE: str = os.getenv("GOOGLE_CREDENTIALS_FILE", "")

# Security Configuration
PASSWORD_BCRYPT_ROUNDS: int = 12

# Rate Limiting
ENABLE_RATE_LIMITING: bool = os.getenv("ENABLE_RATE_LIMITING", "false").lower() == "true"
RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
RATE_LIMIT_MAX_REQUESTS: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "30"))
