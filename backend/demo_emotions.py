#!/usr/bin/env python3
"""Demo script for emotion detection service"""
from app.services.emotion_detector import detect_emotion


def print_header(title):
    """Print formatted header"""
    print(f"\n{'=' * 70}")
    print(f"  {title.upper()}")
    print(f"{'=' * 70}\n")


def demo_emotion(text):
    """Demo single emotion detection"""
    result = detect_emotion(text)
    
    print(f"📝 Texto: {text!r}")
    
    if result["emotion"]:
        emoji_map = {
            "risa": "😄",
            "sorpresa": "😲",
            "sarcasmo": "😏",
            "enojo": "😠",
            "tristeza": "😢",
            "confusión": "😕"
        }
        
        emoji = emoji_map.get(result["emotion"], "😐")
        
        print(f"\n{emoji} Emoción detectada: {result['emotion'].upper()}")
        print(f"   Intensidad: {result['intensity']}/1.0 ({result['intensity_level']})")
        print(f"   Confianza: {result['confidence']}/1.0")
        
        if result.get('all_scores'):
            print("\n   Puntuaciones por emoción:")
            for emotion, score in result['all_scores'].items():
                if score > 0:
                    bar = "█" * int(score * 10)
                    print(f"     {emotion:12} {score:0.2f} {bar}")
    else:
        print(f"\n❓ No se detectó emoción clara")
    
    print()


def main():
    """Run emotion detection demo"""
    print_header("Servicio de Detección de Emociones - Demo")
    
    # Test categories
    tests = {
        "RISA (Laughter)": [
            "jajaja",
            "haha qué divertido!",
            "jajajajaja!!! me muero de risa!!!",
        ],
        "SORPRESA (Surprise)": [
            "no puede ser!",
            "¡Increíble!",
            "wow eso es asombroso!!",
        ],
        "SARCASMO (Sarcasm)": [
            "te dije",
            "claro que sí, seguro",
            "como si fuera verdad...",
        ],
        "ENOJO (Anger)": [
            "¡¡¡estoy furioso!!!",
            "me enoja mucho esto",
            "detesto cuando pasa eso",
        ],
        "TRISTEZA (Sadness)": [
            "me siento muy triste",
            "no hay esperanza",
            "mi corazón duele... adiós",
        ],
        "CONFUSIÓN (Confusion)": [
            "no entiendo... ¿qué?",
            "estoy confundido",
            "perdida... no sé qué hacer??",
        ],
    }
    
    for category, texts in tests.items():
        print_header(category)
        for text in texts:
            demo_emotion(text)
    
    print_header("Resumen")
    print("""
✅ Emociones soportadas:
   • risa (Laughter & Happiness)
   • sorpresa (Surprise & Amazement)
   • sarcasmo (Sarcasm & Irony)
   • enojo (Anger & Fury)
   • tristeza (Sadness & Sorrow)
   • confusión (Confusion & Uncertainty)

📊 Métricas:
   • intensity: Intensidad de la emoción (0.0 - 1.0)
   • intensity_level: Nivel cualitativo (baja, media, alta)
   • confidence: Confianza en la detección (0.0 - 1.0)
   • all_scores: Puntuaciones de todas las emociones

🚀 Para usar en FastAPI:
   POST /api/v1/detect-emotion
   {{"text": "tu texto aquí"}}
    """)
    print(f"\n{'=' * 70}\n")


if __name__ == "__main__":
    main()
