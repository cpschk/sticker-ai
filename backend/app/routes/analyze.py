"""Text analysis endpoint"""
from fastapi import APIRouter, status, HTTPException
from app.models import TextAnalysisRequest, TextAnalysisResponse
from app.services.text_analyzer import TextAnalyzerService
from app.services.emotion_detector import EmotionDetectorService


router = APIRouter(prefix="/api/v1", tags=["analysis"])


@router.post(
    "/analyze-text",
    status_code=status.HTTP_200_OK,
    response_model=TextAnalysisResponse
)
async def analyze_text(request: TextAnalysisRequest):
    """
    Analyze provided text
    
    Extracts keywords, sentiment, theme, and emotion from the input text.
    
    Args:
        request: TextAnalysisRequest with text to analyze
        
    Returns:
        TextAnalysisResponse with analysis results including emotion detection
    """
    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty"
        )
    
    # Text analysis
    analyzer = TextAnalyzerService()
    analysis_result = analyzer.analyze(request.text)
    
    # Emotion detection
    emotion_detector = EmotionDetectorService()
    emotion_result = emotion_detector.detect(request.text)
    
    # Combine results
    combined_result = {
        **analysis_result,
        "emotion": emotion_result.get("emotion"),
        "emotion_intensity": emotion_result.get("intensity"),
        "emotion_intensity_level": emotion_result.get("intensity_level"),
        "emotion_confidence": emotion_result.get("confidence"),
    }
    
    return TextAnalysisResponse(**combined_result)
