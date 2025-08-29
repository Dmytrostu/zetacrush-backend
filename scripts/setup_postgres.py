"""
Setup PostgreSQL database for the application.

This script:
1. Connects to PostgreSQL 
2. Creates the database if it doesn't exist
3. Creates all tables defined in the models
4. Optionally imports data from SQLite or another source
"""
import os
import sys
import argparse
import logging
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import create_engine

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def setup_postgres(db_url, drop_existing=False, import_from_sqlite=False, sqlite_path=None):
    """
    Set up PostgreSQL database.
    
    Args:
        db_url: PostgreSQL database URL
        drop_existing: Whether to drop existing database (DANGER!)
        import_from_sqlite: Whether to import data from SQLite
        sqlite_path: Path to SQLite database file
    """
    from core.database import Base
    from models.user import User
    from models.subscription import Subscription
    from models.book import Book
    
    logger.info(f"Setting up PostgreSQL database at {db_url}")
    
    # Extract the database name from the URL
    db_name = db_url.split("/")[-1]
    
    # Create a connection to PostgreSQL server (without specific database)
    engine_url = "/".join(db_url.split("/")[:-1] + ["postgres"])
    engine = create_engine(engine_url)
    
    # Check if database exists
    if database_exists(db_url):
        if drop_existing:
            logger.warning(f"Dropping existing database {db_name}")
            
            # Disconnect all users first
            with engine.connect() as conn:
                conn.execute(f"SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{db_name}' AND pid <> pg_backend_pid();")
            
            # Drop the database
            with engine.connect() as conn:
                conn.execution_options(isolation_level="AUTOCOMMIT").execute(f"DROP DATABASE {db_name}")
            
            # Recreate the database
            create_database(db_url)
            logger.info(f"Database {db_name} recreated")
        else:
            logger.info(f"Database {db_name} already exists")
    else:
        # Create the database
        create_database(db_url)
        logger.info(f"Database {db_name} created")
    
    # Create engine for the specific database
    db_engine = create_engine(db_url)
    
    # Create all tables
    Base.metadata.create_all(db_engine)
    logger.info("All tables created")
    
    # Import data from SQLite if requested
    if import_from_sqlite and sqlite_path:
        import sqlite3
        from sqlalchemy.orm import sessionmaker
        
        # Create session for PostgreSQL
        Session = sessionmaker(bind=db_engine)
        session = Session()
        
        # Connect to SQLite
        logger.info(f"Importing data from SQLite database at {sqlite_path}")
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        # Get all tables
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in sqlite_cursor.fetchall()]
        
        for table in tables:
            # Get number of rows
            sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = sqlite_cursor.fetchone()[0]
            
            # Get all rows
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            
            logger.info(f"Table {table}: {len(rows)} rows to import")
            
            # For each table, handle import differently
            if table == "users":
                for row in rows:
                    row_dict = dict(row)
                    user = User(
                        id=row_dict.get("id"),
                        email=row_dict.get("email"),
                        name=row_dict.get("name"),
                        password=row_dict.get("password"),
                        created_at=row_dict.get("created_at"),
                        upload_count=row_dict.get("upload_count", 0),
                        max_uploads=row_dict.get("max_uploads", 5)
                    )
                    session.add(user)
                
            elif table == "subscriptions":
                for row in rows:
                    row_dict = dict(row)
                    subscription = Subscription(
                        id=row_dict.get("id"),
                        user_id=row_dict.get("user_id"),
                        trial_active=row_dict.get("trial_active", False),
                        trial_expires_at=row_dict.get("trial_expires_at"),
                        subscription_active=row_dict.get("subscription_active", False),
                        subscription_plan=row_dict.get("subscription_plan"),
                        subscription_expires_at=row_dict.get("subscription_expires_at")
                    )
                    session.add(subscription)
                
            elif table == "books":
                for row in rows:
                    row_dict = dict(row)
                    book = Book(
                        id=row_dict.get("id"),
                        user_id=row_dict.get("user_id"),
                        title=row_dict.get("title"),
                        author=row_dict.get("author"),
                        file_path=row_dict.get("file_path"),
                        file_size=row_dict.get("file_size"),
                        file_type=row_dict.get("file_type"),
                        created_at=row_dict.get("created_at"),
                        summary=row_dict.get("summary"),
                        characters=row_dict.get("characters"),
                        easter_eggs=row_dict.get("easter_eggs")
                    )
                    session.add(book)
            
            session.commit()
        
        sqlite_conn.close()
        logger.info("Data import completed")
    
    logger.info("PostgreSQL database setup completed successfully")

def main():
    parser = argparse.ArgumentParser(description="Set up PostgreSQL database")
    parser.add_argument("--db-url", type=str, help="PostgreSQL database URL (default: from environment)")
    parser.add_argument("--drop-existing", action="store_true", help="Drop existing database (DANGER!)")
    parser.add_argument("--import-sqlite", action="store_true", help="Import data from SQLite")
    parser.add_argument("--sqlite-path", type=str, default="app.db", help="Path to SQLite database file")
    
    args = parser.parse_args()
    
    # Get database URL
    from core.config import DATABASE_URL
    db_url = args.db_url or DATABASE_URL
    
    if not db_url.startswith("postgresql://"):
        logger.error("Database URL must start with postgresql://")
        sys.exit(1)
    
    setup_postgres(
        db_url=db_url,
        drop_existing=args.drop_existing,
        import_from_sqlite=args.import_sqlite,
        sqlite_path=args.sqlite_path
    )

if __name__ == "__main__":
    main()
