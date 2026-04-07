#!/usr/bin/env python3
"""
Quick test para validar que todos los servicios están funcionando
"""

import sys
import traceback
from pathlib import Path

def test_emotion_detector():
    """Prueba el detector de emociones"""
    print("\n" + "="*60)
    print("TEST 1: Detector de Emociones")
    print("="*60)
    
    try:
        from app.services.emotion_detector import detect_emotion
        
        test_cases = [
            "¡Esto es muy divertido!!! jajaja",
            "¡¡¡NO PUEDO CREER ESTO!!!",
            "No sé qué pensar...",
            "¿Qué? No entiendo",
            "Esto es demasiado triste",
            "Claro, seguro... jeje"
        ]
        
        for texto in test_cases:
            result = detect_emotion(texto)
            print(f"\nTexto: '{texto}'")
            print(f"  -> Emocion: {result['emotion']} (intensidad: {result['intensity']:.2f})")
        
        print("\n[OK] Detector de emociones: OK")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error en detector de emociones: {e}")
        traceback.print_exc()
        return False


def test_avatar_poses():
    """Prueba la estructura de poses de avatar"""
    print("\n" + "="*60)
    print("TEST 2: Poses de Avatar")
    print("="*60)
    
    try:
        from app.models.avatar_pose import get_poses_by_emotion, get_pose_by_id, AVATAR_POSES
        
        print(f"\nTotal de poses: {len(AVATAR_POSES)}")
        
        # Verificar por emoción
        for emotion in ["risa", "sorpresa", "enojo"]:
            poses = get_poses_by_emotion(emotion)
            print(f"  • {emotion}: {len(poses)} poses")
        
        # Ejemplo de pose
        pose = get_pose_by_id("pose_001")
        print(f"\nPose de ejemplo (ID=pose_001):")
        print(f"  • Emoción: {pose.emotion}")
        print(f"  • Intensidad: {pose.intensity}")
        print(f"  • Ruta: {pose.image_path}")
        
        print("\n✅ Poses de avatar: OK")
        return True
        
    except Exception as e:
        print(f"❌ Error en poses de avatar: {e}")
        traceback.print_exc()
        return False


def test_avatar_selection():
    """Prueba la selección de poses de avatar"""
    print("\n" + "="*60)
    print("TEST 3: Selección de Poses")
    print("="*60)
    
    try:
        from app.services.avatar_service import AvatarPoseSelectionService
        from app.models.avatar_pose import AVATAR_POSES
        
        service = AvatarPoseSelectionService()
        
        # Test 1: Selección básica
        pose = service.select_best_pose("risa", AVATAR_POSES)
        print(f"\nSelección básica (risa):")
        print(f"  ➜ Pose seleccionada: {pose.id} - {pose.name}")
        
        # Test 2: Selección por intensidad
        pose = service.select_pose_by_intensity_range("sorpresa", 0.3, 0.6, AVATAR_POSES)
        print(f"\nSelección por intensidad (0.3-0.6):")
        print(f"  ➜ Pose seleccionada: {pose.id} - {pose.name} (intensidad: {pose.intensity})")
        
        # Test 3: Selección ponderada
        pose = service.select_best_pose_weighted("enojo", AVATAR_POSES)
        print(f"\nSelección ponderada (enojo):")
        print(f"  ➜ Pose seleccionada: {pose.id} - {pose.name}")
        
        print("\n✅ Selección de poses: OK")
        return True
        
    except Exception as e:
        print(f"❌ Error en selección de poses: {e}")
        traceback.print_exc()
        return False


def test_image_manipulation():
    """Prueba la manipulación de imágenes"""
    print("\n" + "="*60)
    print("TEST 4: Manipulación de Imágenes")
    print("="*60)
    
    try:
        from app.services.image_manipulation import (
            ImageWithSpeechBubble,
            SpeechBubbleStyle,
            add_speech_bubble
        )
        from PIL import Image
        
        # Crear imagen de prueba
        print("\nCreando imagen de prueba...")
        test_img = Image.new('RGB', (400, 300), color='lightblue')
        test_img.save('test_avatar.png')
        print("  ✓ Imagen creada: test_avatar.png")
        
        # Test 1: Uso simple
        print("\nTest 1: Globo simple...")
        result = add_speech_bubble(
            'test_avatar.png',
            '¡Hola mundo!',
            output_path='test_result_1.png'
        )
        print("  ✓ test_result_1.png")
        
        # Test 2: Con estilo personalizado
        print("\nTest 2: Globo con estilo...")
        style = SpeechBubbleStyle(
            bubble_color=(255, 255, 100),
            text_color=(0, 0, 0),
            border_color=(200, 100, 0),
            border_width=3
        )
        result = ImageWithSpeechBubble.add_speech_bubble(
            'test_avatar.png',
            'Texto personalizado',
            output_path='test_result_2.png',
            style=style
        )
        print("  ✓ test_result_2.png")
        
        # Test 3: Con envolturas de texto
        print("\nTest 3: Texto largo con envoltura...")
        long_text = "Este es un texto más largo que se envolverá automáticamente"
        result = ImageWithSpeechBubble.add_speech_bubble(
            'test_avatar.png',
            long_text,
            output_path='test_result_3.png'
        )
        print("  ✓ test_result_3.png")
        
        print("\n✅ Manipulación de imágenes: OK")
        return True
        
    except Exception as e:
        print(f"❌ Error en manipulación de imágenes: {e}")
        traceback.print_exc()
        return False


def test_integration():
    """Prueba la integración completa"""
    print("\n" + "="*60)
    print("TEST 5: Integración Completa")
    print("="*60)
    
    try:
        from app.services.emotion_detector import detect_emotion
        from app.services.avatar_service import AvatarPoseSelectionService
        from app.models.avatar_pose import AVATAR_POSES
        
        # Texto de prueba
        texto = "¡¡¡Esto es INCREÍBLE!!!"
        
        print(f"\nTexto: '{texto}'")
        
        # Step 1: Detectar emoción
        emotion_result = detect_emotion(texto)
        print(f"\n1. Emoción detectada: {emotion_result['emotion']}")
        print(f"   Intensidad: {emotion_result['intensity']:.2f}")
        
        # Step 2: Seleccionar pose
        service = AvatarPoseSelectionService()
        pose = service.select_best_pose(emotion_result['emotion'], AVATAR_POSES)
        print(f"\n2. Pose seleccionada: {pose.name}")
        print(f"   ID: {pose.id}, Emoción: {pose.emotion}, Intensidad: {pose.intensity}")
        
        # Step 3: Generar imagen (simulado - sin archivos reales)
        print(f"\n3. Generaría imagen: {pose.image_path}")
        print(f"   Con texto: '{texto}'")
        
        print("\n✅ Integración completa: OK")
        return True
        
    except Exception as e:
        print(f"❌ Error en integración: {e}")
        traceback.print_exc()
        return False


def main():
    """Ejecuta todos los tests"""
    print("\n" + "[QUICK TEST] - Validacion de Servicios".center(60))
    print("="*60)
    
    results = {
        "Detector de Emociones": test_emotion_detector(),
        "Poses de Avatar": test_avatar_poses(),
        "Seleccion de Poses": test_avatar_selection(),
        "Manipulacion de Imagenes": test_image_manipulation(),
        "Integracion Completa": test_integration(),
    }
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    
    for test_name, result in results.items():
        status_text = "OK" if result else "FAIL"
        print(f"[{status_text:5}] - {test_name}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("\n[SUCCESS] Todos los tests pasaron!")
    else:
        print(f"\n[WARNING] {total - passed} test(s) fallaron")
    
    print("="*60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

