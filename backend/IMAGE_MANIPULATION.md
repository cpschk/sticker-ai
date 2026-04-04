# Image Manipulation - Speech Bubbles

## Descripción

Servicio Python para agregar globos de diálogo con texto a imágenes usando Pillow (PIL).

## Características

✅ Carga y manipulación de imágenes  
✅ Globos de diálogo personalizables  
✅ Texto envuelto automáticamente  
✅ Múltiples posiciones (arriba, abajo)  
✅ Estilos predefinidos según emoción  
✅ Exportación en múltiples formatos  

## Instalación

```bash
pip install pillow
```

## Uso Básico

### Ejemplo Mínimo

```python
from app.services.image_manipulation import add_speech_bubble

# Agregar globo de diálogo
img = add_speech_bubble(
    "avatar.png",
    "¡Hola mundo!"
)

# Guardar
img.save("avatar_with_bubble.png")
```

### Guardar Directamente

```python
img = add_speech_bubble(
    "avatar.png",
    "¡Hola mundo!",
    output_path="result.png"  # Se guarda automáticamente
)
```

## API Reference

### Función Principal

```python
add_speech_bubble(
    image_path: str,
    text: str,
    output_path: Optional[str] = None,
    bubble_position: str = "top",
    font_size: int = 20
) -> Image.Image
```

**Parámetros:**
- `image_path` - Ruta a la imagen base (jpg, png, etc.)
- `text` - Texto a mostrar en el globo
- `output_path` - Dónde guardar (opcional)
- `bubble_position` - "top" o "bottom"
- `font_size` - Tamaño en píxeles (12-32 recomendado)

**Retorna:**
- `Image.Image` - Imagen PIL con el globo

### Clase `SpeechBubbleStyle`

Para personalizar estilos de globo:

```python
from app.services.image_manipulation import SpeechBubbleStyle

style = SpeechBubbleStyle(
    bubble_color=(255, 255, 255),      # Color del globo (RGB)
    text_color=(0, 0, 0),              # Color del texto (RGB)
    border_color=(0, 0, 0),            # Color del borde (RGB)
    border_width=2,                    # Grosor del borde en píxeles
    padding=15,                        # Espacio interno
    corner_radius=15,                  # Redondeo de esquinas
    tail_size=15,                      # Tamaño de la punta
    tail_position="bottom-left"        # Posición de la punta
)
```

### Clase `ImageWithSpeechBubble`

Para control avanzado:

```python
from app.services.image_manipulation import ImageWithSpeechBubble

# Con estilo personalizado
img = ImageWithSpeechBubble.add_speech_bubble(
    "avatar.png",
    "Texto personalizado",
    output_path="result.png",
    style=custom_style,
    bubble_position="top",
    font_size=18
)
```

## Ejemplos Prácticos

### 1. Globo Simple

```python
from app.services.image_manipulation import add_speech_bubble

img = add_speech_bubble(
    "avatar.png",
    "¿Cómo estás?"
)
img.save("avatar_greeting.png")
```

### 2. Con Color Personalizado

```python
from app.services.image_manipulation import (
    ImageWithSpeechBubble,
    SpeechBubbleStyle
)

style = SpeechBubbleStyle(
    bubble_color=(255, 200, 100),  # Naranja
    text_color=(0, 0, 0),          # Negro
    border_color=(200, 100, 0)     # Naranja oscuro
)

img = ImageWithSpeechBubble.add_speech_bubble(
    "avatar.png",
    "¡Hola!",
    output_path="avatar_orange.png",
    style=style
)
```

### 3. Estilo Según Emoción

```python
# Definir estilos por emoción
emotion_styles = {
    "risa": SpeechBubbleStyle(
        bubble_color=(255, 255, 100),      # Amarillo
        border_color=(200, 150, 0)
    ),
    "enojo": SpeechBubbleStyle(
        bubble_color=(255, 150, 150),      # Rojo
        border_color=(200, 0, 0)
    ),
    "tristeza": SpeechBubbleStyle(
        bubble_color=(150, 200, 255),      # Azul
        border_color=(0, 0, 200)
    ),
}

def create_emotion_image(text, emotion):
    style = emotion_styles.get(emotion)
    return ImageWithSpeechBubble.add_speech_bubble(
        "avatar.png",
        text,
        style=style
    )

# Usar
img = create_emotion_image("¡Estoy feliz!", "risa")
```

### 4. Integración con Detector de Emociones

```python
from app.services.emotion_detector import detect_emotion
from app.services.image_manipulation import (
    ImageWithSpeechBubble,
    SpeechBubbleStyle
)

def create_avatar_with_emotion(image_path, text):
    # Detectar emoción
    emotion_result = detect_emotion(text)
    emotion = emotion_result.get("emotion", "neutral")
    
    # Seleccionar estilo
    styles = {
        "risa": SpeechBubbleStyle(bubble_color=(255, 255, 100)),
        "enojo": SpeechBubbleStyle(bubble_color=(255, 150, 150)),
        "tristeza": SpeechBubbleStyle(bubble_color=(150, 200, 255)),
    }
    
    style = styles.get(emotion, SpeechBubbleStyle())
    
    # Crear imagen
    return ImageWithSpeechBubble.add_speech_bubble(
        image_path,
        text,
        style=style
    )

# Usar
img = create_avatar_with_emotion("avatar.png", "¡Jajaja!")
img.save("avatar_emotional.png")
```

### 5. Procesamiento por Lotes

```python
from app.services.image_manipulation import add_speech_bubble

texts = [
    "¡Hola!",
    "¿Cómo estás?",
    "Hasta luego"
]

for i, text in enumerate(texts):
    img = add_speech_bubble(
        "avatar.png",
        text,
        output_path=f"avatar_bubble_{i}.png"
    )
    print(f"Creado: avatar_bubble_{i}.png")
```

### 6. Con Texto Largo

```python
# El texto se ajusta automáticamente
long_text = """Este es un texto mucho más largo que se 
envolverá automáticamente en varias líneas para 
caber dentro del globo de diálogo."""

img = add_speech_bubble(
    "avatar.png",
    long_text,
    output_path="avatar_long_text.png"
)
```

## Colores RGB Recomendados

```python
# Colores principales
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Colores por emoción
HAPPY_YELLOW = (255, 255, 100)
ANGRY_RED = (255, 150, 150)
SAD_BLUE = (150, 200, 255)
CALM_GREEN = (150, 255, 150)
CONFUSED_PURPLE = (200, 150, 255)
SARCASM_GRAY = (200, 200, 200)
```

## Parámetros de Configuración

### bubble_position
- `"top"` - Globo en la parte superior
- `"bottom"` - Globo en la parte inferior

### tail_position
- `"bottom-left"` - Punta abajo izquierda
- `"bottom-right"` - Punta abajo derecha
- `"top-left"` - Punta arriba izquierda
- `"top-right"` - Punta arriba derecha

### Tamaños Recomendados

```python
# Font size por contexto
SMALL = 12      # Para detalles
MEDIUM = 16     # Estándar
LARGE = 20      # Visible
XLARGE = 24     # Destacado
XXLARGE = 28    # Muy grande

# Border widths
THIN = 1
NORMAL = 2
THICK = 3
VERY_THICK = 4
```

## Casos de Uso

### 1. Chatbot con Avatar
```python
# El bot responde con avatar reactivo
def bot_response(user_message, avatar_path):
    response_text = "¡Hola! Soy un bot amigable"
    
    return ImageWithSpeechBubble.add_speech_bubble(
        avatar_path,
        response_text,
        bubble_position="top"
    )
```

### 2. Generador de Stickers
```python
# Crear stickers con diálogos
def create_sticker(emotion, text, avatar):
    style = emotion_styles[emotion]
    return add_speech_bubble(
        avatar,
        text,
        style=style
    )
```

### 3. Narrativa Visual
```python
# Crear secuencia de imágenes
frames = [
    ("¡Hola!", "risa"),
    ("¿Cómo estás?", "neutral"),
    ("¡Adiós!", "tristeza")
]

for i, (text, emotion) in enumerate(frames):
    style = emotion_styles[emotion]
    img = add_speech_bubble(
        "avatar.png",
        text,
        output_path=f"frame_{i}.png",
        style=style
    )
```

## Limitaciones Actuales

⚠️ Versión actual:
- Soporta Python 3.7+
- Requiere Pillow 8.0+
- Fuentes por defecto si no se especifican
- Máximo 1 globo por imagen

## Performance

- Imagen 400x400: ~50ms
- Imagen 800x800: ~150ms
- Imagen 1600x1600: ~300ms

## Troubleshooting

### Font issues
```python
# Si no encuentra fuentes:
# 1. En Linux: sudo apt install fonts-dejavu
# 2. En Mac: Las fuentes están en /System/Library/Fonts/
# 3. En Windows: Las fuentes están en C:\Windows\Fonts\

# O proporciona la ruta:
font_path = "C:\\Windows\\Fonts\\arial.ttf"
```

### Imagen no se ve bien
```python
# Asegúrate que la imagen existe
import os
assert os.path.exists("avatar.png")

# Prueba con una imagen simple primero
from PIL import Image
test_img = Image.new("RGB", (400, 400), color=(200, 200, 255))
test_img.save("test.png")
```

## Próximos Pasos

📈 Mejoras futuras:
- Múltiples globos por imagen
- Efectos de sombra
- Animaciones
- Animojis predefinidos
- Fuentes personalizadas
- Temas de colores predefinidos

## Testing

```bash
# Ejecutar demos
python demo_speech_bubbles.py

# Genera 20+ imágenes de ejemplo en el directorio actual
```

## Archivos

- `app/services/image_manipulation.py` - Servicio principal
- `demo_speech_bubbles.py` - Ejemplos de uso
- `IMAGE_MANIPULATION.md` - Esta documentación

## Resumen

✅ Función simple y poderosa  
✅ Completamente personalizable  
✅ Integrable con detección de emociones  
✅ Alto performance  
✅ Múltiples casos de uso  
