"""Sticker generation service"""
from typing import List, Optional
import uuid


class StickerGeneratorService:
    """Service for generating sticker suggestions"""
    
    # Sample sticker database
    STICKER_LIBRARY = {
        "celebration": [
            {"name": "Party Balloon", "description": "Colorful balloons", "style": "cartoon"},
            {"name": "Confetti", "description": "Falling confetti", "style": "animated"},
            {"name": "Cake Slice", "description": "Delicious cake", "style": "realistic"},
        ],
        "love": [
            {"name": "Heart", "description": "Red heart", "style": "simple"},
            {"name": "Rose", "description": "Red rose", "style": "realistic"},
            {"name": "Cupid", "description": "Cupid with arrow", "style": "cartoon"},
        ],
        "humor": [
            {"name": "Laughing Face", "description": "Laughing emoji", "style": "emoji"},
            {"name": "Joke Bang", "description": "Punchline effect", "style": "comic"},
            {"name": "Funny Cat", "description": "Silly cat face", "style": "cartoon"},
        ],
        "nature": [
            {"name": "Flower", "description": "Beautiful flower", "style": "realistic"},
            {"name": "Butterfly", "description": "Colorful butterfly", "style": "cartoon"},
            {"name": "Sunshine", "description": "Bright sun", "style": "simple"},
        ],
        "work": [
            {"name": "Rocket", "description": "Launching rocket", "style": "cartoon"},
            {"name": "Lightbulb", "description": "Idea lightbulb", "style": "simple"},
            {"name": "Trophy", "description": "Achievement trophy", "style": "realistic"},
        ],
        "general": [
            {"name": "Star", "description": "Shiny star", "style": "simple"},
            {"name": "Smiley", "description": "Happy face", "style": "emoji"},
            {"name": "Sparkle", "description": "Magical sparkle", "style": "animated"},
        ]
    }
    
    @classmethod
    def generate_suggestions(
        cls,
        text: str,
        theme: str = "general",
        keywords: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[dict]:
        """Generate sticker suggestions based on analysis"""
        
        # Get stickers for the theme
        theme_stickers = cls.STICKER_LIBRARY.get(theme, cls.STICKER_LIBRARY["general"])
        
        suggestions = []
        for sticker in theme_stickers[:limit]:
            suggestion = {
                "id": str(uuid.uuid4()),
                "name": sticker["name"],
                "description": sticker["description"],
                "style": sticker["style"],
                "tags": [theme, sticker["style"]] + (keywords or [])[:2]
            }
            suggestions.append(suggestion)
        
        return suggestions
