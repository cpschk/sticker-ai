#!/usr/bin/env python3
"""
Cliente de ejemplo para probar el endpoint /suggest-sticker
Demuestra cómo decodificar y usar la imagen base64 recibida
"""

import json
import base64
from pathlib import Path


def demo_using_response():
    """Demuestra cómo usar la respuesta del endpoint"""
    
    print("\n" + "="*70)
    print("DEMO: Cliente HTTP para /suggest-sticker")
    print("="*70)
    
    # Ejemplo de respuesta JSON (simulada)
    print("\n1. REALIZAR PETICIÓN HTTP")
    print("-" * 70)
    print("curl -X POST http://localhost:8000/api/v1/suggest-sticker \\")
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"text": "¡¡¡ No puedo creer esto !!!"}\'')
    
    # Cargar la imagen de prueba que generamos
    print("\n2. RESPUESTA JSON RECIBIDA")
    print("-" * 70)
    
    try:
        # Cargar imagen de prueba del archivo generado
        with open('test_suggest_sticker_output.png', 'rb') as f:
            image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode()
        
        response = {
            "original_text": "¡¡¡ No puedo creer esto !!!",
            "detected_emotion": "enojo",
            "avatar_pose": {
                "id": "pose_008",
                "emotion": "enojo",
                "intensity": 0.65,
                "image_path": "/avatars/poses/enojo_medio.png",
                "name": "Enojo moderado",
                "description": "Avatar mostrando enojo moderado"
            },
            "suggestions": [
                {
                    "id": "s001",
                    "name": "Star",
                    "description": "Estrella brillante",
                    "style": "simple",
                    "tags": ["expresion", "sorpresa"]
                },
                {
                    "id": "s002",
                    "name": "Smiley",
                    "description": "Cara sonriente",
                    "style": "emoji",
                    "tags": ["cara", "expresion"]
                },
                {
                    "id": "s003",
                    "name": "Sparkle",
                    "description": "Efecto de destellos",
                    "style": "animated",
                    "tags": ["efecto", "luz"]
                }
            ],
            "total_suggestions": 3,
            "generated_image_base64": image_base64
        }
        
        # Mostrar estructura JSON (sin base64 completo para claridad)
        response_display = response.copy()
        response_display["generated_image_base64"] = (
            response_display["generated_image_base64"][:50] + 
            f"... [{len(image_base64):,} caracteres totales]"
        )
        
        print(json.dumps(response_display, indent=2, ensure_ascii=False))
        
        print("\n3. PROCESAR RESPUESTA EN CLIENTE")
        print("-" * 70)
        
        # Ejemplo en Python
        print("""
# En Python:
import json
import base64
from io import BytesIO
from PIL import Image

response = requests.post(
    'http://localhost:8000/api/v1/suggest-sticker',
    json={'text': '¡¡¡ No puedo creer esto !!!'}
)

data = response.json()

# Extraer información
print("Emoción detectada:", data['detected_emotion'])
print("Avatar pose:", data['avatar_pose']['name'])
print("Total de sugerencias:", data['total_suggestions'])

# Decodificar y mostrar la imagen
if data.get('generated_image_base64'):
    image_data = base64.b64decode(data['generated_image_base64'])
    image = Image.open(BytesIO(image_data))
    image.show()
    # O guardarla
    image.save('avatar_with_speech_bubble.png')
        """)
        
        print("\n4. INFORMACIÓN EXTRAÍDA")
        print("-" * 70)
        print(f"Emoción: {response['detected_emotion']}")
        print(f"Avatar: {response['avatar_pose']['name']}")
        print(f"  - Intensidad: {response['avatar_pose']['intensity']}")
        print(f"  - Ruta: {response['avatar_pose']['image_path']}")
        print(f"\nStickers sugeridos ({response['total_suggestions']}):")
        for i, sugg in enumerate(response['suggestions'], 1):
            print(f"  {i}. {sugg['name']} ({sugg['style']})")
            print(f"     {sugg['description']}")
        
        print(f"\nTamaño de imagen generada:")
        print(f"  - PNG comprimido: {len(image_base64):,} caracteres base64")
        print(f"  - Bytes reales: {len(image_data):,} bytes")
        
        print("\n5. USO EN DIFERENTES CONTEXTOS")
        print("-" * 70)
        
        print("""
# JavaScript/Fetch API
fetch('http://localhost:8000/api/v1/suggest-sticker', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text: '¡¡¡ No puedo creer esto !!!'})
})
.then(r => r.json())
.then(data => {
    console.log('Emoción:', data.detected_emotion);
    
    // Mostrar imagen
    if (data.generated_image_base64) {
        const img = new Image();
        img.src = 'data:image/png;base64,' + data.generated_image_base64;
        document.body.appendChild(img);
    }
});

# Swift (iOS)
let url = URL(string: "http://localhost:8000/api/v1/suggest-sticker")!
var request = URLRequest(url: url)
request.httpMethod = "POST"
request.setValue("application/json", forHTTPHeaderField: "Content-Type")

let json = ["text": "¡¡¡ No puedo creer esto !!!"]
request.httpBody = try JSONSerialization.data(withJSONObject: json)

URLSession.shared.dataTask(with: request) { data, _, _ in
    if let data = data,
       let response = try? JSONDecoder().decode(StickerResponse.self, from: data),
       let imageData = Data(base64Encoded: response.generatedImageBase64),
       let image = UIImage(data: imageData) {
        DispatchQueue.main.async {
            self.imageView.image = image
        }
    }
}.resume()
        """)
        
        print("\n6. CASOS DE USO")
        print("-" * 70)
        print("""
✓ Chat con avatares reactivos
  - Mostrar avatar del usuario con su emoción detectada
  - Agregar un globo de diálogo con su mensaje

✓ Recomendación de stickers
  - Sugerir stickers contexto con la emoción
  - Avatar reacciona a lo que está diciendo el usuario

✓ Análisis de sentimiento visual
  - Visualizar cómo el bot interpreta el sentimiento
  - Mostrar la pose de avatar que corresponde

✓ Generación de memes/contenido
  - Crear imágenes con texto automáticamente
  - Usar como base para ediciones posteriores
        """)
        
        print("\n" + "="*70)
        print("[OK] Demo completado")
        print("="*70 + "\n")
        
    except FileNotFoundError:
        print("[ERROR] test_suggest_sticker_output.png no encontrado")
        print("Ejecuta primero: python test_suggest_sticker_with_image.py")


if __name__ == "__main__":
    demo_using_response()
