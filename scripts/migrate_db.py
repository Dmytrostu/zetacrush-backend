"""
Database migration script to update the schema from username to email-based users.

This script will:
1. Create a backup of the current database
2. Update the database schema to match the new models
3. Migrate existing data to the new schema
"""

import os
import sys
import shutil
from datetime import datetime
import argparse
import logging
import sqlite3

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import Base, engine
from models.user import User
from models.subscription import Subscription

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def backup_database(db_path):
    """Create a backup of the database file."""
    if not os.path.exists(db_path):
        logger.warning(f"Database file {db_path} not found. Nothing to backup.")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    
    try:
        shutil.copy2(db_path, backup_path)
        logger.info(f"Database backed up to {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to backup database: {str(e)}")
        return False

def get_db_path():
    """Get the database path from the DATABASE_URL environment variable."""
    from core.config import DATABASE_URL
    
    # Extract path from SQLite URL
    if DATABASE_URL.startswith("sqlite:///"):
        return DATABASE_URL[10:]
    else:
        logger.error(f"Unsupported database URL: {DATABASE_URL}")
        return None

def drop_and_recreate_tables():
    """Drop all tables and recreate them with the new schema."""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Dropped all tables")
        
        Base.metadata.create_all(bind=engine)
        logger.info("Created new tables with updated schema")
        return True
    except Exception as e:
        logger.error(f"Failed to recreate tables: {str(e)}")
        return False

def migrate_data(db_path):
    """Migrate data from old schema to new schema."""
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if old tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone() is None:
            logger.info("No users table found, no data to migrate.")
            conn.close()
            return True
        
        # Create new tables if needed
        Base.metadata.create_all(bind=engine)
        
        # Get columns from existing users table
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [column[1] for column in cursor.fetchall()]
        
        # Check if we need to migrate
        if 'username' in user_columns and 'email' not in user_columns:
            logger.info("Need to migrate from username to email-based schema.")
            
            # Get all users
            cursor.execute("SELECT id, username, password FROM users")
            users = cursor.fetchall()
            
            # Get all subscriptions
            cursor.execute("SELECT id, user_id, trial_end, paid_until FROM subscriptions")
            subscriptions = cursor.fetchall()
            
            # Create new tables
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
            
            # Insert users with username as email
            for user_id, username, password in users:
                cursor.execute(
                    "INSERT INTO users (id, email, password, created_at, upload_count, max_uploads) "
                    "VALUES (?, ?, ?, datetime('now'), 0, 5)",
                    (user_id, f"{username}@example.com", password)
                )
            
            # Insert subscriptions
            for sub_id, user_id, trial_end, paid_until in subscriptions:
                # Set trial_active and subscription_active based on dates
                cursor.execute(
                    "INSERT INTO subscriptions "
                    "(id, user_id, trial_active, trial_expires_at, subscription_active, subscription_plan, subscription_expires_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        sub_id, 
                        user_id, 
                        1 if trial_end > datetime.now().isoformat() else 0, 
                        trial_end,
                        1 if paid_until > datetime.now().isoformat() else 0, 
                        "basic" if paid_until > datetime.now().isoformat() else None,
                        paid_until if paid_until > datetime.now().isoformat() else None
                    )
                )
            
            conn.commit()
            logger.info(f"Migrated {len(users)} users and {len(subscriptions)} subscriptions to new schema.")
        else:
            logger.info("Database already has the new schema or is empty.")
        
        conn.close()
        return True
    
    except Exception as e:
        logger.error(f"Failed to migrate data: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Database migration script")
    parser.add_argument("--force", action="store_true", help="Force migration without confirmation")
    args = parser.parse_args()
    
    db_path = get_db_path()
    if not db_path:
        return
    
    logger.info(f"Database path: {db_path}")
    
    if not args.force:
        confirm = input("This will update your database schema. Make sure you have a backup. Continue? (y/N): ")
        if confirm.lower() != 'y':
            logger.info("Migration cancelled by user.")
            return
    
    # Backup the database
    if backup_database(db_path):
        # Migrate data
        if migrate_data(db_path):
            logger.info("Migration completed successfully.")
        else:
            logger.error("Migration failed.")
    else:
        logger.error("Backup failed. Migration aborted.")

if __name__ == "__main__":
    main()
