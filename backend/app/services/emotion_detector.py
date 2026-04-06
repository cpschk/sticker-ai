"""Emotion detection service"""
import re
from typing import Tuple, Dict
from enum import Enum


class Emotion(str, Enum):
    """Available emotions"""
    RISA = "risa"
    SARCASMO = "sarcasmo"
    ENOJO = "enojo"
    SORPRESA = "sorpresa"
    TRISTEZA = "tristeza"
    CONFUSIÓN = "confusión"


class EmotionDetectorService:
    """Service for detecting emotions in text"""
    
    # Emotion keywords and patterns
    EMOTION_KEYWORDS = {
        Emotion.RISA: {
            "keywords": [
                "jaja", "jajaja", "jajajaja", "haha", "hahaha", "lol", "jeje", "je",
                "hehe", "ja", "aufff", "ajajaja", "kkk", "mdr", "risas", "me rio"
            ],
            "patterns": [r"j[aá]+\s*j[aá]+", r"ha+\s*ha+", r"o+l+o+"],
            "weight": 1.0
        },
        Emotion.SORPRESA: {
            "keywords": [
                "no puede ser", "increíble", "wow", "guau", "ay", "ay dios", "que sorpresa",
                "no lo creo", "en serio", "que locura", "imposible", "de verdad", "oh",
                "omg", "sorprendente", "asombroso"
            ],
            "patterns": [r"¡+\s*[a-z]+\s*!", r"\?+\s*\?+"],
            "weight": 0.9
        },
        Emotion.ENOJO: {
            "keywords": [
                "furioso", "enojado", "rabia", "ira", "furioso", "me enoja", "odio",
                "detesto", "basta", "ya", "que rabia", "maldita", "maldito", "eres un",
                "idiota", "tonto", "estúpido", "no aguanto", "harto", "cansado"
            ],
            "patterns": [r"!!+", r"[a-z]+!!+"],
            "weight": 1.0
        },
        Emotion.TRISTEZA: {
            "keywords": [
                "triste", "tristeza", "llorar", "llorando", "lloré", "lloro", "llore",
                "lágrimas", "lagrimas", "deprimido", "depre", "mal",
                "horrible", "peor", "nunca", "no hay esperanza", "fin", "adiós", "adios",
                "chao", "me duele", "corazón", "corazon", "dolor", "sufriendo", "infeliz",
                "desgraciado", "solo", "sola", "vacío", "vacio"
            ],
            "patterns": [r":'?\(", r"T_T", r"='?\("],
            "weight": 0.95
        },
        Emotion.CONFUSIÓN: {
            "keywords": [
                "confundido", "confusión", "no entiendo", "que", "cual", "que onda",
                "no sé", "ehh", "umm", "que pasa", "que dice", "como así", "que significa",
                "no entendí", "explica", "perdida", "perdido", "ayuda"
            ],
            "patterns": [r"\?+$", r"^s*\?+", r"confuso"],
            "weight": 0.85
        },
        Emotion.SARCASMO: {
            "keywords": [
                "claro", "seguro", "obviamente", "si claro", "te dije", "ya sabía",
                "como si", "supongo", "por supuesto", "aja", "mmm", "interesante",
                "wow qué original", "cuánta creatividad", "muy amable", "gracias por nada",
                "excelente idea"
            ],
            "patterns": [r"\.\.\.$", r"claro que sí"],
            "weight": 0.8
        }
    }
    
    @classmethod
    def _count_repetitions(cls, text: str) -> int:
        """Count character repetitions (intensity marker)"""
        # Look for repeated characters like "jajajaja" or "!!!"
        repetitions = re.findall(r'(.)\1{2,}', text)
        return len(repetitions)
    
    @classmethod
    def _detect_emphasis(cls, text: str) -> float:
        """Detect text emphasis with uppercase and punctuation"""
        uppercase_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        exclamation_marks = text.count('!')
        question_marks = text.count('?')
        
        emphasis = 0.0
        if uppercase_ratio > 0.5:
            emphasis += 0.2
        if exclamation_marks > 0:
            emphasis += 0.1 * min(exclamation_marks, 5)
        if question_marks > 0:
            emphasis += 0.05 * min(question_marks, 5)
        
        return min(emphasis, 1.0)
    
    @classmethod
    def _calculate_intensity(cls, text: str, emotion_score: float) -> float:
        """Calculate intensity of emotion (0.0 to 1.0)"""
        base_intensity = emotion_score
        
        # Add emphasis factors
        emphasis = cls._detect_emphasis(text)
        repetitions = cls._count_repetitions(text)
        
        # Repetitions boost intensity
        repetition_boost = min(repetitions * 0.15, 0.3)
        
        # Calculate final intensity
        intensity = base_intensity + emphasis * 0.2 + repetition_boost
        
        return min(intensity, 1.0)
    
    @classmethod
    def _match_keywords(cls, text: str, emotion: Emotion) -> Tuple[bool, float]:
        """Check if text contains keywords for the emotion"""
        text_lower = text.lower()
        text_lower = re.sub(r'[^\w\s]', ' ', text_lower)  # Remove special chars for matching
        
        keywords = cls.EMOTION_KEYWORDS[emotion]["keywords"]
        patterns = cls.EMOTION_KEYWORDS[emotion]["patterns"]
        
        # Check keywords
        keyword_matches = sum(1 for kw in keywords if kw in text_lower)
        
        # Check patterns
        pattern_matches = sum(1 for pattern in patterns if re.search(pattern, text, re.IGNORECASE))
        
        total_matches = keyword_matches + pattern_matches
        
        if total_matches > 0:
            # Calculate score based on matches
            score = min(total_matches * 0.25, 1.0)
            return True, score
        
        return False, 0.0
    
    @classmethod
    def detect(cls, text: str) -> Dict[str, any]:
        """
        Detect emotion in text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with:
                - emotion: Detected emotion (Emotion enum)
                - intensity: Intensity level (0.0 to 1.0)
                - confidence: Confidence in the detection (0.0 to 1.0)
                - details: Details about matches found
        """
        if not text or len(text.strip()) == 0:
            return {
                "emotion": None,
                "intensity": 0.0,
                "intensity_level": "baja",
                "confidence": 0.0,
                "all_scores": {},
                "details": "Empty text"
            }

        emotion_scores = {}

        # Calculate scores for each emotion
        for emotion in Emotion:
            matched, score = cls._match_keywords(text, emotion)
            if matched:
                emotion_scores[emotion] = score

        if not emotion_scores:
            return {
                "emotion": None,
                "intensity": 0.0,
                "intensity_level": "baja",
                "confidence": 0.0,
                "all_scores": {},
                "details": "No emotion detected"
            }
        
        # Get emotion with highest score
        detected_emotion = max(emotion_scores, key=emotion_scores.get)
        confidence = emotion_scores[detected_emotion]
        intensity = cls._calculate_intensity(text, confidence)
        
        # Format intensity levels
        intensity_level = "baja"
        if intensity >= 0.7:
            intensity_level = "alta"
        elif intensity >= 0.4:
            intensity_level = "media"
        
        return {
            "emotion": detected_emotion.value,
            "intensity": round(intensity, 2),
            "intensity_level": intensity_level,
            "confidence": round(confidence, 2),
            "all_scores": {e.value: round(s, 2) for e, s in sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)}
        }


# Convenience function for FastAPI
def detect_emotion(text: str) -> Dict[str, any]:
    """
    Convenience function to detect emotion
    
    Args:
        text: Input text
        
    Returns:
        Emotion detection result
    """
    return EmotionDetectorService.detect(text)
