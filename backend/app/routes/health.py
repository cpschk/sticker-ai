"""Health check endpoint"""
from fastapi import APIRouter, status
from datetime import datetime


router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint
    
    Returns the status of the API
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Sticker AI Backend"
    }
