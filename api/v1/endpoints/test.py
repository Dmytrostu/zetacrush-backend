import time
import platform
import sys
import psutil
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.dependencies import get_db
from core.config import ENVIRONMENT, DEBUG

router = APIRouter()

@router.get("/test-api", summary="Test API Endpoint", description="Simple endpoint for API testing purposes.")
def test_api():
    """
    Test API endpoint to verify server and routing are working.
    Returns a simple JSON message.
    """
    return {"message": "API is working!", "status": "success"}

@router.get("/health", summary="Health Check", description="Check the health status of the API and its dependencies.")
def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Health check endpoint to verify the API and its dependencies are functioning correctly.
    
    This endpoint checks:
    1. Database connectivity
    2. System resources
    3. Application configuration
    
    Returns:
        Dict[str, Any]: Health status of various components
    """
    start_time = time.time()
    
    # Check database connection
    try:
        # Simple query to verify database connection
        db_result = db.execute("SELECT 1").fetchone()
        db_status = "healthy" if db_result else "error"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Get system information
    system_info = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": platform.platform(),
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage("/").percent,
    }
    
    # Calculate response time
    response_time = time.time() - start_time
    
    return {
        "status": "healthy",
        "environment": ENVIRONMENT,
        "debug_mode": DEBUG,
        "database": {
            "status": db_status,
            "type": "SQLite" if "sqlite" in str(db.bind.url) else str(db.bind.url).split("://")[0],
        },
        "system": system_info,
        "response_time_ms": round(response_time * 1000, 2)
    }
