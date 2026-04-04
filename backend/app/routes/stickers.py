"""Sticker suggestion endpoint"""
from fastapi import APIRouter, status, HTTPException
from io import BytesIO
import base64
from PIL import Image
from app.models import (
    StickerSuggestionRequest,
    StickerSuggestionResponse,
    StickerSuggestion,
    AvatarPoseResponse
)
from app.services.text_analyzer import TextAnalyzerService
from app.services.sticker_generator import StickerGeneratorService
from app.services.emotion_detector import EmotionDetectorService
from app.services.avatar_service import AvatarPoseSelectionService
from app.services.image_manipulation import ImageWithSpeechBubble, SpeechBubbleStyle
from app.models.avatar_pose import AVATAR_POSES


router = APIRouter(prefix="/api/v1", tags=["stickers"])


@router.post(
    "/suggest-sticker",
    status_code=status.HTTP_200_OK,
    response_model=StickerSuggestionResponse
)
async def suggest_sticker(request: StickerSuggestionRequest):
    """
    Get sticker suggestions based on text with avatar pose and generated image
    
    Analyzes the provided text and returns:
    - Relevant sticker suggestions
    - Detected emotion
    - Avatar pose matching the emotion
    - Generated image with speech bubble (base64)
    
    Args:
        request: StickerSuggestionRequest with text and optional parameters
        
    Returns:
        StickerSuggestionResponse with stickers, avatar pose, and generated image
    """
    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty"
        )
    
    # Analyze text if theme not provided
    analyzer = TextAnalyzerService()
    analysis = analyzer.analyze(request.text)
    
    theme = request.theme or analysis["theme"]
    keywords = request.keywords or analysis["keywords"]
    
    # Detect emotion
    emotion_detector = EmotionDetectorService()
    emotion_result = emotion_detector.detect(request.text)
    
    # Select avatar pose based on detected emotion
    avatar_pose = None
    selected_pose = None
    
    if emotion_result.get("emotion"):
        # Use AvatarPoseSelectionService to select best pose
        service = AvatarPoseSelectionService()
        selected_pose = service.select_best_pose(
            emotion=emotion_result["emotion"],
            poses=AVATAR_POSES,
            prefer_intensity=emotion_result.get("intensity", 0.5)
        )
        
        if selected_pose:
            avatar_pose = AvatarPoseResponse(
                id=selected_pose.id,
                emotion=selected_pose.emotion,
                intensity=selected_pose.intensity,
                image_path=selected_pose.image_path,
                name=selected_pose.name,
                description=selected_pose.description
            )
    
    # Generate sticker suggestions
    generator = StickerGeneratorService()
    suggestions_data = generator.generate_suggestions(
        text=request.text,
        theme=theme,
        keywords=keywords,
        limit=5
    )
    
    suggestions = [StickerSuggestion(**s) for s in suggestions_data]
    
    # Generate image with speech bubble
    generated_image_base64 = None
    
    try:
        # Create a test image if no real avatar path exists
        # In production, you would use the actual avatar image from selected_pose.image_path
        if selected_pose:
            # Create a simple avatar image for demo purposes
            avatar_img = Image.new('RGB', (400, 300), color='lightblue')
            
            # Choose bubble style and font size based on emotion
            bubble_styles = {
                'risa': {
                    'bubble_color': (255, 255, 180),
                    'text_color': (30, 30, 30),
                },
                'sorpresa': {
                    'bubble_color': (255, 225, 245),
                    'text_color': (30, 10, 60),
                },
                'enojo': {
                    'bubble_color': (255, 220, 220),
                    'text_color': (80, 10, 10),
                },
                'tristeza': {
                    'bubble_color': (220, 235, 255),
                    'text_color': (20, 40, 80),
                },
                'confusión': {
                    'bubble_color': (235, 225, 255),
                    'text_color': (50, 20, 80),
                },
                'sarcasmo': {
                    'bubble_color': (240, 240, 240),
                    'text_color': (25, 25, 25),
                },
            }
            
            settings = bubble_styles.get(
                emotion_result["emotion"],
                {'bubble_color': (255, 255, 255), 'text_color': (20, 20, 20)}
            )
            
            intensity = emotion_result.get("intensity", 0.5)
            bubble_width_ratio = 0.82
            border_width = 4
            tail_size = 18

            if intensity >= 0.7:
                bubble_width_ratio = 0.9
                border_width = 5
                tail_size = 22
            elif intensity < 0.4:
                bubble_width_ratio = 0.75
                border_width = 3
                tail_size = 14

            font_size = 18
            if len(request.text) > 90:
                font_size = 16
            if len(request.text) > 150:
                font_size = 14
            
            style = SpeechBubbleStyle(
                bubble_color=settings['bubble_color'],
                text_color=settings['text_color'],
                border_color=(0, 0, 0),
                border_width=border_width,
                padding=18,
                corner_radius=18,
                tail_size=tail_size,
                bubble_style="comic"
            )
            
            # Add comic-style speech bubble to the generated avatar image
            result_img = ImageWithSpeechBubble.add_speech_bubble_from_image(
                image=avatar_img,
                text=request.text,
                style=style,
                bubble_position="top",
                bubble_width_ratio=bubble_width_ratio,
                font_size=font_size
            )
            
            # Convert image to base64
            buffer = BytesIO()
            result_img.save(buffer, format="PNG")
            generated_image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
    except Exception as e:
        # If image generation fails, just log it and continue
        # The response will still have the stickers and emotion data
        print(f"Warning: Image generation failed: {e}")
    
    return StickerSuggestionResponse(
        original_text=request.text,
        suggestions=suggestions,
        total_suggestions=len(suggestions),
        avatar_pose=avatar_pose,
        detected_emotion=emotion_result.get("emotion"),
        generated_image_base64=generated_image_base64
    )
