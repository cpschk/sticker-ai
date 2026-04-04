# Endpoint /suggest-sticker con Generación de Imagen

## Resumen

El endpoint `POST /api/v1/suggest-sticker` ahora genera automáticamente una **imagen PNG** con un globo de diálogo reactivo al texto analizado.

## Características Nuevas

✅ **Generación automática de imagen PNG**
- Crea un avatar simple con globo de diálogo
- Color del globo cambia según la emoción detectada

✅ **Entrega en base64**
- La imagen se codifica en base64 y se devuelve en la respuesta JSON
- Facilita la integración en aplicaciones web/móvil

✅ **Estilos reactivos**
- Colores de globo varían según emoción:
  - 😄 Risa (Amarillo): `#FFFF64`
  - 😲 Sorpresa (Magenta): `#FFB4FF`
  - 😠 Enojo (Rojo): `#FF9696`
  - 😢 Tristeza (Azul): `#96C8FF`
  - 😕 Confusión (Púrpura): `#C896FF`
  - 😏 Sarcasmo (Gris): `#C8C8C8`

## Petición

```bash
curl -X POST http://localhost:8000/api/v1/suggest-sticker \
  -H "Content-Type: application/json" \
  -d '{"text": "¡¡¡ No puedo creer esto !!!"}'
```

### Parámetros

```json
{
  "text": "string (requerido) - Texto a analizar",
  "keywords": ["array (opcional) - Palabras clave adicionales"],
  "theme": "string (opcional) - Tema específico"
}
```

## Respuesta

```json
{
  "original_text": "¡¡¡ No puedo creer esto !!!",
  "detected_emotion": "enojo",
  "avatar_pose": {
    "id": "pose_008",
    "emotion": "enojo",
    "intensity": 0.65,
    "image_path": "/avatars/poses/enojo_medio.png",
    "name": "Enojo moderado",
    "description": "Avatar del Avatar mostrando enojo moderado"
  },
  "suggestions": [
    {
      "id": "s001",
      "name": "Star",
      "description": "Estrella brillante",
      "style": "simple",
      "tags": ["expresion", "sorpresa"]
    },
    // ... más sugerencias ...
  ],
  "total_suggestions": 3,
  "generated_image_base64": "iVBORw0KGgo...AAAAASUVORK5CYII=",
  "generated_image_url": null
}
```

### Campos de Respuesta

| Campo | Tipo | Descripción |
|-------|------|------------|
| `original_text` | string | Texto original enviado |
| `detected_emotion` | string | Emoción detectada (risa, sorpresa, etc.) |
| `avatar_pose` | object | Pose de avatar seleccionada |
| `suggestions` | array | Stickers recomendados (hasta 5) |
| `total_suggestions` | number | Total de stickers generados |
| `generated_image_base64` | string | Imagen PNG codificada en base64 |
| `generated_image_url` | string/null | URL a la imagen (si se guardó en servidor) |

## Procesamiento de la Imagen

### Python

```python
import requests
import base64
from PIL import Image
from io import BytesIO

# 1. Realizar petición
response = requests.post(
    'http://localhost:8000/api/v1/suggest-sticker',
    json={'text': '¡¡¡ No puedo creer esto !!!'}
)

data = response.json()

# 2. Decodificar imagen
if data.get('generated_image_base64'):
    image_data = base64.b64decode(data['generated_image_base64'])
    image = Image.open(BytesIO(image_data))
    
    # Mostrar
    image.show()
    
    # O guardar
    image.save('avatar_speaking.png')

# 3. Usar otros datos
print(f"Emoción: {data['detected_emotion']}")
print(f"Avatar: {data['avatar_pose']['name']}")
```

### JavaScript

```javascript
// 1. Realizar petición
const response = await fetch('http://localhost:8000/api/v1/suggest-sticker', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text: '¡¡¡ No puedo creer esto !!!'})
});

const data = await response.json();

// 2. Mostrar imagen en HTML
if (data.generated_image_base64) {
    const img = document.createElement('img');
    img.src = `data:image/png;base64,${data.generated_image_base64}`;
    img.style.maxWidth = '400px';
    document.body.appendChild(img);
}

// 3. Usar otros datos
console.log(`Emoción: ${data.detected_emotion}`);
console.log(`Avatar: ${data.avatar_pose.name}`);

// 4. Descargar imagen
const link = document.createElement('a');
link.href = `data:image/png;base64,${data.generated_image_base64}`;
link.download = 'avatar_speaking.png';
link.click();
```

### Swift / iOS

```swift
import Alamofire

AF.request("http://localhost:8000/api/v1/suggest-sticker",
           method: .post,
           parameters: ["text": "¡¡¡ No puedo creer esto !!!"],
           encoding: JSONEncoding.default)
    .responseJSON { response in
        guard let data = response.value as? [String: Any],
              let base64String = data["generated_image_base64"] as? String,
              let imageData = Data(base64Encoded: base64String),
              let image = UIImage(data: imageData) else {
            return
        }
        
        DispatchQueue.main.async {
            self.avatarImageView.image = image
        }
    }
```

## Flujo de Procesamiento

```
Entrada: "¡¡¡ No puedo creer esto !!!"
    ↓
[1] EmotionDetectorService
    - Analiza: palabras clave, patrones, intensidad
    - Resultado: emotion="enojo", intensity=0.61
    ↓
[2] AvatarPoseSelectionService
    - Selecciona pose por emoción + intensidad
    - Resultado: pose_008 (Enojo moderado)
    ↓
[3] StickerGeneratorService
    - Genera sugerencias contextuales
    - Resultado: 3 stickers recomendados
    ↓
[4] ImageWithSpeechBubble.add_speech_bubble_from_image()
    - Crea imagen base (400x300 px)
    - Elige color de globo según emoción
    - Dibuja globo de diálogo con texto
    - Resultado: Imagen PNG 400x300
    ↓
[5] Codificación base64
    - Convierte PNG a base64
    - Resultado: ~4,000-5,000 caracteres
    ↓
Salida: JSON con imagen, emoción, pose, stickers
```

## Ejemplo Completo

### Request

```bash
curl -X POST http://localhost:8000/api/v1/suggest-sticker \
  -H "Content-Type: application/json" \
  -d '{
    "text": "¡Estoy muy feliz con esta noticia!",
    "theme": "positivo"
  }'
```

### Response

```json
{
  "original_text": "¡Estoy muy feliz con esta noticia!",
  "detected_emotion": "risa",
  "avatar_pose": {
    "id": "pose_001",
    "emotion": "risa",
    "intensity": 0.8,
    "image_path": "/avatars/poses/risa_media.png",
    "name": "Risa Media",
    "description": "Avatar sonriendo moderadamente"
  },
  "suggestions": [
    {
      "id": "stk_joy_01",
      "name": "Happy Stars",
      "description": "Estrellas alegres",
      "style": "animated",
      "tags": ["felicidad", "celebracion"]
    },
    {
      "id": "stk_heart_01",
      "name": "Floating Hearts",
      "description": "Corazones flotantes",
      "style": "animated",
      "tags": ["amor", "felicidad"]
    }
  ],
  "total_suggestions": 2,
  "generated_image_base64": "iVBORw0KGgoAAAANSUhEUgAAAZAAAAEsCAI...",
  "generated_image_url": null
}
```

## Tamaños de Respuesta

| Componente | Tamaño |
|-----------|--------|
| JSON metadata | ~500 bytes |
| Imagen PNG base64 | ~4-5 KB |
| TOTAL | ~4.5-5.5 KB |

## Códigos de Estado

| Código | Significado |
|--------|-----------|
| 200 | Éxito - Imagen generada y devuelta |
| 400 | Error - Texto vacío o inválido |
| 500 | Error - Fallo en generación de imagen (sigue devolviendo resultado) |

## Limitaciones Actuales

⚠️ **Imagen hardcodeada**
- Actualmente genera una imagen azul simple (400x300 px)
- En producción, usaría la ruta real del avatar: `avatar_pose.image_path`

⚠️ **Tipografía limitada**
- Usa fuentes del sistema (Arial en Windows)
- Fallback a fuente por defecto si no está disponible

⚠️ **Tamaño fijo**
- Imagen siempre 400x300 px
- Considerar hacer configurable en futuro

## Mejoras Futuras

1. **Carga de avatares reales**
   - Integrar con un servicio de almacenamiento (S3, Google Cloud)
   - Cargar imágenes reales según `avatar_pose.image_path`

2. **Guardado en servidor**
   - Opción para guardar imagen en servidor
   - Devolver URL en `generated_image_url`
   - Limpiar periódicamente

3. **Parámetros de personalización**
   - Permitir tamaño de imagen configurable
   - Estilos de globo personalizables
   - Posición del globo variable

4. **Múltiples formatos**
   - Soporte para GIF (animado)
   - Soporte para WebP (menor tamaño)
   - JPEG como fallback

5. **Caché de imágenes**
   - Cachear imágenes generadas
   - Reutilizar para textos similares
   - Reducir carga de servidor

## Testing

```bash
# Test básico
python test_suggest_sticker_with_image.py

# Demo de cliente
python demo_suggest_sticker_client.py

# Prueba con curl
curl -X POST http://localhost:8000/api/v1/suggest-sticker \
  -H "Content-Type: application/json" \
  -d '{"text": "Prueba de imagen"}' | jq .
```

## Integración Frontend

```html
<!-- Mostrar imagen en HTML -->
<img id="avatar-image" src="" alt="Avatar con globo" />

<script>
  async function getAvatarWithSpeech(text) {
    const response = await fetch('http://localhost:8000/api/v1/suggest-sticker', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text})
    });
    
    const data = await response.json();
    
    if (data.generated_image_base64) {
      document.getElementById('avatar-image').src = 
        `data:image/png;base64,${data.generated_image_base64}`;
    }
    
    return data;
  }
</script>
```

---

**Última actualización:** Integración completada con generación de imágenes base64
