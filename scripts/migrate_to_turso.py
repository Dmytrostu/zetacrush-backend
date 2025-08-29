"""
Script to migrate data from SQLite to Turso.

This script:
1. Reads all tables from SQLite
2. Creates the same tables in Turso
3. Copies all data from SQLite to Turso
"""
import os
import sys
import argparse
import sqlite3
import logging
import libsql_client

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.database import Base, engine
from models.user import User
from models.subscription import Subscription
from models.book import Book

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_schema_from_sqlite(sqlite_path):
    """Get the schema definition from SQLite database."""
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    schema_sql = []
    
    for table in tables:
        # Get CREATE TABLE statement
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
        create_stmt = cursor.fetchone()[0]
        schema_sql.append(create_stmt)
        
        # Get indices
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='{table}' AND sql IS NOT NULL")
        for row in cursor.fetchall():
            schema_sql.append(row[0])
    
    conn.close()
    return schema_sql

def get_data_from_sqlite(sqlite_path):
    """Get all data from SQLite tables."""
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    data = {}
    
    for table in tables:
        # Get all rows
        cursor.execute(f"SELECT * FROM {table}")
        rows = [dict(row) for row in cursor.fetchall()]
        
        # Get column names and types
        cursor.execute(f"PRAGMA table_info({table})")
        columns = {row['name']: row['type'] for row in cursor.fetchall()}
        
        data[table] = {
            'columns': columns,
            'rows': rows
        }
    
    conn.close()
    return data

def migrate_to_turso(sqlite_path, turso_url, auth_token):
    """Migrate data from SQLite to Turso."""
    logger.info(f"Migrating from {sqlite_path} to Turso at {turso_url}")
    
    # Get schema and data from SQLite
    schema_sql = get_schema_from_sqlite(sqlite_path)
    data = get_data_from_sqlite(sqlite_path)
    
    # Format the Turso URL correctly
    if not turso_url.startswith('https://'):
        # If the URL is in the format "libsql://hostname" or "turso://hostname"
        # convert it to https://hostname
        url_parts = turso_url.split('://')
        if len(url_parts) > 1:
            turso_url = f"https://{url_parts[1]}"
    
    # Connect to Turso
    client = libsql_client.create_client(url=turso_url, auth_token=auth_token)
    
    # Create schema in Turso
    logger.info("Creating schema in Turso")
    for sql in schema_sql:
        try:
            client.execute(sql)
        except Exception as e:
            logger.error(f"Error creating schema: {e}")
            logger.error(f"SQL: {sql}")
    
    # Insert data into Turso
    logger.info("Inserting data into Turso")
    for table, table_data in data.items():
        rows = table_data['rows']
        if not rows:
            logger.info(f"No data for table {table}")
            continue
            
        columns = list(rows[0].keys())
        placeholders = ", ".join(["?" for _ in columns])
        column_names = ", ".join(columns)
        
        insert_sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
        
        for row in rows:
            values = [row[col] for col in columns]
            try:
                client.execute(insert_sql, values)
            except Exception as e:
                logger.error(f"Error inserting data: {e}")
                logger.error(f"SQL: {insert_sql}")
                logger.error(f"Values: {values}")
    
    logger.info("Migration completed successfully")
    client.close()

def main():
    """Main function to run migration."""
    parser = argparse.ArgumentParser(description='Migrate data from SQLite to Turso')
    parser.add_argument('--sqlite-path', type=str, default='app.db',
                        help='Path to SQLite database file')
    parser.add_argument('--turso-url', type=str, required=True,
                        help='Turso database URL (https://[database].turso.io)')
    parser.add_argument('--auth-token', type=str, required=True,
                        help='Turso authentication token')
    
    args = parser.parse_args()
    
    migrate_to_turso(args.sqlite_path, args.turso_url, args.auth_token)

if __name__ == '__main__':
    main()
