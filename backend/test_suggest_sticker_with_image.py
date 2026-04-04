#!/usr/bin/env python3
"""
Test para verificar que /suggest-sticker genera imágenes correctamente
"""

import sys
import base64
from pathlib import Path

def test_suggest_sticker_with_image():
    """Prueba la integración de imagen en /suggest-sticker"""
    
    print("\n" + "="*70)
    print("TEST: /suggest-sticker con generación de imagen")
    print("="*70)
    
    try:
        # Importar los servicios
        from app.services.emotion_detector import EmotionDetectorService
        from app.services.avatar_service import AvatarPoseSelectionService
        from app.services.text_analyzer import TextAnalyzerService
        from app.services.sticker_generator import StickerGeneratorService
        from app.models.avatar_pose import AVATAR_POSES
        from app.services.image_manipulation import ImageWithSpeechBubble, SpeechBubbleStyle
        from PIL import Image
        from io import BytesIO
        
        # Crear instancias
        emotion_detector = EmotionDetectorService()
        avatar_service = AvatarPoseSelectionService()
        text_analyzer = TextAnalyzerService()
        sticker_generator = StickerGeneratorService()
        
        # Texto de prueba
        test_text = "¡¡¡ No puedo creer esto !!!"
        
        print(f"\nTexto de entrada: '{test_text}'")
        print("-" * 70)
        
        # PASO 1: Detectar emoción
        print("\n1. DETECTAR EMOCION")
        emotion_result = emotion_detector.detect(test_text)
        emotion = emotion_result['emotion']
        intensity = emotion_result['intensity']
        print(f"   Emoción detectada: {emotion}")
        print(f"   Intensidad: {intensity:.2f}")
        
        # PASO 2: Seleccionar pose
        print("\n2. SELECCIONAR POSE")
        selected_pose = avatar_service.select_best_pose(
            emotion=emotion,
            poses=AVATAR_POSES,
            prefer_intensity=intensity
        )
        print(f"   Pose seleccionada: {selected_pose.name}")
        print(f"   ID: {selected_pose.id}")
        print(f"   Intensidad de pose: {selected_pose.intensity}")
        
        # PASO 3: Generar stickers
        print("\n3. GENERAR STICKERS")
        analysis = text_analyzer.analyze(test_text)
        suggestions = sticker_generator.generate_suggestions(
            text=test_text,
            theme=analysis["theme"],
            keywords=analysis["keywords"],
            limit=5
        )
        print(f"   Sugerencias generadas: {len(suggestions)}")
        for i, sugg in enumerate(suggestions[:3], 1):
            print(f"      {i}. {sugg['name']} ({sugg['style']})")
        
        # PASO 4: Generar imagen
        print("\n4. GENERAR IMAGEN CON GLOBO")
        
        # Crear imagen simple
        avatar_img = Image.new('RGB', (400, 300), color='lightblue')
        
        # Seleccionar color según emoción
        emotion_colors = {
            'risa': (255, 255, 100),      # Yellow
            'sorpresa': (255, 180, 255),  # Magenta
            'enojo': (255, 150, 150),     # Red
            'tristeza': (150, 200, 255),  # Blue
            'confusión': (200, 150, 255), # Purple
            'sarcasmo': (200, 200, 200),  # Gray
        }
        
        bubble_color = emotion_colors.get(emotion, (200, 200, 200))
        
        # Crear estilo
        style = SpeechBubbleStyle(
            bubble_color=bubble_color,
            border_color=tuple(max(0, c-50) for c in bubble_color),
            border_width=2
        )
        
        print(f"   Color del globo: RGB{bubble_color}")
        print(f"   Posición: top")
        
        # Generar imagen con globo
        result_img = ImageWithSpeechBubble.add_speech_bubble_from_image(
            image=avatar_img,
            text=test_text,
            style=style,
            bubble_position="top",
            font_size=16
        )
        
        # Guardar original en disco para inspection
        result_img.save('test_suggest_sticker_output.png')
        print(f"   v Imagen guardada: test_suggest_sticker_output.png")
        
        # PASO 5: Convertir a base64
        print("\n5. CODIFICAR IMAGEN")
        buffer = BytesIO()
        result_img.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        base64_length = len(image_base64)
        print(f"   Tamaño en base64: {base64_length:,} caracteres")
        print(f"   Primeros 100 caracteres: {image_base64[:100]}...")
        
        # PASO 6: Resumen
        print("\n" + "="*70)
        print("RESUMEN DE LA RESPUESTA SIMULADA")
        print("="*70)
        
        response_data = {
            "original_text": test_text,
            "detected_emotion": emotion,
            "avatar_pose": {
                "id": selected_pose.id,
                "emotion": emotion,
                "intensity": intensity,
                "image_path": selected_pose.image_path,
                "name": selected_pose.name
            },
            "suggestions": suggestions[:2],
            "total_suggestions": len(suggestions),
            "generated_image_base64": f"<base64 de {base64_length:,} caracteres>"
        }
        
        print("\nJSON Response Structure:")
        print(f"{{")
        print(f'  "original_text": "{response_data["original_text"]}",')
        print(f'  "detected_emotion": "{response_data["detected_emotion"]}",')
        print(f'  "avatar_pose": {{')
        print(f'    "id": "{selected_pose.id}",')
        print(f'    "emotion": "{emotion}",')
        print(f'    "intensity": {intensity},')
        print(f'    "name": "{selected_pose.name}"')
        print(f'  }},')
        print(f'  "suggestions": [')
        for i, sugg in enumerate(suggestions[:2]):
            comma = "," if i < 1 else ""
            print(f'    {{')
            print(f'      "id": "{sugg["id"]}",')
            print(f'      "name": "{sugg["name"]}",')
            print(f'      "style": "{sugg["style"]}"')
            print(f'    }}{comma}')
        print(f'  ],')
        print(f'  "total_suggestions": {len(suggestions)},')
        print(f'  "generated_image_base64": "[PNG image data - {base64_length:,} chars]"')
        print(f'}}')
        
        print("\n" + "="*70)
        print("[OK] Test completado exitosamente")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_suggest_sticker_with_image()
    sys.exit(0 if success else 1)
