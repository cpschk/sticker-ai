"""Text analysis service"""
from typing import List
import re


class TextAnalyzerService:
    """Service for analyzing text and extracting information"""
    
    @staticmethod
    def extract_keywords(text: str, limit: int = 5) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction (in production, use NLP libraries)
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        common_words = {'the', 'and', 'for', 'are', 'was', 'were', 'is', 'be', 'have', 'has', 'had'}
        keywords = [w for w in set(words) if w not in common_words]
        return keywords[:limit]
    
    @staticmethod
    def analyze_sentiment(text: str) -> str:
        """Analyze sentiment of text"""
        # Simple sentiment analysis (in production, use proper ML models)
        positive_words = ['happy', 'joy', 'love', 'great', 'awesome', 'excellent', 'good']
        negative_words = ['sad', 'angry', 'hate', 'bad', 'terrible', 'awful', 'poor']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        return "neutral"
    
    @staticmethod
    def detect_theme(text: str) -> str:
        """Detect theme from text"""
        # Simple theme detection (in production, use ML models)
        text_lower = text.lower()
        
        themes = {
            "celebration": ["party", "celebrate", "happy", "joy", "birthday", "anniversary"],
            "love": ["love", "heart", "romantic", "dear", "sweetheart"],
            "humor": ["funny", "laugh", "joke", "hilarious", "lol"],
            "nature": ["flower", "tree", "sun", "moon", "star", "nature", "garden"],
            "work": ["work", "job", "project", "deadline", "office", "meeting"],
            "general": []
        }
        
        for theme, keywords in themes.items():
            if any(keyword in text_lower for keyword in keywords):
                return theme
        
        return "general"
    
    def analyze(self, text: str) -> dict:
        """Perform complete text analysis"""
        return {
            "text": text,
            "keywords": self.extract_keywords(text),
            "sentiment": self.analyze_sentiment(text),
            "theme": self.detect_theme(text)
        }
