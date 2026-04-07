"""Sticker suggestion and image generation endpoints"""
from fastapi import APIRouter, status, HTTPException
from io import BytesIO
from pathlib import Path
from pydantic import BaseModel
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
from app.services.image_manipulation import generate_sticker, generate_placeholder_avatar
from app.models.avatar_pose import AVATAR_POSES


router = APIRouter(prefix="/api/v1", tags=["stickers"])

# Imagen base temporal — se reemplazará con el sistema de poses/avatares
_BASE_IMAGE_PATH = Path(__file__).parent.parent.parent / "sticker_image_test.png"


# ── /suggest-sticker ──────────────────────────────────────────────────────────

@router.post(
    "/suggest-sticker",
    status_code=status.HTTP_200_OK,
    response_model=StickerSuggestionResponse
)
async def suggest_sticker(request: StickerSuggestionRequest):
    """
    Analiza el texto y devuelve emoción + sugerencias.
    Ya NO genera la imagen — eso lo hace /generate-image bajo demanda.
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Text cannot be empty")

    analysis = TextAnalyzerService().analyze(request.text)
    theme    = request.theme    or analysis["theme"]
    keywords = request.keywords or analysis["keywords"]

    emotion_result = EmotionDetectorService().detect(request.text)

    avatar_pose   = None
    selected_pose = None
    if emotion_result.get("emotion"):
        selected_pose = AvatarPoseSelectionService().select_best_pose(
            emotion=emotion_result["emotion"],
            poses=AVATAR_POSES,
            prefer_intensity=emotion_result.get("intensity", 0.5),
        )
        if selected_pose:
            avatar_pose = AvatarPoseResponse(
                id=selected_pose.id,
                emotion=selected_pose.emotion,
                intensity=selected_pose.intensity,
                image_path=selected_pose.image_path,
                name=selected_pose.name,
                description=selected_pose.description,
            )

    suggestions_data = StickerGeneratorService().generate_suggestions(
        text=request.text, theme=theme, keywords=keywords, limit=5
    )

    primary_emotion = emotion_result.get("emotion")
    all_scores      = emotion_result.get("all_scores", {})
    top_emotions    = list(all_scores.keys())[:3]
    if primary_emotion:
        while len(top_emotions) < 3:
            top_emotions.append(primary_emotion)

    return StickerSuggestionResponse(
        original_text=request.text,
        suggestions=[StickerSuggestion(**s) for s in suggestions_data],
        total_suggestions=len(suggestions_data),
        avatar_pose=avatar_pose,
        detected_emotion=primary_emotion,
        top_emotions=top_emotions,
        generated_image_base64=None,   # se genera bajo demanda en /generate-image
    )


# ── /generate-image ───────────────────────────────────────────────────────────

class GenerateImageRequest(BaseModel):
    text: str
    emotion: str = ""


class GenerateImageResponse(BaseModel):
    image_base64: str   # PNG base64 con transparencia


@router.post(
    "/generate-image",
    status_code=status.HTTP_200_OK,
    response_model=GenerateImageResponse
)
async def generate_image(request: GenerateImageRequest):
    """
    Genera el sticker final (personaje + globo de diálogo) bajo demanda.
    Se llama solo cuando el usuario toca una burbuja del teclado.
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Text cannot be empty")

    try:
        if _BASE_IMAGE_PATH.exists():
            avatar_img = Image.open(_BASE_IMAGE_PATH).convert("RGBA")
        else:
            avatar_img = generate_placeholder_avatar(request.emotion)

        result_img = generate_sticker(
            base_image=avatar_img,
            text=request.text,
            output_format="PNG",
        )
        buffer = BytesIO()
        result_img.save(buffer, format="PNG")
        return GenerateImageResponse(image_base64=base64.b64encode(buffer.getvalue()).decode())

    except Exception as e:
        print(f"Error generating sticker image (base path: {_BASE_IMAGE_PATH}): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {e}"
        )
