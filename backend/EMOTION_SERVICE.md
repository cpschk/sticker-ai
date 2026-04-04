# Servicio de Detección de Emociones

## Descripción

El servicio `EmotionDetectorService` detecta la emoción dominante en un texto usando reglas simples basadas en keywords y patrones.

## Emociones Soportadas

| Emoción | Keywords Principales | Ejemplos |
|---------|----------------------|----------|
| **risa** 😄 | jajaja, haha, lol, jeje | "jajaja me muero de risa!!!" |
| **sorpresa** 😲 | no puede ser, increíble, wow | "no puede ser! increíble!" |
| **sarcasmo** 😏 | te dije, claro, seguro, como si | "claro que sí, muy verdad" |
| **enojo** 😠 | furioso, rabia, odio, basta | "¡¡¡estoy furioso!!!" |
| **tristeza** 😢 | triste, llorar, dolor, adiós | "Me siento muy triste..." |
| **confusión** 😕 | confundido, no entiendo, ¿qué? | "No entiendo... ¿qué pasa??" |

## Uso en FastAPI

### 1. Endpoint REST

```python
from fastapi import FastAPI
from app.models import EmotionDetectionRequest, EmotionDetectionResponse
from app.services.emotion_detector import EmotionDetectorService

app = FastAPI()

@app.post("/api/v1/detect-emotion")
async def detect_emotion(request: EmotionDetectionRequest) -> EmotionDetectionResponse:
    result = EmotionDetectorService.detect(request.text)
    return EmotionDetectionResponse(**result)
```

### 2. Función Directa (en rutas o servicios)

```python
from app.services.emotion_detector import detect_emotion

# Uso simple
result = detect_emotion("jajaja esto es increíble!")
print(result["emotion"])      # "risa"
print(result["intensity"])    # 0.85
print(result["intensity_level"])  # "alta"
```

## Estructura de Respuesta

```json
{
  "emotion": "risa",
  "intensity": 0.85,
  "intensity_level": "alta",
  "confidence": 0.75,
  "all_scores": {
    "risa": 0.75,
    "sorpresa": 0.5,
    "enojo": 0.0,
    "sarcasmo": 0.0,
    "tristeza": 0.0,
    "confusión": 0.0
  }
}
```

### Campos:

- **emotion**: Emoción detectada (string o None)
- **intensity**: Intensidad (0.0 a 1.0)
  - **0.0 - 0.39**: Baja
  - **0.40 - 0.69**: Media
  - **0.70 - 1.0**: Alta
- **intensity_level**: Nivel cualitativo ("baja", "media", "alta")
- **confidence**: Confianza en la detección (0.0 a 1.0)
- **all_scores**: Puntuaciones de todas las emociones
- **details**: Información adicional (si hay error)

## Cálculo de Intensidad

La intensidad se calcula considerando:

1. **Base**: Score de confianza del keyword match
2. **Énfasis**: Mayúsculas, signos de exclamación y interrogación
3. **Repeticiones**: Caracteres repetidos (ej: "jajajaja", "!!!")

```python
intensity = base_score + (emphasis * 0.2) + (repetitions * 0.15)
```

### Ejemplo:

```python
# Texto sin énfasis
"jajaja"
# intensity = 0.75 + 0 + 0.15 = 0.90 → ALTA

# Texto con énfasis
"¡¡¡jajajaja!!!"
# intensity = 0.75 + 0.30 + 0.15 = 1.0 → ALTA (capped)

# Texto neutral
"me rio"
# intensity = 0.5 + 0 + 0 = 0.50 → MEDIA
```

## Ejemplos Prácticos

### CURL

```bash
# Risa
curl -X POST http://localhost:8000/api/v1/detect-emotion \
  -H "Content-Type: application/json" \
  -d '{"text": "jajaja esto es hilariante!!!"}'

# Sorpresa
curl -X POST http://localhost:8000/api/v1/detect-emotion \
  -H "Content-Type: application/json" \
  -d '{"text": "¡No puede ser! ¡Increíble!"}'

# Enojo
curl -X POST http://localhost:8000/api/v1/detect-emotion \
  -H "Content-Type: application/json" \
  -d '{"text": "¡¡¡Estoy furioso!!! ¡Qué rabia!"}'

# Tristeza
curl -X POST http://localhost:8000/api/v1/detect-emotion \
  -H "Content-Type: application/json" \
  -d '{"text": "Me siento muy triste... mi corazón duele"}'
```

### Python

```python
from app.services.emotion_detector import EmotionDetectorService

# Detectar emoción
result = EmotionDetectorService.detect("jajaja no puede ser!")

print(f"Emoción: {result['emotion']}")
print(f"Intensidad: {result['intensity']}/1.0 ({result['intensity_level']})")
print(f"Confianza: {result['confidence']}/1.0")

# Acceder a todas las puntuaciones
for emotion, score in result['all_scores'].items():
    print(f"  {emotion}: {score}")
```

## Personalización

### Agregar nuevos keywords

```python
from app.services.emotion_detector import EmotionDetectorService, Emotion

# Extender EMOTION_KEYWORDS
EmotionDetectorService.EMOTION_KEYWORDS[Emotion.RISA]["keywords"].extend([
    "divertido", "cómico", "jajajajaja"
])
```

### Ajustar pesos

```python
# Cambiar peso de una emoción
EmotionDetectorService.EMOTION_KEYWORDS[Emotion.ENOJO]["weight"] = 1.2
```

## Limitaciones Actuales

⚠️ El servicio usa reglas simples basadas en keywords:

- ❌ No entiende contexto complejo
- ❌ Dificultad con ironía subtil
- ❌ Sesgo hacia idiomas con muchos ejemplos (español)
- ❌ No diferencia intensidad de emoticons

## Mejoras Futuras

📈 Versión mejorada con:

- NLP avanzado (spaCy, NLTK)
- Modelos transformers (BERT, DistilBERT)
- Análisis de contexto
- Soporte multi-idioma
- Machine Learning entrenado

## Testing

```bash
# Ejecutar pruebas
python test_emotions.py

# Ejecutar tests unitarios (si existen)
pytest tests/
```

## API Rápida

```python
from app.services.emotion_detector import detect_emotion

# Función de conveniencia
result = detect_emotion("¡Qué sorpresa!")
# result = {
#   'emotion': 'sorpresa',
#   'intensity': 0.65,
#   'intensity_level': 'media',
#   'confidence': 0.5,
#   ...
# }
```
