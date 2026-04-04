# 🚀 Quick Start - Sticker AI Backend

Guía rápida para empezar con el backend de Sticker AI.

## ⚡ En 5 minutos

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

Verifica que Pillow se instale correctamente:
```bash
pip install pillow==10.0.0
```

### 2. Ejecutar tests rápidos

```bash
python quick_test.py
```

Esto validará que todos los servicios funcionen:
- ✅ Detector de emociones
- ✅ Poses de avatar
- ✅ Selección de poses
- ✅ Manipulación de imágenes
- ✅ Integración completa

### 3. Ejecutar la API

```bash
python main.py
```

O con uvicorn:
```bash
uvicorn main:app --reload --port 8000
```

Accede a:
- 🎯 API: http://localhost:8000
- 📚 Documentación: http://localhost:8000/docs

## 📝 Ejemplos de Uso

### Ejemplo 1: Detectar emoción

```bash
curl -X POST http://localhost:8000/api/v1/detect-emotion \
  -H "Content-Type: application/json" \
  -d '{"text": "¡Esto es increíble!!!"}'
```

Respuesta:
```json
{
  "emotion": "risa",
  "intensity": 0.85,
  "intensity_level": "high",
  "confidence": 0.92
}
```

### Ejemplo 2: Sugerir sticker (con avatar pose)

```bash
curl -X POST http://localhost:8000/api/v1/suggest-sticker \
  -H "Content-Type: application/json" \
  -d '{"text": "¡No puedo creer esto!"}'
```

Respuesta:
```json
{
  "original_text": "¡No puedo creer esto!",
  "detected_emotion": "sorpresa",
  "avatar_pose": {
    "id": 7,
    "emotion": "sorpresa",
    "intensity": 0.7,
    "image_path": "/avatars/poses/sorpresa_alta.png",
    "name": "Sorpresa Alta"
  },
  "suggestions": [ ... ]
}
```

### Ejemplo 3: Agregar globo de diálogo a imagen

```python
from app.services.image_manipulation import add_speech_bubble, SpeechBubbleStyle

# Simple
img = add_speech_bubble("avatar.png", "¡Hola mundo!")
img.save("result.png")

# Con estilo
style = SpeechBubbleStyle(
    bubble_color=(255, 200, 100),      # Naranja
    border_color=(200, 100, 0)
)

img = add_speech_bubble(
    "avatar.png",
    "Texto personalizado",
    output_path="result.png",
    style=style,
    bubble_position="top"
)
```

## 🧪 Scripts de Demostración

### Test de Emociones
```bash
python test_emotions.py
```

### Demo de Poses de Avatar
```bash
python demo_avatar_poses.py
python demo_avatar_selection.py
```

### Demo de Globos de Diálogo
```bash
python demo_speech_bubbles.py
python example_speech_bubbles.py
```

### Test Integrado
```bash
python test_integrated_analysis.py
python test_suggest_sticker_integration.py
```

## 📦 Servicios Disponibles

### 1. EmotionDetectorService
Detecta emociones en texto.

```python
from app.services.emotion_detector import detect_emotion

result = detect_emotion("¡Estoy muy feliz!")
# {'emotion': 'risa', 'intensity': 0.8, ...}
```

**Emociones soportadas:** risa, sorpresa, enojo, tristeza, confusión, sarcasmo

### 2. AvatarPoseSelectionService
Selecciona la mejor pose de avatar según emoción.

```python
from app.services.avatar_service import AvatarPoseSelectionService
from app.models.avatar_pose import AVATAR_POSES

service = AvatarPoseSelectionService()
pose = service.select_best_pose("risa", AVATAR_POSES)
# AvatarPose(id=1, emotion='risa', intensity=0.6, ...)
```

**Métodos disponibles:**
- `select_best_pose()` - Selección simple
- `select_best_pose_weighted()` - Ponderada (intensidad 0.4-0.7)
- `select_pose_by_intensity_range()` - Por rango de intensidad
- `select_pose_sequence()` - Secuencia para animación

### 3. ImageWithSpeechBubble
Agrega globos de diálogo a imágenes.

```python
from app.services.image_manipulation import add_speech_bubble, SpeechBubbleStyle

# Uso simple
add_speech_bubble("input.png", "Texto")

# Uso avanzado
style = SpeechBubbleStyle(
    bubble_color=(255, 255, 100),
    text_color=(0, 0, 0),
    border_color=(200, 100, 0),
    border_width=3,
    padding=20,
    corner_radius=15
)

add_speech_bubble(
    "input.png",
    "Texto",
    output_path="output.png",
    style=style,
    bubble_position="top",
    font_size=20
)
```

**Características:**
- ✅ Envoltura de texto automática
- ✅ Posiciones: top, bottom, left, right
- ✅ Estilos personalizables
- ✅ Soporte para fuentes del sistema

## 📚 Documentación Completa

- [README.md](README.md) - Descripción general
- [EMOTION_SERVICE.md](EMOTION_SERVICE.md) - Detector de emociones
- [AVATAR_POSES.md](AVATAR_POSES.md) - Estructura de poses
- [AVATAR_SELECTION.md](AVATAR_SELECTION.md) - Selección de poses
- [IMAGE_MANIPULATION.md](IMAGE_MANIPULATION.md) - Globos de diálogo
- [EXAMPLES.md](EXAMPLES.md) - Ejemplos de uso
- [API_ENDPOINTS.md](API_ENDPOINTS.md) - Referencia de endpoints

## 🐛 Solución de Problemas

### La API no inicia
```bash
# Verifica la instalación
pip check

# Reinstala dependencias
pip install -r requirements.txt --force-reinstall
```

### Error con Pillow
```bash
# Reinstala Pillow específicamente
pip install pillow==10.0.0 --force-reinstall
```

### Tests fallan
```bash
# Ejecuta tests individuales para más detalles
python test_emotions.py
python test_integrated_analysis.py
```

## 🎯 Próximos Pasos

1. **Crear imágenes de avatar reales**
   - Reemplaza las rutas en `app/models/avatar_pose.py`
   - Coloca imágenes en `/avatars/poses/`

2. **Integrar con mobile**
   - Los endpoints están listos en http://localhost:8000
   - Usa `/api/v1/suggest-sticker` para obtener poses y emociones

3. **Mejorar detector de emociones**
   - Implementar modelos ML (transformers, BERT en español)
   - Agregar más palabras clave y patrones

4. **Persistencia de datos**
   - Agregar base de datos (PostgreSQL, MongoDB)
   - Guardar historial de emociones detectadas

## 💡 Tips

- El detector de emociones usa análisis de palabras clave y patrones
- Las poses de avatar tienen intensidad (0.0-1.0) que se mapea a expresión
- La manipulación de imágenes usa Pillow para máximo rendimiento
- Todos los servicios tienen métodos estáticos y de instancia

## 🔗 Enlaces Útiles

- FastAPI docs: https://fastapi.tiangolo.com/
- Pillow docs: https://pillow.readthedocs.io/
- Pydantic docs: https://docs.pydantic.dev/

---

¿Tienes preguntas? Revisa la documentación completa en los archivos `.md` del proyecto.
