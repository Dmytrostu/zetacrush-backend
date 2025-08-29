"""
Database initialization module.

This module handles the initialization of the database tables and
initial data setup when the application starts.
"""
import logging
from sqlalchemy.exc import SQLAlchemyError
from core.database import Base, engine, SessionLocal
from models.user import User
from models.subscription import Subscription
from models.book import Book

logger = logging.getLogger(__name__)

def init_database():
    """
    Initialize the database by creating all tables defined in the models.
    
    This function should be called when the application starts.
    """
    try:
        logger.info("Initializing database...")
        
        # Create all tables defined in models
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Check if we need to create any initial data
        db = SessionLocal()
        try:
            # Example: Check if any users exist, if not, this might be a fresh database
            user_count = db.query(User).count()
            if user_count == 0:
                logger.info("No users found, database appears to be empty")
            else:
                logger.info(f"Found {user_count} existing users in the database")
        finally:
            db.close()
        
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database initialization error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {str(e)}")
        return False

def check_database_connection():
    """
    Check if the database connection is working.
    
    Returns:
        bool: True if connection is successful, False otherwise.
    """
    try:
        # Try to create a session and execute a simple query
        db = SessionLocal()
        try:
            # Simple query to test connection
            db.execute("SELECT 1")
            logger.info("Database connection successful")
            return True
        finally:
            db.close()
    except SQLAlchemyError as e:
        logger.error(f"Database connection error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during database connection check: {str(e)}")
        return False
