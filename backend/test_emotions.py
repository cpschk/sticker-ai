"""Test examples for emotion detector"""
from app.services.emotion_detector import EmotionDetectorService


# Test cases
test_cases = [
    # Risa (Laughter)
    "jajaja",
    "haha qué divertido",
    "jajajaja me muero de risa!!!",
    
    # Sorpresa (Surprise)
    "no puede ser!",
    "increíble!!",
    "wow eso es asombroso",
    "¡Ay dios mío!",
    
    # Sarcasmo (Sarcasm)
    "te dije",
    "claro que sí, seguro",
    "como si eso fuera verdad",
    "gracias por nada",
    
    # Enojo (Anger)
    "¡¡¡estoy furioso!!!",
    "me enoja mucho esto",
    "detesto cuando pasa eso",
    "basta ya!!!",
    "qué rabia",
    
    # Tristeza (Sadness)
    "Me siento muy triste",
    "No hay esperanza",
    "Lloré toda la noche",
    "Mi corazón duele",
    "Chao... adiós",
    
    # Confusión (Confusion)
    "No entiendo... ¿qué?",
    "Estoy confundido",
    "Que pasa?? No sé",
    "Perdido sin rumbo",
    "ehh.. explica por favor??",
]


def test_emotions():
    """Run emotion detection tests"""
    print("=" * 70)
    print("EMOTION DETECTION TESTS")
    print("=" * 70)
    
    for text in test_cases:
        result = EmotionDetectorService.detect(text)
        
        print(f"\nText: '{text}'")
        print(f"Emotion: {result['emotion'].upper() if result['emotion'] else 'None'}")
        print(f"Intensity: {result['intensity']}/1.0 ({result['intensity_level']})")
        print(f"Confidence: {result['confidence']}/1.0")
        if result.get('all_scores'):
            print(f"All scores: {result['all_scores']}")
        print("-" * 70)


if __name__ == "__main__":
    test_emotions()
