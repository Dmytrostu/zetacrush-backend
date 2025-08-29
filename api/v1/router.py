from fastapi import APIRouter
from api.v1.endpoints import users, subscriptions, upload, test, cors_test, books, health

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(books.router, prefix="/books", tags=["books"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(test.router, tags=["test"])
api_router.include_router(cors_test.router, tags=["cors"])
