"""Data models for Sticker AI"""
from pydantic import BaseModel
from typing import List, Optional, Dict


class EmotionDetectionRequest(BaseModel):
    """Request model for emotion detection"""
    text: str


class EmotionDetectionResponse(BaseModel):
    """Response model for emotion detection"""
    emotion: Optional[str]
    intensity: float
    intensity_level: str
    confidence: float
    details: Optional[str] = None
    all_scores: Optional[Dict[str, float]] = None


class TextAnalysisRequest(BaseModel):
    """Request model for text analysis"""
    text: str


class TextAnalysisResponse(BaseModel):
    """Response model for text analysis"""
    text: str
    keywords: List[str]
    sentiment: str
    theme: str
    emotion: Optional[str] = None
    emotion_intensity: Optional[float] = None
    emotion_intensity_level: Optional[str] = None
    emotion_confidence: Optional[float] = None


class StickerSuggestionRequest(BaseModel):
    """Request model for sticker suggestions"""
    text: str
    keywords: Optional[List[str]] = None
    theme: Optional[str] = None


class StickerSuggestion(BaseModel):
    """Single sticker suggestion"""
    id: str
    name: str
    description: str
    style: str
    tags: List[str]


class AvatarPoseResponse(BaseModel):
    """Response model for avatar pose"""
    id: str
    emotion: str
    intensity: float
    image_path: str
    name: str
    description: str


class StickerSuggestionResponse(BaseModel):
    """Response model for sticker suggestions"""
    original_text: str
    suggestions: List[StickerSuggestion]
    total_suggestions: int
    avatar_pose: Optional[AvatarPoseResponse] = None
    detected_emotion: Optional[str] = None
    top_emotions: List[str] = []
    generated_image_base64: Optional[str] = None  # Image with speech bubble as base64
    generated_image_url: Optional[str] = None  # URL to generated image (if saved)
