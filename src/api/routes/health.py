from fastapi import APIRouter


# Create a router for health check endpoints
router = APIRouter()


@router.get("/health")
def health_check():
    """
    Simple endpoint to confirm the API is running.
    """
    return {"status": "ok"}