"""
Turso (libSQL) database connection adapter for SQLAlchemy.
This adapter allows using Turso's libSQL with your SQLAlchemy models.
"""
import os
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import libsql_client
from sqlalchemy.dialects.sqlite.pysqlite import SQLiteDialect_pysqlite
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.engine.interfaces import Dialect, ExecutionContext
from sqlalchemy.engine.url import URL
from sqlalchemy.pool.impl import SingletonThreadPool
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine import create_engine

logger = logging.getLogger(__name__)

class TursoDialect(SQLiteDialect_pysqlite):
    """Turso dialect for SQLAlchemy."""
    name = "turso"
    driver = "libsql"

    @classmethod
    def dbapi(cls):
        return TursoDBAPI()

    def create_connect_args(self, url):
        url_str = str(url)
        logger.info(f"Creating connection arguments for URL: {url_str}")
        
        if url_str.startswith('turso://'):
            parsed = urlparse(url_str.replace('turso://', ''))
        elif url_str.startswith('libsql://'):
            parsed = urlparse(url_str.replace('libsql://', ''))
        else:
            parsed = urlparse(url_str)
            
        # For local SQLite-compatible database
        if not parsed.hostname:
            database_path = parsed.path.lstrip("/") if parsed.path else ":memory:"
            logger.info(f"Using local SQLite-compatible database: {database_path}")
            return [], {"database": database_path}
        
        # For remote Turso database
        server_url = f"https://{parsed.hostname}{':'+str(parsed.port) if parsed.port else ''}"
        database = parsed.path.lstrip("/") if parsed.path else "main"
        
        connect_args = {
            "url": server_url,
            "database": database
        }
        
        # Get auth token from URL username, password or environment
        auth_token = None
        if parsed.username:
            auth_token = parsed.username
        elif os.environ.get("TURSO_AUTH_TOKEN"):
            auth_token = os.environ.get("TURSO_AUTH_TOKEN")
            
        if auth_token:
            connect_args["auth_token"] = auth_token
        else:
            logger.warning("No auth_token found for Turso database. Connection might fail.")
            
        logger.info(f"Using remote Turso database at {server_url}")
        return [], connect_args

    def do_ping(self, dbapi_connection):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
        except Exception as e:
            logger.error(f"Error pinging Turso database: {e}")
            return False
        finally:
            cursor.close()

# This is where the actual connection to Turso happens
class TursoDBAPI:
    """DBAPI implementation for Turso."""
    
    paramstyle = "qmark"
    threadsafety = 1
    
    # Set sqlite version to a recent version to satisfy SQLAlchemy requirements
    sqlite_version = "3.35.0"
    sqlite_version_info = (3, 35, 0)
    
    def __init__(self):
        self.Warning = Warning
        self.Error = Exception
        self.InterfaceError = Exception
        self.DatabaseError = Exception
        self.OperationalError = Exception
        self.IntegrityError = Exception
        self.DataError = Exception
        self.ProgrammingError = Exception
        self.NotSupportedError = Exception

    def connect(self, *args, **kwargs):
        """Create a connection to the libSQL database."""
        database = kwargs.get("database", ":memory:")
        # url = kwargs.get("url")
        print('**********************************\ndatabase-url: ', database, ' database: ', database)
        auth_token = kwargs.get("auth_token")
        
        try:
            if database:
                # Get auth token from environment if not provided
                if not auth_token:
                    auth_token = os.environ.get("TURSO_AUTH_TOKEN")
                    if not auth_token:
                        logger.warning("No auth_token provided for Turso database. Connection might fail.")
                
                # Remote Turso connection
                client = libsql_client.create_client(url=database, auth_token=auth_token)
                logger.info(f"Connected to remote Turso database at {database}")
            else:
                # Local SQLite-compatible connection
                client = libsql_client.create_client(f"file:{database}")
                logger.info(f"Connected to local SQLite database at {database}")
            
            return TursoConnection(client)
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise

class TursoConnection:
    """Connection wrapper for Turso."""
    
    def __init__(self, client):
        self.client = client
        self.closed = False
        self._in_transaction = False

    def close(self):
        """Close the connection."""
        self.closed = True
        try:
            self.client.close()
        except Exception as e:
            logger.error(f"Error closing connection: {e}")
    
    def commit(self):
        """Commit the transaction."""
        # Turso automatically commits after each statement
        # unless explicitly in a transaction
        pass
    
    def rollback(self):
        """Rollback the transaction."""
        # Try to execute ROLLBACK if in transaction
        if self._in_transaction:
            try:
                self.client.execute("ROLLBACK")
                self._in_transaction = False
            except Exception as e:
                logger.error(f"Error during rollback: {e}")
    
    def cursor(self):
        """Create a cursor."""
        return TursoCursor(self.client)

class TursoCursor:
    """Cursor wrapper for Turso."""
    
    def __init__(self, client):
        self.client = client
        self.arraysize = 1
        self._rows = None
        self._rowcount = -1
        self._lastrowid = None
        self.description = None
    
    def close(self):
        """Close the cursor."""
        self._rows = None
    
    def execute(self, operation, parameters=None):
        """Execute a SQL statement."""
        if parameters is None:
            parameters = []
        
        try:
            result = self.client.execute(operation, parameters)
            
            # Set description based on column names if available
            if result.columns:
                self.description = [(name, None, None, None, None, None, None) for name in result.columns]
            else:
                self.description = None
                
            # Store rows for fetchone/fetchmany/fetchall
            self._rows = result.rows
            self._rowcount = len(result.rows)
            self._lastrowid = result.last_insert_rowid
            
            return self
        except Exception as e:
            logger.error(f"Error executing SQL: {operation} with params {parameters}")
            logger.error(f"Exception: {e}")
            raise
    
    def executemany(self, operation, seq_of_parameters):
        """Execute multiple SQL statements."""
        rowcount = 0
        for parameters in seq_of_parameters:
            self.execute(operation, parameters)
            rowcount += self._rowcount
        self._rowcount = rowcount
        return self
    
    def fetchone(self):
        """Fetch one row."""
        if not self._rows:
            return None
        row = self._rows[0]
        self._rows = self._rows[1:]
        return row
    
    def fetchmany(self, size=None):
        """Fetch many rows."""
        if size is None:
            size = self.arraysize
        if not self._rows:
            return []
        rows = self._rows[:size]
        self._rows = self._rows[size:]
        return rows
    
    def fetchall(self):
        """Fetch all rows."""
        if not self._rows:
            return []
        rows = self._rows
        self._rows = []
        return rows
    
    @property
    def rowcount(self):
        """Number of rows affected."""
        return self._rowcount
    
    @property
    def lastrowid(self):
        """Last inserted row ID."""
        return self._lastrowid

# Register the dialect
from sqlalchemy.dialects import registry
registry.register("turso", "core.turso_db", "TursoDialect")
registry.register("libsql", "core.turso_db", "TursoDialect")
