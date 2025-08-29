from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
from dotenv import load_dotenv
from core.config import DATABASE_URL

# Import the Turso dialect to register it
import core.turso_db

load_dotenv()

logger = logging.getLogger(__name__)
logger.info(f"Using database URL: {DATABASE_URL}")
# Create engine based on database type
if DATABASE_URL.startswith("postgresql://"):
    # PostgreSQL database (preferred)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Check connection before using from pool
        pool_size=10,        # Default connection pool size
        max_overflow=20      # Allow up to 20 connections over pool_size
    )
    logger.info("Using PostgreSQL database")
elif DATABASE_URL.startswith("turso://") or DATABASE_URL.startswith("libsql://"):
    # Turso database (fallback)
    if DATABASE_URL.startswith("libsql://"):
        url = DATABASE_URL  # libsql:// format is directly supported
    else:
        # Convert turso:// to libsql:// 
        url = "libsql://" + DATABASE_URL[8:]
    
    engine = create_engine(url)
    logger.info(f"Using Turso database with URL: {url}")
else:
    # SQLite database (local development only - not recommended for production)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    logger.warning("Using SQLite database - not recommended for production")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
