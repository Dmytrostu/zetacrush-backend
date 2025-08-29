from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from api.v1.router import api_router
from core.config import (
    CORS_ORIGINS, 
    API_V1_PREFIX, 
    ENABLE_RATE_LIMITING,
    RATE_LIMIT_WINDOW_SECONDS,
    RATE_LIMIT_MAX_REQUESTS,
    DEBUG,
    ENVIRONMENT
)
from middleware.logging import RequestLoggingMiddleware
from middleware.rate_limit import RateLimitMiddleware
from middleware.error_handler import (
    error_handler_middleware,
    validation_exception_handler,
    database_exception_handler,
    not_found_exception_handler
)
import os
import logging
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Book Summarization API",
    description="FastAPI backend for book summarization application",
    version="1.0.0"
)

# Add middleware
# Note: Order matters! The middleware is executed in reverse order
# (last middleware added is executed first)

# 1. Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# 2. Configure rate limiting middleware (optional, based on configuration)
if ENABLE_RATE_LIMITING:
    logger.info(f"Rate limiting enabled: {RATE_LIMIT_MAX_REQUESTS} requests per {RATE_LIMIT_WINDOW_SECONDS} seconds")
    app.add_middleware(
        RateLimitMiddleware,
        window_size=RATE_LIMIT_WINDOW_SECONDS,
        max_requests=RATE_LIMIT_MAX_REQUESTS,
        exclude_paths=["/docs", "/redoc", "/openapi.json", "/static/", "/api/v1/cors-test"]
    )
else:
    logger.info("Rate limiting disabled")

# 3. Add middleware for error handling
app.middleware("http")(error_handler_middleware)

# 4. Add exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(404, not_found_exception_handler)

# 5. Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include API router with version prefix
app.include_router(api_router, prefix=API_V1_PREFIX)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoint for API information
@app.get("/")
async def root():
    """
    Root endpoint providing basic API information and links to documentation.
    """
    return {
        "app_name": "Book Summarization API",
        "version": "1.0.0",
        "documentation_urls": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "cors_test_page": "/static/cors_test.html",
        "api_prefix": API_V1_PREFIX,
        "status": "running"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Execute code when the application starts.
    """
    logger.info(f"Starting Book Summarization API in {ENVIRONMENT.upper()} mode")
    logger.info(f"API Base URL: {API_V1_PREFIX}")
    logger.info(f"Debug mode: {'Enabled' if DEBUG else 'Disabled'}")
    logger.info(f"CORS configured for origins: {', '.join(CORS_ORIGINS)}")
    
    # Initialize database
    try:
        from core.init_db import init_database, check_database_connection
        
        # First check if we can connect to the database
        if not check_database_connection():
            logger.error("Failed to connect to database. Application may not work correctly.")
        
        # Initialize database tables and data
        if init_database():
            logger.info("Database initialized successfully")
        else:
            logger.error("Failed to initialize database. Application may not work correctly.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
    
    # Ensure uploads directory exists
    uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        logger.info(f"Created uploads directory: {uploads_dir}")
    else:
        logger.info(f"Uploads directory exists: {uploads_dir}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Execute code when the application shuts down.
    """
    logger.info("Shutting down Book Summarization API")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[os.path.dirname(os.path.abspath(__file__))],
        reload_excludes=[
            "*/.git/*",
            "*/__pycache__/*",
            "*.pyc",
            "*/.pytest_cache/*",
            "*/.vscode/*",
            "*/.idea/*"
        ],
        reload_delay=1,
        reload_includes=["*.py", "*.html", "*.css", "*.js"]
    )