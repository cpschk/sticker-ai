"""Emotion detection endpoint"""
from fastapi import APIRouter, status, HTTPException
from app.models import EmotionDetectionRequest, EmotionDetectionResponse
from app.services.emotion_detector import EmotionDetectorService


router = APIRouter(prefix="/api/v1", tags=["emotions"])


@router.post(
    "/detect-emotion",
    status_code=status.HTTP_200_OK,
    response_model=EmotionDetectionResponse
)
async def detect_emotion(request: EmotionDetectionRequest):
    """
    Detect emotion from text
    
    Analyzes the provided text and detects the dominant emotion.
    
    Supported emotions:
    - **risa**: Laughter and happiness
    - **sarcasmo**: Sarcasm and irony
    - **enojo**: Anger and fury
    - **sorpresa**: Surprise and amazement
    - **tristeza**: Sadness and sorrow
    - **confusión**: Confusion and uncertainty
    
    Args:
        request: EmotionDetectionRequest with text to analyze
        
    Returns:
        EmotionDetectionResponse with detected emotion and intensity
        
    Example:
        ```
        {
            "text": "jajaja no puede ser increíble!!!"
        }
        ```
    """
    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty"
        )
    
    result = EmotionDetectorService.detect(request.text)
    
    return EmotionDetectionResponse(**result)
