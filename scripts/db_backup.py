"""
PostgreSQL database backup and restore script.

This script provides utilities for backing up and restoring the PostgreSQL database.
It can be used for creating regular backups and restoring from them if needed.
"""
import os
import sys
import argparse
import logging
import subprocess
from datetime import datetime
import re
from urllib.parse import urlparse

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.config import DATABASE_URL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def parse_db_url(url):
    """Parse database URL into components."""
    if not url.startswith('postgresql://'):
        logger.error("Only PostgreSQL URLs are supported")
        return None
    
    parsed = urlparse(url)
    username = parsed.username
    password = parsed.password
    hostname = parsed.hostname
    port = parsed.port or 5432
    database = parsed.path.lstrip('/')
    
    return {
        'username': username,
        'password': password,
        'hostname': hostname,
        'port': port,
        'database': database
    }

def backup_database(output_file=None, db_url=None):
    """
    Backup the PostgreSQL database to a file.
    
    Args:
        output_file (str, optional): Output file path. If not provided, a timestamped file is created.
        db_url (str, optional): Database URL. If not provided, it's taken from environment.
    
    Returns:
        str: Path to the backup file if successful, None otherwise.
    """
    url = db_url or DATABASE_URL
    db_info = parse_db_url(url)
    
    if not db_info:
        return None
    
    # Create backup directory if it doesn't exist
    backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate backup filename if not provided
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(backup_dir, f"{db_info['database']}_{timestamp}.sql")
    
    # Set environment variables for pg_dump
    env = os.environ.copy()
    env['PGPASSWORD'] = db_info['password']
    
    try:
        # Build pg_dump command
        cmd = [
            'pg_dump',
            '-h', db_info['hostname'],
            '-p', str(db_info['port']),
            '-U', db_info['username'],
            '-d', db_info['database'],
            '-f', output_file,
            '--clean'
        ]
        
        logger.info(f"Running backup command: {' '.join(cmd)}")
        
        # Execute pg_dump
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Backup failed: {stderr.decode()}")
            return None
        
        logger.info(f"Backup completed successfully: {output_file}")
        return output_file
    
    except Exception as e:
        logger.error(f"Backup error: {str(e)}")
        return None

def restore_database(backup_file, db_url=None):
    """
    Restore the PostgreSQL database from a backup file.
    
    Args:
        backup_file (str): Path to the backup file.
        db_url (str, optional): Database URL. If not provided, it's taken from environment.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    url = db_url or DATABASE_URL
    db_info = parse_db_url(url)
    
    if not db_info:
        return False
    
    # Check if backup file exists
    if not os.path.exists(backup_file):
        logger.error(f"Backup file not found: {backup_file}")
        return False
    
    # Set environment variables for psql
    env = os.environ.copy()
    env['PGPASSWORD'] = db_info['password']
    
    try:
        # Build psql command
        cmd = [
            'psql',
            '-h', db_info['hostname'],
            '-p', str(db_info['port']),
            '-U', db_info['username'],
            '-d', db_info['database'],
            '-f', backup_file
        ]
        
        logger.info(f"Running restore command: {' '.join(cmd)}")
        
        # Execute psql
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Restore failed: {stderr.decode()}")
            return False
        
        logger.info("Restore completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Restore error: {str(e)}")
        return False

def list_backups():
    """
    List all available backups.
    
    Returns:
        list: List of backup files with timestamps.
    """
    backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backups")
    
    if not os.path.exists(backup_dir):
        logger.info(f"Backup directory doesn't exist: {backup_dir}")
        return []
    
    # Get all .sql files
    backups = []
    for filename in os.listdir(backup_dir):
        if filename.endswith('.sql'):
            filepath = os.path.join(backup_dir, filename)
            timestamp = os.path.getmtime(filepath)
            date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            
            # Try to extract database name and backup timestamp from filename
            match = re.match(r'(.+)_(\d{8}_\d{6})\.sql', filename)
            db_name = match.group(1) if match else "unknown"
            
            backups.append({
                'filename': filename,
                'path': filepath,
                'date': date,
                'size': os.path.getsize(filepath),
                'database': db_name
            })
    
    # Sort by date, newest first
    backups.sort(key=lambda x: x['date'], reverse=True)
    return backups

def main():
    parser = argparse.ArgumentParser(description="PostgreSQL database backup and restore tool")
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Backup the database')
    backup_parser.add_argument('--output', type=str, help='Output file path')
    backup_parser.add_argument('--db-url', type=str, help='Database URL (if not using environment)')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore the database from a backup')
    restore_parser.add_argument('file', type=str, help='Backup file path')
    restore_parser.add_argument('--db-url', type=str, help='Database URL (if not using environment)')
    
    # List command
    subparsers.add_parser('list', help='List all available backups')
    
    args = parser.parse_args()
    
    if args.command == 'backup':
        backup_database(args.output, args.db_url)
    elif args.command == 'restore':
        confirm = input("This will overwrite your current database. Are you sure? (y/N): ")
        if confirm.lower() == 'y':
            restore_database(args.file, args.db_url)
        else:
            logger.info("Restore cancelled")
    elif args.command == 'list':
        backups = list_backups()
        if backups:
            print("\nAvailable backups:")
            print(f"{'Filename':<40} {'Database':<15} {'Date':<20} {'Size':<10}")
            print("-" * 85)
            for backup in backups:
                size_str = f"{backup['size'] / 1024:.1f} KB"
                print(f"{backup['filename']:<40} {backup['database']:<15} {backup['date']:<20} {size_str:<10}")
            print()
        else:
            print("\nNo backups found\n")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
