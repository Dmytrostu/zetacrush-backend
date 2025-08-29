#!/usr/bin/env python3
"""
Database migration script to add the books table.
"""
import sys
import os
import logging
from datetime import datetime, timedelta
import uuid
import json

# Add parent directory to path to import local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from core.database import Base, engine
from models.book import Book
from models.user import User
from models.subscription import Subscription

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """
    Run the migration to create the books table.
    """
    logger.info("Starting database migration...")
    
    try:
        # Create the books table
        logger.info("Creating books table...")
        Base.metadata.create_all(bind=engine, tables=[Book.__table__])
        
        logger.info("Migration completed successfully!")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        sys.exit(1)

def seed_dummy_data():
    """
    Seed some dummy data for testing.
    """
    logger.info("Seeding dummy data...")
    
    # Create a session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if there are users
        users = db.query(User).all()
        if not users:
            logger.info("No users found. Creating test user...")
            
            # Create test user
            from utils.auth import get_password_hash
            
            user = User(
                email="test@example.com",
                name="Test User",
                password=get_password_hash("password"),
                created_at=datetime.utcnow(),
                upload_count=0,
                max_uploads=5
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create subscription
            subscription = Subscription(
                user_id=user.id,
                trial_active=True,
                trial_expires_at=datetime.utcnow() + timedelta(days=14),
                subscription_active=False,
                subscription_plan=None,
                subscription_expires_at=None
            )
            db.add(subscription)
            db.commit()
            
            logger.info(f"Created test user with ID {user.id}")
        
        # Add dummy book for first user
        user = db.query(User).first()
        if user:
            # Check if user already has books
            books = db.query(Book).filter(Book.user_id == user.id).all()
            
            if not books:
                logger.info(f"Adding dummy book for user ID {user.id}...")
                
                book_id = uuid.uuid4().hex
                
                # Sample data
                characters = [
                    {"name": "Elizabeth", "occurrences": 635},
                    {"name": "Darcy", "occurrences": 418},
                    {"name": "Jane", "occurrences": 292},
                    {"name": "Bingley", "occurrences": 257},
                    {"name": "Wickham", "occurrences": 194}
                ]
                
                synopsis = [
                    "Elizabeth felt herself growing more angry every moment; yet she tried to the utmost to speak with composure when she said: \"You are mistaken, Mr. Darcy, if you suppose that the mode of your declaration affected me in any other way, than as it spared me the concern which I might have felt in refusing you, had you behaved in a more gentlemanlike manner.\"",
                    "\"In vain I have struggled. It will not do. My feelings will not be repressed. You must allow me to tell you how ardently I admire and love you.\" Elizabeth's astonishment was beyond expression. She stared, coloured, doubted, and was silent."
                ]
                
                book = Book(
                    user_id=user.id,
                    book_id=book_id,
                    filename="pride_and_prejudice.txt",
                    file_path="/uploads/dummy_path.txt",
                    file_size=1024 * 1024,
                    file_type="txt",
                    uploaded_at=datetime.utcnow(),
                    characters=json.dumps(characters),
                    synopsis=json.dumps(synopsis),
                    easter_egg="Her father captivated by youth and beauty, and that appearance of good humour which youth and beauty generally give, had married a woman whose weak understanding and illiberal mind had very early in their marriage put an end to all real affection for her."
                )
                db.add(book)
                db.commit()
                
                logger.info(f"Added dummy book with ID {book_id}")
    
    except Exception as e:
        logger.error(f"Error seeding data: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_migration()
    
    # Check if --seed flag was passed
    if len(sys.argv) > 1 and sys.argv[1] == "--seed":
        seed_dummy_data()
