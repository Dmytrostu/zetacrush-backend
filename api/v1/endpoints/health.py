"""
Health check endpoints for the API.

These endpoints can be used to check the health of the API and its dependencies.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.dependencies import get_db
from core.init_db import check_database_connection
from core.database import engine
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", summary="Health check endpoint", description="Check if the API is running")
def health_check():
    """
    Health check endpoint to verify that the API is running.
    
    Returns:
        dict: Status of the API.
    """
    return {"status": "ok", "message": "API is running"}

@router.get("/db", summary="Database health check", description="Check if the database connection is working")
def db_health_check(db: Session = Depends(get_db)):
    """
    Check if the database connection is working.
    
    Args:
        db (Session, optional): SQLAlchemy session.
    
    Returns:
        dict: Database connection status.
    """
    try:
        # Try to execute a simple query
        db.execute("SELECT 1")
        
        # Get database engine information
        db_info = {
            "dialect": engine.dialect.name,
            "driver": engine.dialect.driver if hasattr(engine.dialect, 'driver') else "unknown",
        }
        
        # Get PostgreSQL version if using PostgreSQL
        if db_info["dialect"] == "postgresql":
            result = db.execute("SELECT version()")
            version = result.scalar()
            db_info["version"] = version
        
        return {
            "status": "ok", 
            "message": "Database connection is working",
            "database": db_info
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

@router.get("/readiness", summary="Readiness check", description="Check if the application is ready to serve requests")
def readiness_check(db: Session = Depends(get_db)):
    """
    Check if the application is ready to serve requests.
    
    This checks all required dependencies and services.
    
    Args:
        db (Session, optional): SQLAlchemy session.
        
    Returns:
        dict: Readiness status.
    """
    # Check database connection
    try:
        db.execute("SELECT 1")
        db_status = "ok"
        db_message = "Database connection is working"
    except Exception as e:
        db_status = "error"
        db_message = f"Database connection failed: {str(e)}"
        logger.error(f"Database readiness check failed: {str(e)}")
    
    # Check uploads directory
    import os
    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "uploads")
    if os.path.exists(uploads_dir) and os.access(uploads_dir, os.W_OK):
        uploads_status = "ok"
        uploads_message = "Uploads directory is accessible"
    else:
        uploads_status = "error"
        uploads_message = "Uploads directory is not accessible"
        logger.error(f"Uploads directory readiness check failed: {uploads_dir} not accessible")
    
    # Overall status
    overall_status = "ok" if all(s == "ok" for s in [db_status, uploads_status]) else "error"
    
    return {
        "status": overall_status,
        "database": {
            "status": db_status,
            "message": db_message
        },
        "uploads": {
            "status": uploads_status,
            "message": uploads_message
        }
    }
