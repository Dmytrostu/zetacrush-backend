from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Union, Dict, Any

logger = logging.getLogger(__name__)

async def error_handler_middleware(request: Request, call_next):
    """
    Middleware to handle exceptions and return consistent error responses.
    """
    try:
        return await call_next(request)
    except Exception as e:
        logger.exception(f"Unhandled exception in request: {request.url}")
        
        # Don't expose internal errors to the client
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )

def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler for request validation errors.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", "")
        })
    
    logger.warning(f"Validation error: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )

def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handler for database errors.
    """
    logger.error(f"Database error: {str(exc)}")
    
    # Don't expose internal database errors
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error occurred"}
    )

def not_found_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for 404 errors.
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)}
    )
