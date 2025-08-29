"""
Script to migrate data from SQLite to PostgreSQL.

This script will:
1. Create all tables in PostgreSQL
2. Export data from SQLite
3. Import data into PostgreSQL
"""
import os
import sys
import csv
import tempfile
import argparse
from sqlalchemy import create_engine, MetaData, Table, inspect, text

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.database import Base, engine as target_engine
from models.user import User
from models.subscription import Subscription
from models.book import Book

def get_sqlite_engine(sqlite_url):
    """Create SQLAlchemy engine for SQLite."""
    from sqlalchemy import create_engine
    return create_engine(sqlite_url)

def migrate_data(sqlite_url, tables_to_migrate=None):
    """
    Migrate data from SQLite to PostgreSQL.
    
    Args:
        sqlite_url: SQLite database URL
        tables_to_migrate: List of table names to migrate (None for all)
    """
    # Source SQLite engine
    source_engine = get_sqlite_engine(sqlite_url)
    source_metadata = MetaData()
    source_metadata.reflect(bind=source_engine)
    
    # Create all tables in PostgreSQL
    Base.metadata.create_all(bind=target_engine)
    
    # Get list of tables to migrate
    if not tables_to_migrate:
        tables_to_migrate = source_metadata.tables.keys()
    
    # For each table
    for table_name in tables_to_migrate:
        print(f"Migrating table: {table_name}")
        
        # Get table objects
        source_table = Table(table_name, source_metadata, autoload_with=source_engine)
        
        # Check if table exists in target
        if not inspect(target_engine).has_table(table_name):
            print(f"Table {table_name} does not exist in target database. Skipping.")
            continue
            
        # Extract data from source
        source_conn = source_engine.connect()
        result = source_conn.execute(source_table.select())
        rows = result.fetchall()
        
        if not rows:
            print(f"No data in table {table_name}. Skipping.")
            continue
            
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w+', newline='', delete=False) as temp_file:
            # Get column names
            columns = [col.name for col in source_table.columns]
            
            # Write CSV
            writer = csv.DictWriter(temp_file, fieldnames=columns)
            writer.writeheader()
            
            for row in rows:
                # Convert row to dict
                row_dict = {columns[i]: value for i, value in enumerate(row)}
                writer.writerow(row_dict)
                
            temp_file_path = temp_file.name
        
        # Import data to target
        target_conn = target_engine.connect()
        try:
            # Prepare column list
            column_list = ', '.join(columns)
            value_list = ', '.join([f':{col}' for col in columns])
            
            # Build INSERT statement
            insert_stmt = f"INSERT INTO {table_name} ({column_list}) VALUES ({value_list})"
            
            # Read CSV and execute insert for each row
            with open(temp_file_path, 'r', newline='') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    target_conn.execute(text(insert_stmt), row)
            
            target_conn.commit()
            print(f"Successfully migrated {len(rows)} rows from table {table_name}")
            
        except Exception as e:
            target_conn.rollback()
            print(f"Error migrating table {table_name}: {str(e)}")
        
        finally:
            target_conn.close()
            
        # Remove temporary file
        os.unlink(temp_file_path)
            
    print("Migration completed!")

def main():
    """Main function to run migration."""
    parser = argparse.ArgumentParser(description='Migrate data from SQLite to PostgreSQL')
    parser.add_argument('--sqlite-url', type=str, default='sqlite:///./app.db',
                        help='SQLite database URL (default: sqlite:///./app.db)')
    parser.add_argument('--tables', type=str, nargs='+',
                        help='Tables to migrate (default: all)')
    
    args = parser.parse_args()
    
    migrate_data(args.sqlite_url, args.tables)

if __name__ == '__main__':
    main()
