"""
Endpoint for testing CORS configuration.

This module contains endpoints that can be used to test if CORS is properly configured.
"""
from fastapi import APIRouter, Request, Depends
from core.config import CORS_ORIGINS
import platform
import sys

router = APIRouter()

@router.get("/cors-test")
async def test_cors(request: Request):
    """
    Test endpoint to verify CORS configuration.
    
    This endpoint returns information about the request including origin headers
    to help diagnose CORS issues.
    
    Returns:
        dict: A dictionary containing request information and a success message.
    """
    return {
        "message": "CORS test successful",
        "origin": request.headers.get("origin"),
        "host": request.headers.get("host"),
        "method": request.method,
        "headers": {
            key: value for key, value in request.headers.items()
            if key.lower() in ["origin", "referer", "host", "user-agent", "accept", "accept-language"]
        }
    }

@router.get("/cors-config")
async def get_cors_config():
    """
    Get the current CORS configuration.
    
    Returns information about the configured CORS origins and system information.
    
    Returns:
        dict: A dictionary containing CORS configuration and system information.
    """
    return {
        "cors_origins": CORS_ORIGINS,
        "system_info": {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": platform.platform(),
            "system": platform.system(),
            "test_html_page": "/static/cors_test.html"
        },
        "instructions": "To test CORS functionality, open the test HTML page in a browser and use the buttons to make requests to the API."
    }

@router.options("/cors-test")
async def options_cors_test():
    """
    Handle OPTIONS requests for CORS preflight.
    
    This endpoint is automatically handled by the CORS middleware but is included 
    here for demonstration purposes.
    
    Returns:
        dict: A dictionary containing a success message.
    """
    return {"message": "CORS preflight request successful"}
