from fastapi import APIRouter

router = APIRouter()

@router.get("/test-api", summary="Test API Endpoint", description="Simple endpoint for API testing purposes.")
def test_api():
    """
    Test API endpoint to verify server and routing are working.
    Returns a simple JSON message.
    """
    return {"message": "API is working!", "status": "success"}
